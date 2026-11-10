from pathlib import Path

ROOT = Path(__file__).resolve().parent


def asset(name):
    """Resolve a project resource independently of the working directory."""
    return str(ROOT / name)
