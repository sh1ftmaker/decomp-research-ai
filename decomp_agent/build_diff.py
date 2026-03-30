"""Compile a translation unit and diff against target."""

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .config import Config


@dataclass
class DiffResult:
    compiled_ok: bool
    compile_error: Optional[str] = None
    func_match_pct: Optional[float] = None
    func_size_target: int = 0
    func_size_compiled: int = 0
    diff_counts: dict = field(default_factory=dict)  # e.g. {"DIFF_ARG_MISMATCH": 47}
    total_instructions: int = 0
    duration_secs: float = 0.0

    @property
    def size_matches(self) -> bool:
        return self.func_size_target == self.func_size_compiled and self.func_size_target > 0

    @property
    def is_matched(self) -> bool:
        return self.func_match_pct is not None and self.func_match_pct == 100.0

    @property
    def is_regalloc_only(self) -> bool:
        if not self.size_matches:
            return False
        logic_diffs = (self.diff_counts.get("DIFF_INSERT", 0) +
                       self.diff_counts.get("DIFF_DELETE", 0) +
                       self.diff_counts.get("DIFF_REPLACE", 0))
        arg_diffs = self.diff_counts.get("DIFF_ARG_MISMATCH", 0)
        return logic_diffs <= 4 and arg_diffs > 0

    @property
    def summary(self) -> str:
        if not self.compiled_ok:
            return f"COMPILE_ERROR: {self.compile_error[:100] if self.compile_error else 'unknown'}"
        if self.is_matched:
            return "MATCHED"
        parts = [f"{self.func_match_pct:.1f}%"]
        parts.append(f"size:{self.func_size_compiled}/{self.func_size_target}")
        for kind, count in sorted(self.diff_counts.items()):
            if count > 0 and kind != "DIFF_NONE":
                parts.append(f"{kind.removeprefix('DIFF_')}:{count}")
        return " ".join(parts)


def build_unit(config: Config, source_path: str, unit_name: str = "") -> tuple[bool, str]:
    """Compile a single .o file via ninja. Returns (success, error_msg)."""
    # Use objdiff.json base_path for accurate build target
    if unit_name:
        import json
        with open(config.objdiff_json_path) as f:
            data = json.load(f)
        for u in data["units"]:
            if u["name"] == unit_name:
                obj_path = u["base_path"]  # relative path for ninja
                break
        else:
            obj_path = "build/GALE01/" + source_path.replace(".c", ".o")
    else:
        obj_path = "build/GALE01/" + source_path.replace(".c", ".o")
    result = subprocess.run(
        ["ninja", obj_path],
        capture_output=True, text=True,
        cwd=str(config.melee_root),
        timeout=60,
    )
    if result.returncode != 0:
        return False, result.stderr[-500:] if result.stderr else result.stdout[-500:]
    return True, ""


def diff_function(config: Config, unit_name: str, func_name: str) -> DiffResult:
    """Run objdiff-cli diff for a specific function and parse results."""
    start = time.time()

    out_path = f"/tmp/decomp_agent_diff_{func_name}.json"
    result = subprocess.run(
        ["objdiff-cli", "diff", "-u", unit_name, func_name,
         "-o", out_path, "--format", "json-pretty"],
        capture_output=True, text=True,
        cwd=str(config.melee_root),
        timeout=30,
    )

    if result.returncode != 0:
        return DiffResult(compiled_ok=False,
                          compile_error=result.stderr[-300:],
                          duration_secs=time.time() - start)

    with open(out_path) as f:
        data = json.load(f)

    # Find the function in left (target) and right (compiled) symbols
    target_sym = None
    compiled_sym = None
    for sym in data.get("left", {}).get("symbols", []):
        if sym.get("name") == func_name:
            target_sym = sym
            break
    for sym in data.get("right", {}).get("symbols", []):
        if sym.get("name") == func_name:
            compiled_sym = sym
            break

    if not target_sym:
        return DiffResult(compiled_ok=True, duration_secs=time.time() - start)

    target_size = int(target_sym.get("size", "0"))
    compiled_size = int(compiled_sym.get("size", "0")) if compiled_sym else 0
    match_pct = target_sym.get("match_percent")

    # Count diff kinds from instructions
    diff_counts = {}
    total_instr = 0
    for inst in target_sym.get("instructions", []):
        total_instr += 1
        dk = inst.get("diff_kind", "DIFF_NONE")
        diff_counts[dk] = diff_counts.get(dk, 0) + 1

    return DiffResult(
        compiled_ok=True,
        func_match_pct=match_pct,
        func_size_target=target_size,
        func_size_compiled=compiled_size,
        diff_counts=diff_counts,
        total_instructions=total_instr,
        duration_secs=time.time() - start,
    )


def build_and_diff(config: Config, source_path: str, unit_name: str,
                   func_name: str) -> DiffResult:
    """Full compile + diff pipeline for one function."""
    ok, err = build_unit(config, source_path, unit_name)
    if not ok:
        return DiffResult(compiled_ok=False, compile_error=err)
    return diff_function(config, unit_name, func_name)
