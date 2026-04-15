"""LLM client for ipub. Supports Anthropic Claude API and stdin fallback."""

import os
import sys

from ipub.config import load_config


def call_llm(prompt: str) -> str:
    """Call LLM with the given prompt. Returns response text."""
    config = load_config()
    provider = config["llm"]["provider"]
    model = config["llm"]["model"]

    if provider == "anthropic":
        return _call_anthropic(prompt, model)
    elif provider == "stdin":
        return _call_stdin(prompt)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def _call_anthropic(prompt: str, model: str) -> str:
    """Call Anthropic Claude API."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. Either:\n"
            "  1. export ANTHROPIC_API_KEY=your-key\n"
            "  2. Set llm.provider to 'stdin' in ipub.yaml for manual mode"
        )

    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            "anthropic package not installed. Run:\n"
            "  pip install 'ipub[llm]'"
        )

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _call_stdin(prompt: str) -> str:
    """Fallback: print prompt and read response from stdin."""
    print("=" * 60)
    print("LLM PROMPT (copy to your preferred LLM):")
    print("=" * 60)
    print(prompt)
    print("=" * 60)
    print("Paste LLM response below (end with Ctrl+D or empty line):")
    print()

    lines = []
    try:
        for line in sys.stdin:
            if line.strip() == "" and lines:
                break
            lines.append(line)
    except EOFError:
        pass

    return "".join(lines)
