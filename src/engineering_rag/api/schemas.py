'''HTTP request and response schemas.'''

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    '''Response returned by the health endpoint.'''

    model_config = ConfigDict(extra='forbid')

    status: str = Field(min_length=1)

