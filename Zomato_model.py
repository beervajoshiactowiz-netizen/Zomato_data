from pydantic import BaseModel, Field
from typing import List, Optional,Any,Dict

class ZomatoItem(BaseModel):
    item_id: str
    item_name: str
    item_slug: List[str] = Field(default_factory=list)
    item_description: Optional[str] = "No description available"
    is_veg: bool = True


class ZomatoCategory(BaseModel):
    category_name: str
    items: List[ZomatoItem]

class ZomatoRestaurant(BaseModel):
    restaurant_id: int
    restaurant_name: str
    restaurant_url:str
    restaurant_contact:List[str]
    fssai_licence_number:List[str]
    address_info:Dict[str,Any]
    cuisines:List[Dict[str,Any]]
    timings:Dict[str,Any]
    menu_categories: List[ZomatoCategory]
