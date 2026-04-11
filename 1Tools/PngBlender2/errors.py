from __future__ import annotations

# later this may be replaced with a proper logging system


def report_error(message: str) -> None:
    """
    Report a non-fatal error to the console.

    Args:
        message: Human-readable error message.
    """
    print(f"[ERROR] {message}")


def report_warning(message: str) -> None:
    """
    Report a non-fatal warning to the console.

    Args:
        message: Human-readable warning message.
    """
    print(f"[WARN] {message}")


def report_info(message: str) -> None:
    """
    Report a non-fatal informational message to the console.

    Args:
        message: Human-readable informational message.
    """
    print(f"[INFO] {message}")
