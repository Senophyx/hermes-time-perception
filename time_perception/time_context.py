"""
Turn-level time formatting utility.

Design key points:
  - Timezone resolution prioritizes delegating to the Hermes built-in ``hermes_time`` module
    to ensure consistency with the Hermes main program's priority chain:
    HERMES_TIMEZONE > ~/.hermes/config.yaml: timezone > system local timezone.
  - When Hermes cannot be imported (standalone testing scenario), fall back to local
    equivalent implementation.
  - Timezone string is parsed once at module load time and cached (``_tz_str``),
    datetime.now() is re-evaluated on each call.
  - Any exception falls back to ``datetime.now().astimezone()``, ensuring the hook never raises.
"""

import os
from datetime import datetime
from pathlib import Path


def _resolve_tz_from_hermes() -> str:
    """Prioritize delegating to hermes_time._resolve_timezone_name() to maintain consistency with Hermes."""
    try:
        import hermes_time  # type: ignore[import-not-found]
        return (hermes_time._resolve_timezone_name() or "").strip()
    except Exception:
        return ""


def _resolve_tz_local() -> str:
    """Local equivalent implementation when Hermes is unavailable: env > ~/.hermes/config.yaml > ''."""
    tz_env = os.environ.get("HERMES_TIMEZONE", "").strip()
    if tz_env:
        return tz_env
    try:
        import yaml  # PyYAML is a Hermes runtime dependency
        cfg_path = Path(
            os.environ.get("HERMES_HOME", Path.home() / ".hermes")
        ) / "config.yaml"
        if cfg_path.exists():
            loaded = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            tz_cfg = loaded.get("timezone", "")
            if isinstance(tz_cfg, str) and tz_cfg.strip():
                return tz_cfg.strip()
    except Exception:
        pass
    return ""


_tz_str = _resolve_tz_from_hermes() or _resolve_tz_local()


_WEEKDAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def format_current_time() -> str:
    """
    Return a time label string in the format `[Current time: Friday 2026-06-12 16:33 Asia/Jakarta]`.

    Never raises an exception: any timezone resolution failure falls back to local timezone.
    """
    tz_label = ""
    try:
        if _tz_str:
            from zoneinfo import ZoneInfo
            now = datetime.now(ZoneInfo(_tz_str))
            tz_label = _tz_str
        else:
            now = datetime.now().astimezone()
    except Exception:
        now = datetime.now().astimezone()

    weekday = _WEEKDAYS_EN[now.weekday()]
    tz_label = tz_label or now.strftime("%Z") or now.strftime("%z")
    return f"[Current time: {weekday} {now.strftime('%Y-%m-%d')} {now.strftime('%H:%M')} {tz_label}]"
