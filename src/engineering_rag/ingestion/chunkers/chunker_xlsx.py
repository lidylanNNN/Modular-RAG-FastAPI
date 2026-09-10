'''XLSX chunker skeleton.'''

from engineering_rag.contracts.chunk import Chunk


def chunk_xlsx(source_units: list[dict]) -> list[Chunk]:
    '''Convert XLSX source units into unified chunks.'''
    raise NotImplementedError('XLSX chunking is planned for M3.')

