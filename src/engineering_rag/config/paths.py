'''Cross-platform path resolution helpers.'''

from pathlib import Path

from engineering_rag.config.settings import Settings


def resolve_runtime_path(base: Path, value: str | Path) -> Path:
    '''Resolve a configured path relative to a base directory when needed.'''
    path = Path(value)
    return path if path.is_absolute() else base / path


def ensure_runtime_directories(settings: Settings) -> None:
    '''Create local runtime directories that are intentionally ignored by Git.'''
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.artifacts_dir.mkdir(parents=True, exist_ok=True)

