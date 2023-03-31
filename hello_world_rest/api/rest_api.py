import datetime
import os

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, validator
from pymongo import MongoClient
import logging

app = FastAPI()
logging.basicConfig(
    format='%(asctime)s | %(levelname)s: %(message)s',
    level=getattr(logging, os.environ.get('LOG_LEVEL', 'INFO'))
)
LOGGER = logging.getLogger()


@app.on_event("startup")
def startup_db_client() -> None:
    """
    Initializes the database components
    """
    app.mongodb_client = MongoClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017/hello_world_rest_db"))
    app.database = app.mongodb_client.birthdates
    LOGGER.debug("Connected to the MongoDB database!")


@app.on_event("shutdown")
def shutdown_db_client() -> None:
    """
    Closes the database client
    """
    app.mongodb_client.close()


class UserData(BaseModel):
    """
    User input data used in the PUT endpoint
    """
    dateOfBirth: str

    @validator('dateOfBirth')
    def name_must_contain_space(cls, v):
        """
        Validates the 'dateOfBirth' so it is older than today
        :param v: object to validate
        :return: validated object
        """
        today = datetime.date.today()
        try:
            parsed_v = datetime.datetime.strptime(v, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError(f"{v} is not a valid date")
        if parsed_v > today:
            raise ValueError("You were not born yet! really?")
        return v

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "dateOfBirth": "2023-03-25"
            }
        }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Captures the validation exception modifying the message shown to the caller
    :param request: request received
    :param exc: exception raised during the validation
    :return: JSON response with the error message
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.get(
    "/hello/{username}",
    response_description="Greets the users congratulating it if today is its birthday, if not, counts days till then",
    status_code=status.HTTP_200_OK
)
def get_helloword(username: str) -> dict:
    """
    Rest endpoint that greets the user. It congratulates the user if today is the birthday, if not counts how long till
    the day
    :param username: Name of the user to greet
    :return: HTTP response containing the greetings and the status code
    """
    LOGGER.debug(f"Received GET request for user {username}")
    today = datetime.date.today()

    record = app.database.users.find_one(jsonable_encoder({"user": username}))
    if not record:
        return {"message": f"Hello, {username}! Your birthdate is not yet in the system"}
    birth_date = datetime.datetime.strptime(record["dateOfBirth"], '%Y-%m-%d')
    if today.day == birth_date.date().day and today.month == birth_date.date().month:
        return {"message": f"Hello, {username}! Happy birthday!"}
    else:
        next_birthday = datetime.datetime.strptime(
            f"{today.year.real + 1}-{birth_date.month.real}-{birth_date.day.real}", '%Y-%m-%d')

        days = (next_birthday.date() - today) / datetime.timedelta(days=1)
        return {"message": f"Hello, {username}! Your birthday is in {int(days)} day(s)"}


@app.put(
    "/hello/{username}",
    response_description="Stores the birthdate of the user",
    status_code=status.HTTP_204_NO_CONTENT)
def put_birthdate(username: str, user_data: UserData) -> Response:
    """
    Rest endpoint that stores the birthdate of the user
    :param username: Name of the user whose birthdate we should store
    :param user_data: json data passed to the rest call
    :return: HTTP response containing the NO_CONTENT status code
    """
    LOGGER.debug(f"Received PUT request for user {username} with data: {user_data}")
    try:
        datetime.datetime.strptime(user_data.dateOfBirth, '%Y-%m-%d')
        record = app.database.users.find_one(jsonable_encoder({"user": username}))
        if not record:
            app.database.users.insert_one({"user": username, "dateOfBirth": user_data.dateOfBirth})
        else:
            app.database.users.find_one_and_replace(
                jsonable_encoder({"user": username}),
                jsonable_encoder({"user": username, "dateOfBirth": user_data.dateOfBirth}))
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": f"{user_data.dateOfBirth} is not a valid date", "detail": e})


@app.get("/isAlive", response_description="Is alive endpoint for health checks", status_code=status.HTTP_200_OK)
def is_alive():
    LOGGER.debug(f"Received GET request for isAlive")
    return


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("LISTENING_PORT", "8000")))
