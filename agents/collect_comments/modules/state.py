
from __future__ import annotations
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field, ConfigDict
from selenium.webdriver.chrome.webdriver import WebDriver
from langgraph.graph.message import add_messages


class CollectCommentsState(BaseModel):
    driver: Optional[WebDriver] = Field(default=None)
    profile_url: str = Field(default="https://www.instagram.com/hanr0r0/")
    post_links: List[str] = Field(default_factory=list)
    current_post_url: Optional[str] = Field(default=None)
    page_source: Optional[str] = Field(default=None)
    comments: List[str] = Field(default_factory=list)
    csv_filename: str = Field(default="instagram_comments.csv")

    
    response: Annotated[List[str], add_messages] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)
