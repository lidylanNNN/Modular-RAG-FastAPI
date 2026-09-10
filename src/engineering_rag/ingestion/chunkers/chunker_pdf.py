'''PDF chunker skeleton.'''

from engineering_rag.contracts.chunk import Chunk


def chunk_pdf(source_units: list[dict]) -> list[Chunk]:
    '''Convert PDF source units into unified chunks.'''
    raise NotImplementedError('PDF chunking is planned for M9.')

