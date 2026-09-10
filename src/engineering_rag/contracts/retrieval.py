'''Retrieval query and candidate contracts.'''

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RetrievalFilter(BaseModel):
    '''Structured filter accepted by retrieval before candidate ranking.'''

    model_config = ConfigDict(extra='forbid')

    document_ids: list[str] | None = None
    revision_ids: list[str] | None = None
    file_types: list[Literal['docx', 'pdf', 'pptx', 'xlsx']] | None = None
    sheet: str | None = None


class SearchQuery(BaseModel):
    '''User query plus retrieval budget and filtering options.'''

    model_config = ConfigDict(extra='forbid')

    question: str = Field(min_length=1)
    filters: RetrievalFilter = Field(default_factory=RetrievalFilter)
    top_k: int = Field(default=5, ge=1, le=50)


class Candidate(BaseModel):
    '''Candidate chunk returned by one retrieval or fusion stage.'''

    model_config = ConfigDict(extra='forbid')

    chunk_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    rank: int = Field(ge=1)
    score: float | None = None
    source: Literal['bm25', 'dense', 'rrf', 'reranker']
    metadata: dict = Field(default_factory=dict)


class FinalCandidate(Candidate):
    '''Final ranked candidate after reranking and evidence validation.'''

    source_id: str = Field(min_length=1)

