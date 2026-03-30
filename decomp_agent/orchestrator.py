"""Main orchestrator for the automated decompilation pipeline."""

import argparse
import json
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .config import Config
from .state_db import StateDB, FunctionState, Attempt, TERMINAL_STATES
from .target_selector import populate_db, load_report
from .build_diff import build_and_diff, DiffResult
from .source_editor import (extract_function_asm, extract_function_c,
                            has_placeholder, replace_placeholder, replace_function,
                            get_nearby_matched_c)
from .m2c_runner import decompile_function
from .permuter_runner import permute_function
from .ai_fixer import fix_logic, fix_regalloc, fix_syntax


def classify(diff: DiffResult) -> str:
    """Classify a diff result into a state."""
    if not diff.compiled_ok:
        return "COMPILE_ERROR"
    if diff.is_matched:
        return "MATCHED"
    if diff.is_regalloc_only:
        return "REGALLOC_ONLY"
    if not diff.size_matches:
        return "SIZE_MISMATCH"
    return "SIZE_MISMATCH"  # has logic diffs even though size matches


def process_function(config: Config, db: StateDB, fs: FunctionState,
                     dry_run: bool = False) -> str:
    """Process a single function through the state machine. Returns final state."""
    func = fs.func_name
    unit = fs.unit_name
    src = fs.source_path
    asm = fs.asm_path

    print(f"  [{func}] state={fs.state} match={fs.current_match_pct}% size={fs.size_bytes}b")

    # Step 1: If function has only a placeholder, try m2c first
    src_path = config.melee_root / src
    if has_placeholder(src_path, func):
        if dry_run:
            print(f"    → Would run m2c to decompile {func}")
            return "DECOMPILING"

        db.update_state(func, "DECOMPILING")
        c_code = decompile_function(config, func, src, asm)
        if c_code:
            replace_placeholder(src_path, func, c_code)
            print(f"    → m2c generated {len(c_code)} chars")
        else:
            print(f"    → m2c failed, skipping")
            db.update_state(func, "SKIPPED", last_error="m2c_failed")
            return "SKIPPED"

    # Step 2: Build and diff
    if dry_run:
        print(f"    → Would build and diff {unit}/{func}")
        return "BUILDING"

    db.update_state(func, "BUILDING")
    diff = build_and_diff(config, src, unit, func)
    category = classify(diff)
    match_pct = diff.func_match_pct

    db.update_state(func, category, current_match_pct=match_pct)
    db.increment(func, "attempt_count")
    db.log_attempt(Attempt(
        func_name=func, state=category, match_pct=match_pct,
        diff_summary=diff.summary, ai_model=None,
        ai_prompt_tokens=None, ai_response_tokens=None,
        duration_secs=diff.duration_secs,
    ))

    print(f"    → {diff.summary}")

    if category == "MATCHED":
        return "MATCHED"

    if category == "COMPILE_ERROR":
        return _handle_compile_error(config, db, func, unit, src, diff, dry_run)

    if category == "REGALLOC_ONLY":
        return _handle_regalloc(config, db, func, unit, src, diff, dry_run)

    if category == "SIZE_MISMATCH":
        return _handle_size_mismatch(config, db, func, unit, src, asm, diff, dry_run)

    return category


def _handle_compile_error(config, db, func, unit, src, diff, dry_run):
    """Handle compilation errors with AI syntax fix."""
    fs = db.get_state(func)
    if fs.attempt_count >= config.max_syntax_fix_attempts:
        db.update_state(func, "SKIPPED", last_error="max_syntax_attempts")
        return "SKIPPED"

    if dry_run:
        print(f"    → Would call AI for syntax fix")
        return "AI_SYNTAX_FIX"

    src_path = config.melee_root / src
    current_c = extract_function_c(src_path, func) or ""
    result = fix_syntax(config, current_c, diff.compile_error or "")

    if result.success and result.c_code:
        replace_function(src_path, func, result.c_code)
        db.log_attempt(Attempt(
            func_name=func, state="AI_SYNTAX_FIX", match_pct=None,
            diff_summary="syntax_fix", ai_model=result.model,
            ai_prompt_tokens=result.prompt_tokens,
            ai_response_tokens=result.response_tokens, duration_secs=0,
        ))
        # Recurse to rebuild
        new_fs = db.get_state(func)
        return process_function(config, db, new_fs, dry_run)

    db.update_state(func, "SKIPPED", last_error="ai_syntax_fix_failed")
    return "SKIPPED"


