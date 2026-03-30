"""Read and write individual functions in .c source files."""

import re
from pathlib import Path
from typing import Optional


def extract_function_asm(asm_path: Path, func_name: str) -> Optional[str]:
    """Extract a single function's assembly from a .s file."""
    if not asm_path.exists():
        return None
    text = asm_path.read_text()
    pattern = rf'(\.fn {re.escape(func_name)},.*?\n.*?\.endfn {re.escape(func_name)})'
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1) if match else None


def extract_function_c(source_path: Path, func_name: str) -> Optional[str]:
    """Extract a single C function from a source file by matching its name."""
    if not source_path.exists():
        return None
    text = source_path.read_text()

    # Find the function signature containing func_name
    # Pattern: type func_name(params) { ... }
    # Use a brace-counting approach starting from the function name
    idx = text.find(func_name)
    if idx == -1:
        return None

    # Walk backwards to find the return type (start of line)
    line_start = text.rfind("\n", 0, idx)
    if line_start == -1:
        line_start = 0
    else:
        line_start += 1

    # Walk forward to find the opening brace
    brace_start = text.find("{", idx)
    if brace_start == -1:
        return None

    # Count braces to find the end
    depth = 0
    for i in range(brace_start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[line_start:i + 1]
    return None


def has_placeholder(source_path: Path, func_name: str) -> bool:
    """Check if a function has a placeholder comment (/// #func_name)."""
    text = source_path.read_text()
    pattern = rf'^/// #{re.escape(func_name)}$'
    return bool(re.search(pattern, text, re.MULTILINE))


def replace_placeholder(source_path: Path, func_name: str, c_code: str) -> bool:
    """Replace a /// #func_name placeholder with actual C code."""
    text = source_path.read_text()
    pattern = rf'^/// #{re.escape(func_name)}$(?:\r?\n)?'
    new_text, count = re.subn(pattern, c_code + "\n", text, flags=re.MULTILINE)
    if count == 0:
        return False
    source_path.write_text(new_text)
    return True


def replace_function(source_path: Path, func_name: str, new_code: str) -> bool:
    """Replace an existing function in a source file with new code."""
    old_code = extract_function_c(source_path, func_name)
    if old_code is None:
        return False
    text = source_path.read_text()
    new_text = text.replace(old_code, new_code, 1)
    if new_text == text:
        return False
    source_path.write_text(new_text)
    return True


def get_nearby_matched_c(source_path: Path, report_funcs: list,
                         exclude: str, max_count: int = 2,
                         max_size: int = 200) -> list[tuple[str, str]]:
    """Get small matched functions from the same file for style reference."""
    results = []
    matched = [f for f in report_funcs
               if f.get("fuzzy_match_percent") == 100.0
               and int(f.get("size", "0")) <= max_size
               and f["name"] != exclude]
    matched.sort(key=lambda f: int(f["size"]))

    for f in matched[:max_count]:
        code = extract_function_c(source_path, f["name"])
        if code and len(code) < 500:
            results.append((f["name"], code))
    return results
