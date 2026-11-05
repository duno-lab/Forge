import shutil
from pathlib import Path

import typer
from rich.console import Console

from forge.core.options import PackageManager
from forge.core.runner import CommandError, run_command
from forge.core.validators import validate_project_name

console = Console()


def generate_nestjs(
    name: str,
    manager: PackageManager,
    parent_dir: Path | None = None,
    install_dependencies: bool = True,
) -> None:
    """Generate a NestJS backend using the official Nest CLI."""
    if not validate_project_name(name):
        console.print("[red]Invalid project name.[/red]")
        raise typer.Exit(code=1)

    base_dir = parent_dir or Path.cwd()
    project_path = base_dir / name

    if project_path.exists():
        console.print(f"[red]Destination already exists: {project_path}[/red]")
        raise typer.Exit(code=1)

    if shutil.which("npx") is None:
        console.print("[red]npx is not installed or not available in PATH.[/red]")
        raise typer.Exit(code=1)

    if shutil.which(manager.value) is None:
        console.print(
            f"[red]Package manager '{manager.value}' is not installed or not in PATH.[/red]"
        )
        raise typer.Exit(code=1)

    command = [
        "npx", "--yes", "@nestjs/cli", "new", name,
        "--package-manager", manager.value,
        "--skip-git",
    ]

    if not install_dependencies:
        command.append("--skip-install")

    console.print("\n[bold cyan]FORGE[/bold cyan] — NestJS Generator\n")
    console.print(f"Project: [bold]{name}[/bold]")
    console.print(f"Package manager: [cyan]{manager.value}[/cyan]\n")

    try:
        console.print("[bold]Generating NestJS project...[/bold]\n")
        run_command(command, cwd=base_dir)

        if not project_path.is_dir():
            raise CommandError(
                "Nest CLI completed, but the project directory was not created."
            )

    except (OSError, CommandError) as error:
        console.print(f"\n[red]NestJS generation failed:[/red] {error}")
        console.print(
            f"[yellow]A partial project may remain at {project_path}.[/yellow]"
        )
        raise typer.Exit(code=1) from error

    console.print(f"\n[bold green]NestJS backend '{name}' created successfully![/bold green]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  cd {name}")
    console.print(f"  {manager.value} run start:dev")
