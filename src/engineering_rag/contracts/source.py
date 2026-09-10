'''Source document identity contracts.'''

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SourceDocument(BaseModel):
    '''Identity and immutable file metadata for one document revision.'''

    model_config = ConfigDict(extra='forbid')

    document_id: str = Field(min_length=1)
    revision_id: str = Field(min_length=1)
    file_name: str = Field(min_length=1)
    file_type: Literal['docx', 'pdf', 'pptx', 'xlsx']
    content_hash: str = Field(pattern='^[0-9a-f]{64}$')
    version: str | None = None
    is_current: bool = True


class ParseArtifact(BaseModel):
    '''Identity for parsed source content created from one source revision.'''

    model_config = ConfigDict(extra='forbid')

    parse_artifact_id: str = Field(pattern='^[0-9a-f]{64}$')
    revision_id: str = Field(min_length=1)
    parser_identity: str = Field(min_length=1)

