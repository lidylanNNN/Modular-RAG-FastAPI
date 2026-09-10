'''Generation context construction.'''

from engineering_rag.contracts.retrieval import FinalCandidate


def build_context(candidates: list[FinalCandidate], token_budget: int) -> list[FinalCandidate]:
    '''Select candidates that fit within the generation context budget.'''
    raise NotImplementedError('Context construction is planned for M8.')

