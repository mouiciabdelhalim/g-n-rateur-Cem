"""
rate_limit.py — Simple in-session rate limiting for Streamlit pages.

Prevents users from hammering the AI generation button, protecting
API quota and preventing resource exhaustion.

Usage:
    from backend.utils.rate_limit import check_rate_limit

    if not check_rate_limit("texte_gen"):
        st.warning("Trop de requêtes. Attendez 1 minute.")
        st.stop()
"""
import time
import streamlit as st

_DEFAULT_MAX_CALLS = 5   # max requests per window
_DEFAULT_WINDOW_SEC = 60  # rolling window in seconds


def check_rate_limit(
    action_key: str,
    max_calls: int = _DEFAULT_MAX_CALLS,
    window_sec: int = _DEFAULT_WINDOW_SEC,
) -> bool:
    """
    Returns True if the action is allowed, False if the rate limit is exceeded.

    Uses Streamlit session_state to track per-session call history.
    Each unique action_key has its own independent counter.

    Args:
        action_key:  Unique identifier for the action (e.g. 'texte_gen').
        max_calls:   Maximum allowed calls within the window (default 5).
        window_sec:  Rolling time window in seconds (default 60).

    Returns:
        True  — request allowed.
        False — rate limit exceeded, caller should stop and warn user.
    """
    now = time.time()
    state_key = f"_rl_{action_key}"
    history: list[float] = st.session_state.get(state_key, [])

    # Slide the window: discard timestamps older than window_sec
    history = [t for t in history if now - t < window_sec]

    if len(history) >= max_calls:
        return False

    history.append(now)
    st.session_state[state_key] = history
    return True


def remaining_wait(action_key: str, window_sec: int = _DEFAULT_WINDOW_SEC) -> int:
    """
    Returns the number of seconds until the next slot is available.
    Useful for telling the user how long to wait.
    """
    now = time.time()
    state_key = f"_rl_{action_key}"
    history: list[float] = st.session_state.get(state_key, [])
    if not history:
        return 0
    oldest_in_window = min(t for t in history if now - t < window_sec)
    return max(0, int(window_sec - (now - oldest_in_window)))
