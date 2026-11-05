
import re
from pathlib import Path

import typer
from rich.console import Console

console = Console()


def normalize_package_name(name: str) -> str:
    """Convert a project name into a valid Python package name."""
    return name.replace("-", "_").replace(" ", "_").lower()


def init_project(name: str):
    """Create a new Python project."""

    if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]*", name):
        console.print(
            "[red]Invalid project name.[/red] "
            "Use letters, numbers, hyphens or underscores, "
            "and start with a letter."
        )
        raise typer.Exit(code=1)

    project_path = Path.cwd() / name

    if project_path.exists():
        console.print(
            f"[red]Cannot create project:[/red] "
            f"'{name}' already exists."
        )
        raise typer.Exit(code=1)

    package_name = normalize_package_name(name)
    package_path = project_path / "src" / package_name

    files = {
        project_path / "README.md": f"""# {name}

A Python project created with FORGE.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Tests

```bash
pytest
```
""",
        project_path / "pyproject.toml": f"""[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
description = "A Python project."
requires-python = ">=3.11"

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
""",
        project_path / ".gitignore": """# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# Virtual environment
.venv/
venv/

# IDE
.idea/
.vscode/

# Environment variables
.env
""",
        package_path / "__init__.py": f'"""The {name} package."""\n',
        project_path / "tests" / "__init__.py": "",
    }

    try:
        for directory in (
            package_path,
            project_path / "tests",
        ):
            directory.mkdir(parents=True, exist_ok=True)

        for file_path, content in files.items():
            file_path.write_text(content, encoding="utf-8")

    except OSError as error:
        console.print(f"[red]Project creation failed:[/red] {error}")
        raise typer.Exit(code=1) from error

    console.print()
    console.print(f"[bold green]Project '{name}' created successfully![/bold green]")
    console.print(f"[dim]Location: {project_path}[/dim]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  cd {name}")
    console.print("  python -m venv .venv")
    console.print("  source .venv/bin/activate")
    console.print("  pip install -e '.[dev]'")
