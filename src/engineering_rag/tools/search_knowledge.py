'''search_knowledge tool adapter.'''

from engineering_rag.contracts.retrieval import FinalCandidate, SearchQuery
from engineering_rag.services.query_service import search_knowledge as service_search_knowledge


def search_knowledge(query: SearchQuery) -> list[FinalCandidate]:
    '''Call the public query service from the tool adapter.'''
    return service_search_knowledge(query)

