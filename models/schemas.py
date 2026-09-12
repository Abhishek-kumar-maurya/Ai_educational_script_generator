from pydantic import BaseModel, Field

class Scene(BaseModel):
    start_time: str
    end_time: str
    visual_animation: str = Field(min_length=1)
    voiceover_dialogue: str = Field(min_length=1)
    ots_sfx: str = ""

class Script(BaseModel):
    scenes: list[Scene] = Field(min_length=1)

class Concept(BaseModel):
    name: str
    source_page: int
    evidence: str

class ConceptList(BaseModel):
    concepts: list[Concept]
