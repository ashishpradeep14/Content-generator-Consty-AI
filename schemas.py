from pydantic import BaseModel
from typing import Optional

class ContentRequest(BaseModel):
    prompt: str
    content_type: str = "summary"