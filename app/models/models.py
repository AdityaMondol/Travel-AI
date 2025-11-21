from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class Place(BaseModel):
    name: str
    rating: float
    description: str
    facilities: List[str]
    image_url: str
    best_time: str
    entry_fee: str
    duration: str

class WeatherInfo(BaseModel):
    current_season: str
    temperature_range: str
    best_time: str
    rainy_season: str
    humidity: str
    packing_suggestions: List[str]
    weather_alerts: str
    climate_type: str
    travel_tips: List[str]

class Hotel(BaseModel):
    name: str
    price_range: str
    rating: float
    amenities: List[str]
    location: str

class Accommodation(BaseModel):
    budget: Hotel
    mid_range: Hotel
    luxury: Hotel

class DailyItinerary(BaseModel):
    day: int
    activities: List[str]
    meals: List[str]
    accommodation: str

class Itinerary(BaseModel):
    three_days: List[DailyItinerary]
    five_days: List[DailyItinerary]
    seven_days: List[DailyItinerary]
    tips: List[str]

class TravelPlan(BaseModel):
    destination: str
    places: List[Place] = []
    weather: Optional[WeatherInfo] = None
    accommodation: Optional[Accommodation] = None
    itinerary: Optional[Itinerary] = None
    # Add other fields as needed
