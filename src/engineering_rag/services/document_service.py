'''Document ingestion and lifecycle service.'''

from pathlib import Path


def ingest(path: Path) -> str:
    '''Ingest a document through the public service boundary.'''
    raise NotImplementedError('Document service ingestion is planned for M2.')


def delete(document_id: str) -> None:
    '''Delete a document through the public service boundary.'''
    raise NotImplementedError('Document deletion is planned for M5.')

