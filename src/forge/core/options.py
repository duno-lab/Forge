from enum import Enum


class PackageManager(str, Enum):
    NPM = "npm"
    PNPM = "pnpm"
    YARN = "yarn"


class BackendFramework(str, Enum):
    NESTJS = "nestjs"
    FASTIFY = "fastify"
