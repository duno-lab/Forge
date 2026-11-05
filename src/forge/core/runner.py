import shutil
import subprocess
from pathlib import Path
from typing import Mapping


class CommandError(Exception):
    """Raised when an external command fails."""


def run_command(
    command: list[str],
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a command without a shell and stream its output to the terminal."""
    if not command:
        raise CommandError("Cannot execute an empty command.")

    executable = shutil.which(command[0])
    if executable is None:
        raise CommandError(
            f"Required tool '{command[0]}' is not installed or not available in PATH."
        )

    try:
        result = subprocess.run(
            [executable, *command[1:]],
            cwd=cwd,
            env=dict(env) if env is not None else None,
            check=False,
            text=True,
        )
    except OSError as error:
        raise CommandError(f"Could not execute '{command[0]}': {error}") from error

    if result.returncode != 0:
        raise CommandError(
            f"Command '{command[0]}' failed with exit code {result.returncode}."
        )

    return result