def _handle_regalloc(config, db, func, unit, src, diff, dry_run):
    """Handle register allocation issues: permuter first, then AI."""
    if dry_run:
        print(f"    → Would run permuter for {func}")
        return "PERMUTER"

    # Try permuter
    db.update_state(func, "PERMUTER")
    print(f"    → Running permuter (timeout={config.permuter_timeout_secs}s)...")
    perm_result = permute_function(config, func, unit, src)
    db.update_state(func, "PERMUTER",
                    permuter_best_score=perm_result.best_score)

    if perm_result.matched and perm_result.best_source:
        # Apply the matched source
        src_path = config.melee_root / src
        # Extract just the function from permuter output
        replace_function(src_path, func, perm_result.best_source)
        # Verify
        new_diff = build_and_diff(config, src, unit, func)
        if new_diff.is_matched:
            db.update_state(func, "MATCHED", current_match_pct=100.0)
            print(f"    → MATCHED via permuter!")
            return "MATCHED"

    # Permuter didn't solve it, try AI regalloc fix
    fs = db.get_state(func)
    if fs.regalloc_fix_attempts >= config.max_regalloc_fix_attempts:
        db.update_state(func, "SKIPPED", last_error="max_regalloc_attempts")
        return "SKIPPED"

    src_path = config.melee_root / src
    current_c = extract_function_c(src_path, func) or ""
    result = fix_regalloc(config, current_c, diff.summary)

    if result.success and result.c_code:
        replace_function(src_path, func, result.c_code)
        db.increment(func, "regalloc_fix_attempts")
        db.log_attempt(Attempt(
            func_name=func, state="AI_REGALLOC_FIX", match_pct=None,
            diff_summary="regalloc_fix", ai_model=result.model,
            ai_prompt_tokens=result.prompt_tokens,
            ai_response_tokens=result.response_tokens, duration_secs=0,
        ))
        # Rebuild and check
        new_diff = build_and_diff(config, src, unit, func)
        if new_diff.is_matched:
            db.update_state(func, "MATCHED", current_match_pct=100.0)
            return "MATCHED"
        db.update_state(func, "SKIPPED",
                        current_match_pct=new_diff.func_match_pct,
                        last_error="regalloc_not_solved")
        return "SKIPPED"

    db.update_state(func, "SKIPPED", last_error="ai_regalloc_failed")
    return "SKIPPED"


def _handle_size_mismatch(config, db, func, unit, src, asm, diff, dry_run):
    """Handle logic/size mismatch issues with AI."""
    fs = db.get_state(func)
    if fs.logic_fix_attempts >= config.max_logic_fix_attempts:
        db.update_state(func, "SKIPPED", last_error="max_logic_attempts")
        return "SKIPPED"

    # Check token budget
    if db.get_total_tokens(func) >= config.token_budget_per_func:
        db.update_state(func, "SKIPPED", last_error="token_budget_exceeded")
        return "SKIPPED"

    if dry_run:
        print(f"    → Would call AI for logic fix")
        return "AI_LOGIC_FIX"

    src_path = config.melee_root / src
    current_c = extract_function_c(src_path, func) or ""
    target_asm = extract_function_asm(Path(config.melee_root / asm), func) or ""

    # Get nearby matched function for style reference
    report = load_report(config)
    nearby_c = ""
    for u in report.get("units", []):
        if u["name"] == unit:
            nearby = get_nearby_matched_c(src_path, u.get("functions", []), func)
            if nearby:
                nearby_c = nearby[0][1]
            break

    # Escalate model based on attempt count
    model = config.cheap_model
    if fs.logic_fix_attempts >= 2:
        model = config.expensive_model

    result = fix_logic(config, current_c, target_asm,
                       diff.func_size_target, diff.func_size_compiled,
                       diff.summary, nearby_c, model=model)

    if result.success and result.c_code:
        replace_function(src_path, func, result.c_code)
        db.increment(func, "logic_fix_attempts")
        db.log_attempt(Attempt(
            func_name=func, state="AI_LOGIC_FIX",
            match_pct=diff.func_match_pct,
            diff_summary=diff.summary, ai_model=result.model,
            ai_prompt_tokens=result.prompt_tokens,
            ai_response_tokens=result.response_tokens, duration_secs=0,
        ))
        # Rebuild and check
        new_diff = build_and_diff(config, src, unit, func)
        new_cat = classify(new_diff)
        db.update_state(func, new_cat, current_match_pct=new_diff.func_match_pct)

        if new_cat == "MATCHED":
            print(f"    → MATCHED via AI logic fix!")
            return "MATCHED"
        if new_cat == "REGALLOC_ONLY":
            return _handle_regalloc(config, db, func, unit, src, new_diff, dry_run)

        # Still mismatched, try again next round
        print(f"    → AI fix: {new_diff.summary}")
        return new_cat

    db.update_state(func, "SKIPPED", last_error="ai_logic_failed")
    return "SKIPPED"


