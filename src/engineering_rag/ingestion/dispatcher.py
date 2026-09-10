'''Document ingestion dispatcher.'''

from pathlib import Path


def ingest_document(path: Path) -> str:
    '''Dispatch a document into the parser and indexing pipeline.'''
    raise NotImplementedError('Document ingestion is planned for M2.')

