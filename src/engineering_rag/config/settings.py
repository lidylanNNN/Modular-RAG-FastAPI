'''Runtime settings for Engineering RAG.'''

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    '''Resolved runtime settings used by the application.'''

    environment: str
    data_dir: Path
    artifacts_dir: Path
    elasticsearch_url: str
    active_snapshot: str | None
    embedding_model: str
    reranker_model: str
    llm_model: str | None


def load_settings() -> Settings:
    '''Load settings from environment variables with safe local defaults.'''
    return Settings(
        environment=os.getenv('ENGINEERING_RAG_ENV', 'development'),
        data_dir=Path(os.getenv('ENGINEERING_RAG_DATA_DIR', '.local')),
        artifacts_dir=Path(os.getenv('ENGINEERING_RAG_ARTIFACTS_DIR', 'artifacts')),
        elasticsearch_url=os.getenv('ENGINEERING_RAG_ELASTICSEARCH_URL', 'http://localhost:9200'),
        active_snapshot=os.getenv('ENGINEERING_RAG_ACTIVE_SNAPSHOT') or None,
        embedding_model=os.getenv('ENGINEERING_RAG_EMBEDDING_MODEL', 'BAAI/bge-m3'),
        reranker_model=os.getenv('ENGINEERING_RAG_RERANKER_MODEL', 'BAAI/bge-reranker-v2-m3'),
        llm_model=os.getenv('ENGINEERING_RAG_LLM_MODEL') or None,
    )

