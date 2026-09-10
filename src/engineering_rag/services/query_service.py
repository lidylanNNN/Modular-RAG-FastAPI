'''Query service boundary.'''

from engineering_rag.contracts.retrieval import FinalCandidate, SearchQuery


def search_knowledge(query: SearchQuery) -> list[FinalCandidate]:
    '''Search engineering knowledge through the public service boundary.'''
    raise NotImplementedError('Query service search is planned for M4-M7.')

