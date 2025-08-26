from enum import Enum
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field


class StoryData(BaseModel):
    name: str = Field(..., description="The name of the story")
    description: str = Field(..., description="The description of the story")
    image_prompt: str = Field(
        ..., description="The prompt for generating images related to the story"
    )


class Character(BaseModel):
    name: str = Field(..., description="The name of the character")
    description: str = Field(..., description="The description of the character")
    physicality: str = Field(
        ..., description="The physical attributes of the character"
    )
    psychology: str = Field(
        ..., description="The psychological traits of the character"
    )


class Relationship(BaseModel):
    type: str = Field(..., description="The type of relationship")
    details: str = Field(..., description="Details about the relationship")
    connection: List[str] = Field(
        ..., description="Connection points between characters"
    )


class MinMax(str, Enum):
    MIN = "min"
    STANDARD = "standard"
    MAX = "max"


class Tone(BaseModel):
    name: str = Field(..., description="The name of the tone")
    value: MinMax = Field(..., description="The value of the tone")
    hints: Optional[List[str]] = Field(None, description="Optional hints for the tone")


class TablePrompt(BaseModel):
    premise: str = Field(..., description="The premise of the story")
    environment: str = Field(
        ..., description="The environment the story takes place in"
    )
    exposition: str = Field(..., description="The exposition of the story")
    first_action: str = Field(..., description="The first action in the story")
    main_character: Character = Field(
        ..., description="The main character of the story"
    )
    side_characters: Optional[List[Character]] = Field(
        None, description="Optional side characters in the story"
    )
    relationships: Optional[List[Relationship]] = Field(
        None, description="Optional relationships between characters"
    )
    winning_scenarios: Optional[List[str]] = Field(
        None, description="Optional winning scenarios in the story"
    )
    losing_scenarios: Optional[List[str]] = Field(
        None, description="Optional losing scenarios in the story"
    )
    key_events: Optional[List[str]] = Field(
        None, description="Optional key events in the story"
    )
    tense: Literal["past", "present", "future"] = Field(
        ..., description="The tense of the story"
    )
    story_arcs: MinMax = Field(..., description="The complexity of the story arcs")
    writing_style: str = Field(..., description="The style of writing for the story")
    voice: str = Field(..., description="The narrative voice of the story")
    pacing: MinMax = Field(..., description="The pacing of the story")
    pov: Optional[Literal["first", "second", "third"]] = Field(
        None, description="The point of view of the story"
    )
    tone: Optional[Tone] = Field(
        None, description="Optional tones to be used in the story"
    )
    additional_data: Optional[str] = Field(
        None, description="Any additional data relevant to the story"
    )


class TopicDraft(BaseModel):
    title: str = Field(..., description="The title of the topic")
    story_data: Optional[StoryData] = Field(
        None, description="Optional story data associated with the topic"
    )
    open_prompt: Optional[str] = Field(..., description="The open prompt of the topic")
    table_prompt: Optional[TablePrompt] = Field(
        ..., description="The detailed table prompt for the topic"
    )
