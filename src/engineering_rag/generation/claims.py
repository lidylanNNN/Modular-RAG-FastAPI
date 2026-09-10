'''Answer claim extraction.'''

from engineering_rag.contracts.generation import Claim


def extract_claims(answer_text: str) -> list[Claim]:
    '''Extract atomic claims from generated answer text.'''
    raise NotImplementedError('Claim extraction is planned for M8.')

