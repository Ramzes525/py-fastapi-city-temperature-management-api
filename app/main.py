from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends

from app.database import SessionLocal, engine
from app.models import Base, City, Temperature
from app.schemas import CityCreate, CityOut
from app.schemas import TemperatureCreate, TemperatureOut


Base.metadata.create_all(bind=engine)


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/cities/", response_model=CityOut)
def create_city(city: CityCreate, db: Session = Depends(get_db)):
    db_city = City(
        name=city.name, additional_info=city.additional_info
        )
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city


@app.get("/cities/", response_model=list[CityOut])
def read_cities(
    skip: int=0, limit: int=10, db: Session = Depends(get_db)
    ):
    cities = db.query(City).offset(skip).limit(limit).all()
    return cities


@app.put("/cities/{city_id}", response_model=CityOut)
def update_city(
    city_id: int, city: CityCreate, db: Session = Depends(get_db)
    ):
    db_city = db.query(City).filter(City.id == city_id).first()
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    db_city.name = city.name
    db_city.additional_info = city.additional_info
    db.commit()
    db.refresh(db_city)
    return db_city


@app.delete("/cities/{city_id}", response_model=dict)
def delete_city(city_id: int, db: Session = Depends(get_db)):
    db_city = db.query(City).filter(City.id == city_id).first()

    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    db.delete(db_city)
    db.commit()
    return {"detail": "City deleted"}


@app.post("/temperatures/update/", response_model=list[TemperatureOut])
async def update_temperature(
    fake_temp: float = 25, db: Session = Depends(get_db)
    ):
    cities = db.query(City).all()
    temperatures = []

    for city in cities:
        temp_record = Temperature(city_id=city.id, temperature=fake_temp)
        db.add(temp_record)
        temperatures.append(temp_record)
    db.commit()
    return temperatures


@app.post("/temperatures/", response_model=TemperatureOut)
def create_temperature(
    temperature: TemperatureCreate, db: Session = Depends(get_db)
    ):
    db_temperature = Temperature(
        city_id=temperature.city_id, temperature=temperature.temperature
        )
    db.add(db_temperature)
    db.commit()
    db.refresh(db_temperature)
    return db_temperature


@app.get("/temperatures/?city_id=city_id", response_model=list[TemperatureOut])
def read_city_temperatures(city_id: int, db: Session = Depends(get_db)):
    temperatures = db.query(Temperature).filter(
        Temperature.city_id == city_id
        ).all()

    if not temperatures:
        raise HTTPException(status_code=404, detail="No temperature record found for this city")
    return temperatures
