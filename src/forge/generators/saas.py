import json
import shutil
from pathlib import Path

import typer
from rich.console import Console

from forge.core.options import BackendFramework, PackageManager
from forge.core.runner import CommandError, run_command
from forge.core.validators import normalize_npm_package_name, validate_project_name
from forge.generators.fastify import generate_fastify
from forge.generators.nestjs import generate_nestjs
from forge.generators.vite import Framework, generate_vite

console = Console()


def _workspace_readme_commands(
    manager: PackageManager,
    backend: BackendFramework,
) -> tuple[str, str]:
    api_script = "start:dev" if backend == BackendFramework.NESTJS else "dev"

    if manager == PackageManager.NPM:
        return (
            "npm run dev --workspace apps/web",
            f"npm run {api_script} --workspace apps/api",
        )

    if manager == PackageManager.PNPM:
        return (
            "pnpm --filter web dev",
            f"pnpm --filter api {api_script}",
        )

    return (
        "yarn workspace web dev",
        f"yarn workspace api {api_script}",
    )


def generate_saas(
    name: str,
    frontend: Framework,
    backend: BackendFramework,
    manager: PackageManager,
) -> None:
    """Generate a full-stack SaaS monorepo."""
    if not validate_project_name(name):
        console.print("[red]Invalid project name.[/red]")
        raise typer.Exit(code=1)

    project_path = Path.cwd() / name
    apps_path = project_path / "apps"

    if project_path.exists():
        console.print(f"[red]Destination already exists: {project_path}[/red]")
        raise typer.Exit(code=1)

    if shutil.which(manager.value) is None:
        console.print(
            f"[red]Package manager '{manager.value}' is not installed or not in PATH.[/red]"
        )
        raise typer.Exit(code=1)

    package_name = normalize_npm_package_name(name)
    web_command, api_command = _workspace_readme_commands(manager, backend)

    console.print("\n[bold cyan]FORGE[/bold cyan] — SaaS Generator\n")
    console.print(f"Project: [bold]{name}[/bold]")
    console.print(f"Frontend: [cyan]{frontend.value}[/cyan]")
    console.print(f"Backend: [cyan]{backend.value}[/cyan]")
    console.print(f"Package manager: [cyan]{manager.value}[/cyan]\n")

    try:
        apps_path.mkdir(parents=True)

        root_package = {
            "name": package_name,
            "version": "1.0.0",
            "private": True,
        }

        if manager in (PackageManager.NPM, PackageManager.YARN):
            root_package["workspaces"] = ["apps/*"]

        (project_path / "package.json").write_text(
            json.dumps(root_package, indent=2) + "\n",
            encoding="utf-8",
        )

        (project_path / ".gitignore").write_text(
            "node_modules/\ndist/\n.env\n.env.*\n!.env.example\ncoverage/\n*.log\n",
            encoding="utf-8",
        )

        (project_path / "README.md").write_text(
            f"""# {name}

Full-stack SaaS monorepo generated with FORGE.

## Applications

- `apps/web`: {frontend.value} frontend
- `apps/api`: {backend.value} backend

## Development

Run the frontend:

```bash
{web_command}
```

Run the backend in another terminal:

```bash
{api_command}
```
""",
            encoding="utf-8",
        )

        if manager == PackageManager.PNPM:
            (project_path / "pnpm-workspace.yaml").write_text(
                "packages:\n  - 'apps/*'\n",
                encoding="utf-8",
            )

        console.print("[bold]Generating frontend...[/bold]")
        generate_vite(
            name="web",
            framework=frontend,
            manager=manager,
            parent_dir=apps_path,
            install_dependencies=False,
        )

        console.print("\n[bold]Generating backend...[/bold]")
        if backend == BackendFramework.FASTIFY:
            generate_fastify(
                name="api",
                manager=manager,
                parent_dir=apps_path,
                install_dependencies=False,
            )
        else:
            generate_nestjs(
                name="api",
                manager=manager,
                parent_dir=apps_path,
                install_dependencies=False,
            )

        console.print("\n[bold]Installing workspace dependencies...[/bold]\n")
        run_command([manager.value, "install"], cwd=project_path)

    except (OSError, CommandError) as error:
        console.print(f"\n[red]SaaS generation failed:[/red] {error}")
        console.print(
            f"[yellow]A partial project may remain at {project_path}.[/yellow]"
        )
        raise typer.Exit(code=1) from error

    console.print(f"\n[bold green]SaaS project '{name}' created successfully![/bold green]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  cd {name}")
    console.print(f"  {web_command}")
    console.print(f"  {api_command}")
