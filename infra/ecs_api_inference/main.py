from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class SensorData(BaseModel):
    date: str
    temperature: float
    humidity: float
    light: int
    co2: float
    humidity_ratio: float


class SensorDataWithOccupancy(SensorData):
    inferred_occupancy: int


@app.post("/sensor_data/", response_model=SensorDataWithOccupancy)
async def create_sensor_data(sensor_data: SensorData):
    # Here, we're just adding a dummy "inferred_occupancy" for the sake of example.
    # In a real application, you'd likely use some kind of model to infer this value based on the input data.
    return SensorDataWithOccupancy(**sensor_data.dict(), inferred_occupancy=0)
