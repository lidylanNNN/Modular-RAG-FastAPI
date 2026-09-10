'''Unified retrieval service.'''

from engineering_rag.contracts.retrieval import FinalCandidate, SearchQuery


def search(query: SearchQuery) -> list[FinalCandidate]:
    '''Run the configured retrieval pipeline for one query.'''
    raise NotImplementedError('Unified retrieval is planned for M4-M7.')

