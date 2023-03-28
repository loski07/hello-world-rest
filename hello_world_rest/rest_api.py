import datetime
import json
import os
import uvicorn
import motor.motor_asyncio
from fastapi import FastAPI
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()
db_client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/birthdates"))
db = db_client.birthdates


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    app.database = app.mongodb_client["birthdates"]
    print("Connected to the MongoDB database!")


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


class UserData(BaseModel):
    dateOfBirth: str

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "dateOfBirth": "2023-03-25"
            }
        }


@app.get(
    "/hello/{username}",
    response_description="Greets the users congratulating it if today is its birthday, if not, counts days till then",
    status_code=status.HTTP_200_OK
)
def get_helloword(username: str) -> Response:
    """
    Rest endpoint that greets the user. It congratulates the user if today is the birthday, if not counts how long till
    the day
    :param username: Name of the user to greet
    :return: HTTP response containing the greetings and the status code
    """
    today = datetime.date.today()
    record = db["users"].find_one({"user": username})
    birth_date = datetime.datetime.strptime(record["dateOfBirth"], '%Y-%m-%d')
    if today == birth_date.date():
        return Response(content={"message": f"Hello, {username}! Happy birthday!"},
                        status_code=status.HTTP_200_OK,
                        media_type='application/json')
    else:
        if today > birth_date.date():
            next_birthday = datetime.datetime.strptime(
                f"{birth_date.year.real + 1}-{birth_date.month.real}-{birth_date.day.real}", '%Y-%m-%d')
        else:
            next_birthday = datetime.datetime.strptime(
                f"{birth_date.year.real}-{birth_date.month.real}-{birth_date.day.real}", '%Y-%m-%d')
        days = (next_birthday.date() - today) / datetime.timedelta(days=1)
        return Response(content={"message": f"Hello, {username}! Your birthday is in {int(days)} day(s)"},
                        status_code=status.HTTP_200_OK,
                        media_type='application/json')


@app.put(
    "/hello/{username}",
    response_description="Stores the birthdate of the user",
    status_code=status.HTTP_204_NO_CONTENT)
def put_birthdate(username: str, user_data: UserData) -> Response:
    """
    Rest endpoint that stores the birthdate of the user.
    :param username: Name of the user whose birthdate we should store
    :param user_data: json data passed to the rest call
    :return: HTTP response containing the NO_CONTENT status code
    """
    try:
        datetime.datetime.strptime(user_data.dateOfBirth, '%Y-%m-%d')
        db["users"].find_one_and_replace({"user": username}, {"user": username, "dateOfBirth": user_data.dateOfBirth})
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": f"{user_data.dateOfBirth} is not a valid date", "detail": e})


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
