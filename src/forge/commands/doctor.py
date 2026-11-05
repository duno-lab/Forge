
import platform
import shutil
import subprocess
import sys

from rich.console import Console
from rich.table import Table

console = Console()


def get_command_version(command: str, args: list[str]) -> str | None:
    """Return a command's version if installed."""
    executable = shutil.which(command)

    if executable is None:
        return None

    try:
        result = subprocess.run(
            [executable, *args],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        if result.returncode != 0:
            return None

        output = (result.stdout or result.stderr).strip()

        return output.splitlines()[0] if output else None

    except (subprocess.TimeoutExpired, OSError):
        return None


def doctor():
    """Inspect the development environment."""

    console.print("\n[bold cyan]FORGE[/bold cyan] — Environment Doctor\n")

    table = Table(title="Development Environment")
    table.add_column("Tool", style="bold")
    table.add_column("Version")
    table.add_column("Status", justify="center")

    table.add_row(
        "Python",
        platform.python_version(),
        "[green]Available[/green]",
    )

    tools = [
        ("Git", "git", ["--version"]),
        ("Node.js", "node", ["--version"]),
        ("npm", "npm", ["--version"]),
        ("pnpm", "pnpm", ["--version"]),
        ("Docker", "docker", ["--version"]),
    ]

    for name, command, args in tools:
        version = get_command_version(command, args)

        if version:
            table.add_row(name, version, "[green]Available[/green]")
        else:
            table.add_row(name, "Not detected", "[yellow]Missing[/yellow]")

    console.print(table)

    console.print(
        f"\n[dim]Operating system: "
        f"{platform.system()} {platform.release()}[/dim]"
    )
