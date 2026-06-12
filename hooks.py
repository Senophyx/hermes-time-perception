"""
Hermes pre_llm_call hook — time-awareness injection.

Hermes triggers pre_llm_call before each LLM call in a turn.
The hook returns {"context": "..."} which is appended to the end of the current turn's user message,
visible to the LLM but does not pollute the system prompt (protecting prompt cache prefix),
and is not persisted to the session database.
"""

from time_perception.time_context import format_current_time


def on_pre_llm_call(*, session_id: str = "", user_message: str = "",
                    conversation_history=None, is_first_turn: bool = False,
                    model: str = "", platform: str = "", sender_id: str = "",
                    **kwargs) -> dict:
    """Return current time tag for each turn (ephemeral, appended to the end of user message)."""
    return {"context": format_current_time()}


def register_hooks(ctx) -> None:
    ctx.register_hook("pre_llm_call", on_pre_llm_call)
