import re


_PROJECT_NAME_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]*")


def validate_project_name(name: str) -> bool:
    """Validate a project directory name."""
    return bool(_PROJECT_NAME_PATTERN.fullmatch(name))


def normalize_python_package_name(name: str) -> str:
    """Convert a project name into a valid Python package name."""
    return name.replace("-", "_").replace(" ", "_").lower()


def normalize_npm_package_name(name: str) -> str:
    """Convert a project name into a simple lowercase npm package name."""
    normalized = re.sub(r"[^a-z0-9._-]+", "-", name.lower())
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    return normalized
