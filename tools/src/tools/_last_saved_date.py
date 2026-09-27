from datetime import datetime
from pathlib import Path
import subprocess

def git_repo_last_commit_datetime() -> datetime | None:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct"],
            capture_output=True, text=True, check=True
        )
        timestamp = int(result.stdout.strip())
        return datetime.fromtimestamp(timestamp)
    except subprocess.CalledProcessError:
        return None

def last_saved_datetime(path: str | Path, repo_wide: bool = False) -> datetime | None:
    """
    Return the datetime of the last Git commit for a file or repo.
    Falls back to filesystem modification time if not committed yet.

    :param path: Path to file or directory.
    :param repo_wide: If True, use the latest commit in the repo.
    :return: datetime object or None if unavailable.
    """
    path = Path(path).resolve()

    # --- 1. Try git commit timestamp ---
    try:
        args = ["git", "log", "-1", "--format=%ct"]
        if not repo_wide:
            args.append(str(path))
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        ts = result.stdout.strip()
        if ts:
            return datetime.fromtimestamp(int(ts))
    except subprocess.CalledProcessError:
        pass  # not in git or not committed

    # --- 2. Fall back to file modification time ---
    try:
        return datetime.fromtimestamp(path.stat().st_mtime)
    except FileNotFoundError:
        return None
