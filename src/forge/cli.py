import typer
from rich.console import Console

from forge.commands.doctor import doctor
from forge.commands.init import init_project
from forge.core.options import BackendFramework, PackageManager
from forge.generators.fastify import generate_fastify
from forge.generators.nestjs import generate_nestjs
from forge.generators.saas import generate_saas
from forge.generators.vite import Framework, generate_vite

app = typer.Typer(
    name="forge",
    help="A toolkit for automating developer workflows.",
    no_args_is_help=True,
)

console = Console()


@app.callback()
def main() -> None:
    """FORGE - Developer Workflow Automation Toolkit."""


@app.command()
def version() -> None:
    """Display FORGE version."""
    console.print("[bold cyan]FORGE[/bold cyan] v0.1.0")


app.command(name="doctor")(doctor)
app.command(name="init")(init_project)


@app.command()
def frontend(
    name: str,
    framework: Framework = typer.Option(
        Framework.VUE_TS,
        "--framework",
        "-f",
        help="Frontend framework to use.",
    ),
    manager: PackageManager = typer.Option(
        PackageManager.PNPM,
        "--manager",
        "-m",
        help="JavaScript package manager.",
    ),
) -> None:
    """Generate a frontend project using Vite."""
    generate_vite(name, framework, manager)


@app.command()
def backend(
    name: str,
    framework: BackendFramework = typer.Option(
        BackendFramework.FASTIFY,
        "--framework",
        "-f",
        help="Backend framework to use.",
    ),
    manager: PackageManager = typer.Option(
        PackageManager.PNPM,
        "--manager",
        "-m",
        help="JavaScript package manager.",
    ),
) -> None:
    """Generate a backend project."""
    if framework == BackendFramework.FASTIFY:
        generate_fastify(name, manager)
    else:
        generate_nestjs(name, manager)


@app.command()
def saas(
    name: str,
    frontend: Framework = typer.Option(
        Framework.VUE_TS,
        "--frontend",
        "-f",
        help="Frontend framework.",
    ),
    backend: BackendFramework = typer.Option(
        BackendFramework.FASTIFY,
        "--backend",
        "-b",
        help="Backend framework.",
    ),
    manager: PackageManager = typer.Option(
        PackageManager.PNPM,
        "--manager",
        "-m",
        help="JavaScript package manager.",
    ),
) -> None:
    """Generate a complete SaaS monorepo."""
    generate_saas(name, frontend, backend, manager)


if __name__ == "__main__":
    app()
