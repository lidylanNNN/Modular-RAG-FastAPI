'''Generation, citation, and refusal contracts.'''

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Citation(BaseModel):
    '''Citation that binds generated text to a request-local source.'''

    model_config = ConfigDict(extra='forbid')

    source_id: str = Field(min_length=1)
    quote: str = Field(min_length=1)


class Claim(BaseModel):
    '''Atomic answer claim that must be checked against evidence.'''

    model_config = ConfigDict(extra='forbid')

    text: str = Field(min_length=1)
    citation_ids: list[str] = Field(default_factory=list)


class Answer(BaseModel):
    '''Generated answer with claims, citations, and refusal status.'''

    model_config = ConfigDict(extra='forbid')

    text: str
    claims: list[Claim] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    refusal_reason: Literal['insufficient_evidence', 'version_conflict', 'unsupported_claim'] | None = None

