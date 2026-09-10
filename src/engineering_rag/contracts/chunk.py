'''Chunk and source span contracts.'''

from pydantic import BaseModel, ConfigDict, Field


class SourceSpan(BaseModel):
    '''Character span that points back to a parsed source unit.'''

    model_config = ConfigDict(extra='forbid')

    unit_id: str = Field(min_length=1)
    char_start: int = Field(ge=0)
    char_end: int = Field(gt=0)


class Chunk(BaseModel):
    '''Unified chunk contract used by indexing, retrieval, and citation.'''

    model_config = ConfigDict(extra='forbid')

    chunk_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    revision_id: str = Field(min_length=1)
    parse_artifact_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    chunk_index: int = Field(ge=0)
    source_spans: list[SourceSpan]
    metadata: dict = Field(default_factory=dict)


class ChunkFailure(BaseModel):
    '''Structured failure emitted when a parsed unit cannot become a chunk.'''

    model_config = ConfigDict(extra='forbid')

    source_id: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    detail: str = Field(min_length=1)

