"""Run m2c to decompile assembly functions into initial C code."""

import subprocess
from pathlib import Path
from typing import Optional

from .config import Config


def build_context(config: Config, source_path: str) -> Optional[Path]:
    """Build the .ctx file for a source file via ninja."""
    ctx_path = config.melee_root / "build" / "GALE01" / source_path.replace(".c", ".ctx")
    result = subprocess.run(
        ["ninja", str(ctx_path)],
        capture_output=True, text=True,
        cwd=str(config.melee_root),
        timeout=60,
    )
    if result.returncode != 0:
        return None
    return ctx_path


def run_m2c(config: Config, func_name: str, asm_path: str,
            ctx_path: Optional[Path] = None) -> Optional[str]:
    """Run m2c to decompile a function from assembly.

    Returns the decompiled C code, or None on failure.
    """
    cmd = ["m2c", "--knr", "--pointer", "left", "-t", "ppc-mwcc-c"]
    if ctx_path and ctx_path.exists():
        cmd.extend(["--context", str(ctx_path)])
    cmd.extend(["-f", func_name, str(asm_path)])

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=30,
        cwd=str(config.melee_root),
    )
    if result.returncode != 0:
        return None

    output = result.stdout.strip()
    if not output or "M2C_ERROR" in output:
        return None
    return output


def decompile_function(config: Config, func_name: str,
                       source_path: str, asm_path: str) -> Optional[str]:
    """Full m2c pipeline: build context, run m2c, return C code."""
    ctx_path = build_context(config, source_path)
    asm_full = config.melee_root / asm_path if not Path(asm_path).is_absolute() else Path(asm_path)
    if not asm_full.exists():
        # Try the build asm path
        unit_rel = source_path.removeprefix("src/").removesuffix(".c")
        asm_full = config.asm_root / f"{unit_rel}.s"
    if not asm_full.exists():
        return None
    return run_m2c(config, func_name, str(asm_full), ctx_path)
