"""Auto-setup and run decomp-permuter for register allocation fixes."""

import json
import shutil
import subprocess
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .config import Config
from .source_editor import extract_function_c


@dataclass
class PermuterResult:
    best_score: Optional[int]
    best_source: Optional[str]  # C code from best permutation
    iterations: int
    duration_secs: float
    matched: bool  # score == 0


def get_compile_flags(config: Config, unit_name: str) -> dict:
    """Get compiler flags and paths from objdiff.json for a unit."""
    with open(config.objdiff_json_path) as f:
        data = json.load(f)
    for unit in data["units"]:
        if unit["name"] == unit_name:
            return unit.get("scratch", {})
    return {}


def setup_permuter_dir(config: Config, func_name: str, unit_name: str,
                       source_path: str) -> Optional[Path]:
    """Create the permuter directory with compile.sh, base.c, target.o, settings.toml."""
    perm_dir = config.nonmatchings_root / func_name
    perm_dir.mkdir(parents=True, exist_ok=True)

    scratch = get_compile_flags(config, unit_name)
    if not scratch:
        return None

    c_flags = scratch.get("c_flags", "")
    ctx_path_str = scratch.get("ctx_path", "")
    ctx_path = config.melee_root / ctx_path_str if ctx_path_str else None

    # target_path comes from the objdiff unit, not scratch
    with open(config.objdiff_json_path) as f:
        data = json.load(f)
    target_path_str = ""
    for unit in data["units"]:
        if unit["name"] == unit_name:
            target_path_str = unit.get("target_path", "")
            break
    if not target_path_str:
        return None
    target_path = config.melee_root / target_path_str

    # 1. compile.sh
    compile_sh = perm_dir / "compile.sh"
    compile_sh.write_text(f"""#!/bin/bash
cd {config.melee_root}
build/tools/wibo build/tools/sjiswrap.exe build/compilers/GC/1.2.5n/mwcceppc.exe \\
    {c_flags} \\
    -c "$1" -o "$3"
""")
    compile_sh.chmod(0o755)

    # 2. target.o
    if target_path.exists():
        shutil.copy2(target_path, perm_dir / "target.o")
    else:
        return None

    # 3. base.c - use ctx file + function code wrapped in PERM_RANDOMIZE
    src_full = config.melee_root / source_path
    func_code = extract_function_c(src_full, func_name)
    if not func_code:
        return None

    # Read ctx file for type declarations
    ctx_content = ""
    if ctx_path.exists():
        ctx_content = ctx_path.read_text()

    # Build self-contained base.c
    base_c = f"#define NULL ((void*)0)\n{ctx_content}\n\n{func_code}\n"
    (perm_dir / "base.c").write_text(base_c)

    # 4. settings.toml
    (perm_dir / "settings.toml").write_text(
        f'compiler_type = "mwcc"\nfunc_name = "{func_name}"\n'
    )

    return perm_dir


def run_permuter(config: Config, perm_dir: Path) -> PermuterResult:
    """Run the permuter with timeout. Returns the best result."""
    start = time.time()
    permuter_py = config.permuter_root / "permuter.py"

    result = subprocess.run(
        ["python3", str(permuter_py), str(perm_dir),
         f"-j{config.permuter_threads}", "--stop-on-zero", "--best-only"],
        capture_output=True, text=True,
        cwd=str(config.melee_root),
        timeout=config.permuter_timeout_secs,
    )

    duration = time.time() - start
    output = result.stdout + result.stderr

    # Parse best score from output
    best_score = None
    iterations = 0
    score_matches = re.findall(r'score = (\d+)', output)
    if score_matches:
        best_score = min(int(s) for s in score_matches)

    iter_matches = re.findall(r'iteration (\d+)', output)
    if iter_matches:
        iterations = max(int(i) for i in iter_matches)

    # Check for score 0 output directory
    best_source = None
    matched = False
    zero_dirs = sorted(perm_dir.glob("output-0-*"))
    if zero_dirs:
        matched = True
        best_source_path = zero_dirs[0] / "source.c"
        if best_source_path.exists():
            best_source = best_source_path.read_text()
    elif best_score is not None:
        # Get best non-zero output
        output_dirs = sorted(perm_dir.glob("output-*"), key=lambda p: int(p.name.split("-")[1]))
        if output_dirs:
            best_source_path = output_dirs[0] / "source.c"
            if best_source_path.exists():
                best_source = best_source_path.read_text()

    return PermuterResult(
        best_score=best_score,
        best_source=best_source,
        iterations=iterations,
        duration_secs=duration,
        matched=matched,
    )


def permute_function(config: Config, func_name: str, unit_name: str,
                     source_path: str) -> PermuterResult:
    """Full permuter pipeline: setup dir, run permuter, return result."""
    perm_dir = setup_permuter_dir(config, func_name, unit_name, source_path)
    if not perm_dir:
        return PermuterResult(None, None, 0, 0.0, False)
    try:
        return run_permuter(config, perm_dir)
    except subprocess.TimeoutExpired:
        # Still check for results even after timeout
        best_source = None
        output_dirs = sorted(perm_dir.glob("output-*"), key=lambda p: int(p.name.split("-")[1]))
        if output_dirs:
            sp = output_dirs[0] / "source.c"
            if sp.exists():
                best_source = sp.read_text()
        return PermuterResult(None, best_source, 0, config.permuter_timeout_secs, False)
