# src/a2a_cross_framework_poc/shared/schema/a2a_protocol_models.py

from typing import List, Optional, Union, Literal, Dict
from pydantic import BaseModel

class TextPart(BaseModel):
    type: Literal["text"] = "text"
    text: str
    metadata: Optional[Dict[str, any]] = {}

class FilePart(BaseModel):
    type: Literal["file"] = "file"
    file: Dict[str, Optional[str]]  # name, mimeType, bytes or uri
    metadata: Optional[Dict[str, any]] = {}

class DataPart(BaseModel):
    type: Literal["data"] = "data"
    data: Dict[str, any]
    metadata: Optional[Dict[str, any]] = {}

Part = Union[TextPart, FilePart, DataPart]

class Message(BaseModel):
    role: Literal["user", "agent"]
    parts: List[Part]
    metadata: Optional[Dict[str, any]] = {}

class Artifact(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parts: List[Part]
    metadata: Optional[Dict[str, any]] = {}
    index: int
    append: Optional[bool] = False
    lastChunk: Optional[bool] = True

class PushNotificationConfig(BaseModel):
    url: str
    token: Optional[str] = None
    authentication: Optional[Dict[str, Optional[str]]] = None

class TaskPushNotificationConfig(BaseModel):
    id: str
    pushNotificationConfig: PushNotificationConfig

class Skill(BaseModel):
    id: str
    name: str
    description: str
    tags: List[str]
    examples: Optional[List[str]] = []
    inputModes: Optional[List[str]] = []
    outputModes: Optional[List[str]] = []

class AgentCard(BaseModel):
    name: str
    description: str
    url: str
    provider: Optional[Dict[str, str]] = None
    version: str
    documentationUrl: Optional[str] = None
    capabilities: Dict[str, bool]
    authentication: Dict[str, Optional[Union[str, List[str]]]]
    defaultInputModes: List[str]
    defaultOutputModes: List[str]
    skills: List[Skill]
