"""
Hermes Time Perception plugin registration entry point.

Hermes automatically discovers ~/.hermes/plugins/hermes-time-perception/ and calls register(ctx).
This extension does one thing: before each LLM turn, append the current time via the pre_llm_call
hook to the end of the user message (ephemeral, does not pollute system prompt / prompt cache).
"""

import importlib.util
import sys
from pathlib import Path

# Plugin root in sys.path so the local `time_perception/` package is importable.
# Flat layout (Hermes 0.14+): __init__.py lives at <plugin-root>/__init__.py.
_repo_root = Path(__file__).resolve().parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))


def _load_register_hooks():
    hooks_path = _repo_root / "hooks.py"
    module_name = f"{__name__}._hooks"
    spec = importlib.util.spec_from_file_location(module_name, hooks_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load hooks module from {hooks_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.register_hooks


register_hooks = _load_register_hooks()


def register(ctx) -> None:
    register_hooks(ctx)
