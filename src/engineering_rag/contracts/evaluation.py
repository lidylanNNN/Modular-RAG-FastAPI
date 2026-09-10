'''Evaluation dataset and run result contracts.'''

from pydantic import BaseModel, ConfigDict, Field


class GoldAnchor(BaseModel):
    '''Gold evidence anchor from an evaluation case.'''

    model_config = ConfigDict(extra='forbid')

    anchor_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    revision_id: str = Field(min_length=1)
    parse_artifact_id: str = Field(min_length=1)


class EvalCase(BaseModel):
    '''One evaluation question and its answerability metadata.'''

    model_config = ConfigDict(extra='allow')

    case_id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    answerable: bool


class RunResult(BaseModel):
    '''Serializable output for one evaluation run.'''

    model_config = ConfigDict(extra='forbid')

    run_id: str = Field(min_length=1)
    metrics: dict = Field(default_factory=dict)
    artifacts: list[str] = Field(default_factory=list)

