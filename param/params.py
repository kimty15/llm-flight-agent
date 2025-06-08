from pydantic import BaseModel, Field
from typing import List, Optional, Type

class FoodPlace(BaseModel):
    name: str
    address: str
    rating: Optional[float] = None
    price_level: Optional[str] = None
    type: Optional[str] = None

class FoodSearchResponse(BaseModel):
    places: List[FoodPlace]
    location: str
    # is_nha_trang: bool = Field(default=False, description="Whether the query is for Nha Trang")

class FoodQuery(BaseModel):
    query: str = Field(..., description="The type of food or cuisine to search for")
    location: Optional[str] = Field(None, description="The location to search in")
    is_nha_trang: bool = Field(default=False, description="Whether the query is for Nha Trang")
