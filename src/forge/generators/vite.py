import shutil
from enum import Enum
from pathlib import Path

import typer
from rich.console import Console

from forge.core.options import PackageManager
from forge.core.runner import CommandError, run_command
from forge.core.validators import validate_project_name

console = Console()


class Framework(str, Enum):
    VUE_TS = "vue-ts"
    REACT_TS = "react-ts"


def get_create_command(
    manager: PackageManager,
    project_name: str,
    framework: Framework,
) -> list[str]:
    """Build the official create-vite command."""
    if manager == PackageManager.NPM:
        return [
            "npm", "create", "vite@latest", project_name,
            "--", "--template", framework.value,
        ]

    if manager == PackageManager.PNPM:
        return [
            "pnpm", "create", "vite", project_name,
            "--template", framework.value,
        ]

    return [
        "yarn", "create", "vite", project_name,
        "--template", framework.value,
    ]


def generate_vite(
    name: str,
    framework: Framework,
    manager: PackageManager,
    parent_dir: Path | None = None,
    install_dependencies: bool = True,
) -> None:
    """Generate a Vue or React TypeScript frontend using Vite."""
    if not validate_project_name(name):
        console.print("[red]Invalid project name.[/red]")
        raise typer.Exit(code=1)

    base_dir = parent_dir or Path.cwd()
    project_path = base_dir / name

    if project_path.exists():
        console.print(f"[red]Destination already exists: {project_path}[/red]")
        raise typer.Exit(code=1)

    if shutil.which(manager.value) is None:
        console.print(
            f"[red]Package manager '{manager.value}' is not installed or not in PATH.[/red]"
        )
        raise typer.Exit(code=1)

    console.print("\n[bold cyan]FORGE[/bold cyan] — Vite Generator\n")
    console.print(f"Project: [bold]{name}[/bold]")
    console.print(f"Framework: [cyan]{framework.value}[/cyan]")
    console.print(f"Package manager: [cyan]{manager.value}[/cyan]\n")

    try:
        console.print("[bold]Creating Vite project...[/bold]")
        run_command(
            get_create_command(manager, name, framework),
            cwd=base_dir,
        )

        if not project_path.is_dir():
            raise CommandError(
                "Vite completed, but the project directory was not created."
            )

        if install_dependencies:
            console.print("\n[bold]Installing dependencies...[/bold]")
            run_command([manager.value, "install"], cwd=project_path)

    except (OSError, CommandError) as error:
        console.print(f"\n[red]Vite generation failed:[/red] {error}")
        console.print(
            f"[yellow]A partial project may remain at {project_path}.[/yellow]"
        )
        raise typer.Exit(code=1) from error

    console.print(f"\n[bold green]Frontend '{name}' created successfully![/bold green]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  cd {name}")
    console.print(f"  {manager.value} run dev")
