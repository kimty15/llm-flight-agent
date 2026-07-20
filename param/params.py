from pydantic import BaseModel, Field


class FoodPlace(BaseModel):
    name: str
    address: str
    rating: float | None = None
    price_level: str | None = None
    type: str | None = None


class FoodSearchResponse(BaseModel):
    places: list[FoodPlace]
    location: str


class FoodQuery(BaseModel):
    query: str = Field(..., description="Food, cuisine, or meal stop to search for")
    location: str | None = Field(None, description="Location to search in")
    is_nha_trang: bool = Field(
        default=False,
        description="Whether the query is for Nha Trang",
    )