def run(config: Config, limit: int = 0, dry_run: bool = False,
        workers: int = 1):
    """Main entry point. Process functions in parallel by unit."""
    db = StateDB(config.state_db_path)

    # Populate DB with latest report data
    print("Populating database from report.json...")
    count = populate_db(config, db)
    print(f"  {count} functions loaded")

    stats = db.get_stats()
    print(f"  Current stats: {dict(stats)}")
    print()

    processed = 0
    seen = set()

    # Single pass: get all pending, process up to limit
    pending = db.get_pending(batch_size=limit if limit else 9999)
    if not pending:
        print("No pending functions to process.")
        db.close()
        return

    # Group by unit for serialized builds within each unit
    by_unit = {}
    for fs in pending:
        if fs.func_name in seen:
            continue
        seen.add(fs.func_name)
        by_unit.setdefault(fs.unit_name, []).append(fs)

    # Flatten to respect limit
    all_batches = []
    for unit_name, funcs in by_unit.items():
        all_batches.append((unit_name, funcs))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for unit_name, funcs in all_batches:
            remaining = (limit - processed) if limit else len(funcs)
            if remaining <= 0:
                break
            batch = funcs[:remaining]
            futures[executor.submit(
                _process_unit_batch, config, db, unit_name, batch, dry_run
            )] = unit_name

        for future in as_completed(futures):
            unit_name = futures[future]
            try:
                results = future.result()
                processed += len(results)
                for func_name, state in results:
                    status = "✓" if state == "MATCHED" else "✗" if state == "SKIPPED" else "?"
                    print(f"  {status} {func_name} → {state}")
            except Exception as e:
                print(f"  ERROR processing unit {unit_name}: {e}")

    # Final stats
    stats = db.get_stats()
    print(f"\nFinal stats:")
    for state, count in sorted(stats.items()):
        if count > 0:
            print(f"  {state}: {count}")
    db.close()


def _process_unit_batch(config, db, unit_name, funcs, dry_run):
    """Process a batch of functions in one unit sequentially."""
    results = []
    print(f"\n[Unit: {unit_name}]")
    for fs in funcs:
        try:
            final_state = process_function(config, db, fs, dry_run)
            results.append((fs.func_name, final_state))
        except Exception as e:
            print(f"  ERROR {fs.func_name}: {e}")
            db.update_state(fs.func_name, "FAILED", last_error=str(e)[:200])
            results.append((fs.func_name, "FAILED"))
    return results


def main():
    parser = argparse.ArgumentParser(description="Automated decomp agent")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without making changes")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max functions to process (0 = unlimited)")
    parser.add_argument("--workers", type=int, default=1,
                        help="Parallel workers (by unit)")
    parser.add_argument("--permuter-timeout", type=int, default=600,
                        help="Permuter timeout in seconds")
    args = parser.parse_args()

    config = Config()
    config.permuter_timeout_secs = args.permuter_timeout
    run(config, limit=args.limit, dry_run=args.dry_run, workers=args.workers)


if __name__ == "__main__":
    main()
