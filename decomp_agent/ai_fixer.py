"""Minimal AI prompt generation and API calls for decompilation fixes."""

import re
import os
from typing import Optional
from dataclasses import dataclass

from .config import Config
from .prompts import LOGIC_FIX, REGALLOC_FIX, SYNTAX_FIX


@dataclass
class AIResult:
    c_code: Optional[str]
    model: str
    prompt_tokens: int
    response_tokens: int
    success: bool


def _extract_code_block(text: str) -> str:
    """Extract C code from a response, handling markdown code blocks."""
    # Try to find ```c ... ``` block
    match = re.search(r'```c?\n(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # If no code block, assume the whole response is code
    return text.strip()


def _call_anthropic(prompt: str, model: str, max_tokens: int = 2000) -> AIResult:
    """Call the Anthropic API. Returns AIResult."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return AIResult(None, model, 0, 0, False)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text
        c_code = _extract_code_block(text)
        return AIResult(
            c_code=c_code,
            model=model,
            prompt_tokens=response.usage.input_tokens,
            response_tokens=response.usage.output_tokens,
            success=True,
        )
    except Exception as e:
        return AIResult(None, model, 0, 0, False)


def fix_logic(config: Config, current_c: str, target_asm: str,
              target_size: int, compiled_size: int,
              diff_details: str, nearby_c: str = "",
              model: Optional[str] = None) -> AIResult:
    """Ask AI to fix logic/control flow issues."""
    prompt = LOGIC_FIX.format(
        asm=target_asm[:3000],  # cap at 3000 chars
        current_c=current_c,
        target_size=target_size,
        compiled_size=compiled_size,
        delta=compiled_size - target_size,
        diff_details=diff_details[:1000],
        nearby_c=nearby_c[:500] if nearby_c else "(none available)",
    )
    return _call_anthropic(prompt, model or config.cheap_model)


def fix_regalloc(config: Config, current_c: str, diff_details: str,
                 model: Optional[str] = None) -> AIResult:
    """Ask AI to fix register allocation by reordering declarations."""
    prompt = REGALLOC_FIX.format(
        current_c=current_c,
        diff_details=diff_details[:1500],
    )
    return _call_anthropic(prompt, model or config.cheap_model)


def fix_syntax(config: Config, current_c: str, error: str,
               model: Optional[str] = None) -> AIResult:
    """Ask AI to fix compilation errors."""
    prompt = SYNTAX_FIX.format(
        current_c=current_c,
        error=error[:500],
    )
    return _call_anthropic(prompt, model or config.cheap_model)
