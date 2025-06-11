"""Parameter models for food search functionality."""

from pydantic import BaseModel, Field
from typing import List, Optional

class FoodPlace(BaseModel):
    """Model for a food place/restaurant."""
    name: str = Field(..., description="Name of the food place")
    address: str = Field(..., description="Address of the food place")
    rating: Optional[float] = Field(None, description="Rating of the food place")
    price_level: Optional[str] = Field(None, description="Price level indicator")
    type: Optional[str] = Field(None, description="Type of cuisine or establishment")

class FoodSearchResponse(BaseModel):
    """Response model for food search results."""
    places: List[FoodPlace] = Field(..., description="List of found food places")
    location: str = Field(..., description="Location searched")

class FoodQuery(BaseModel):
    """Model for parsed food search queries."""
    query: str = Field(..., description="The type of food or cuisine to search for")
    location: Optional[str] = Field(None, description="The location to search in")
    is_nha_trang: bool = Field(default=False, description="Whether the query is for Nha Trang") 