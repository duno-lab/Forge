import json
import shutil
from pathlib import Path

import typer
from rich.console import Console

from forge.core.options import PackageManager
from forge.core.runner import CommandError, run_command
from forge.core.validators import normalize_npm_package_name, validate_project_name

console = Console()


def get_install_command(manager: PackageManager) -> list[str]:
    """Return the install command for the selected package manager."""
    return {
        PackageManager.NPM: ["npm", "install"],
        PackageManager.PNPM: ["pnpm", "install"],
        PackageManager.YARN: ["yarn", "install"],
    }[manager]


def generate_fastify(
    name: str,
    manager: PackageManager,
    parent_dir: Path | None = None,
    install_dependencies: bool = True,
) -> None:
    """Generate a Fastify API using TypeScript."""
    if not validate_project_name(name):
        console.print("[red]Invalid project name.[/red]")
        raise typer.Exit(code=1)

    base_dir = parent_dir or Path.cwd()
    project_path = base_dir / name

    if project_path.exists():
        console.print(f"[red]Destination already exists: {project_path}[/red]")
        raise typer.Exit(code=1)

    if install_dependencies and shutil.which(manager.value) is None:
        console.print(
            f"[red]Package manager '{manager.value}' is not installed or not in PATH.[/red]"
        )
        raise typer.Exit(code=1)

    package_name = normalize_npm_package_name(name)

    json_files = {
        "package.json": {
            "name": package_name,
            "version": "1.0.0",
            "private": True,
            "type": "module",
            "scripts": {
                "dev": "tsx watch src/server.ts",
                "build": "tsc -p tsconfig.json",
                "start": "node dist/server.js",
                "test": "vitest run",
                "test:watch": "vitest",
                "typecheck": "tsc --noEmit",
            },
            "dependencies": {
                "dotenv": "^16.4.7",
                "fastify": "^5.0.0",
            },
            "devDependencies": {
                "@types/node": "^22.0.0",
                "tsx": "^4.19.0",
                "typescript": "^5.7.0",
                "vitest": "^3.0.0",
            },
        },
        "tsconfig.json": {
            "compilerOptions": {
                "target": "ES2022",
                "module": "NodeNext",
                "moduleResolution": "NodeNext",
                "rootDir": "src",
                "outDir": "dist",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "declaration": True,
                "sourceMap": True,
            },
            "include": ["src/**/*.ts"],
            "exclude": ["node_modules", "dist", "test"],
        },
    }

    text_files = {
        "src/app.ts": """\
import Fastify from 'fastify'
import { healthRoutes } from './routes/health.route.js'

export function buildApp() {
  const app = Fastify({
    logger: true,
  })

  app.register(healthRoutes)

  return app
}
""",
        "src/server.ts": """\
import 'dotenv/config'
import { buildApp } from './app.js'

const app = buildApp()

const port = Number(process.env.PORT ?? 4000)
const host = process.env.HOST ?? '0.0.0.0'

try {
  await app.listen({ port, host })
} catch (error) {
  app.log.error(error)
  await app.close()
  process.exitCode = 1
}
""",
        "src/routes/health.route.ts": """\
import type { FastifyInstance } from 'fastify'

export async function healthRoutes(app: FastifyInstance): Promise<void> {
  app.get('/health', async () => ({
    status: 'ok',
    timestamp: new Date().toISOString(),
  }))
}
""",
        "test/health.test.ts": """\
import { afterAll, beforeAll, describe, expect, it } from 'vitest'
import type { FastifyInstance } from 'fastify'
import { buildApp } from '../src/app.js'

describe('GET /health', () => {
  let app: FastifyInstance

  beforeAll(async () => {
    app = buildApp()
    await app.ready()
  })

  afterAll(async () => {
    await app.close()
  })

  it('returns the API health status', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/health',
    })

    expect(response.statusCode).toBe(200)
    expect(response.json()).toMatchObject({ status: 'ok' })
  })
})
""",
        ".env.example": "PORT=4000\nHOST=0.0.0.0\n",
        ".gitignore": "node_modules/\ndist/\n.env\ncoverage/\n*.log\n",
        "README.md": f"""\
# {name}

A Fastify API powered by TypeScript and generated with FORGE.

## Getting started

Copy `.env.example` to `.env`, then run:

```bash
{manager.value} run dev
```

## Scripts

- `dev`: Start the development server.
- `build`: Compile TypeScript.
- `start`: Run the compiled server.
- `test`: Run tests.
- `typecheck`: Check TypeScript types.

## Health check

`GET /health`
""",
    }

    console.print("\n[bold cyan]FORGE[/bold cyan] — Fastify Generator\n")

    try:
        project_path.mkdir(parents=True)

        for relative_path, content in json_files.items():
            destination = project_path / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(
                json.dumps(content, indent=2) + "\n",
                encoding="utf-8",
            )

        for relative_path, content in text_files.items():
            destination = project_path / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")

        console.print("[green]Project structure created.[/green]")

        if install_dependencies:
            console.print("[cyan]Installing dependencies...[/cyan]\n")
            run_command(get_install_command(manager), cwd=project_path)

    except (OSError, CommandError) as error:
        console.print(f"\n[red]Fastify generation failed:[/red] {error}")
        console.print(
            f"[yellow]A partial project may remain at {project_path}.[/yellow]"
        )
        raise typer.Exit(code=1) from error

    console.print(f"\n[bold green]Fastify project '{name}' created successfully![/bold green]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  cd {name}")
    console.print(f"  {manager.value} run dev")
