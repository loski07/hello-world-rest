import datetime
from fastapi.encoders import jsonable_encoder

from fastapi.testclient import TestClient
from hello_world_rest.api.rest_api import app
import mongomock
import pytest
from fastapi import status
import json


@pytest.fixture
def test_client() -> TestClient:
    app.mongodb_client = mongomock.MongoClient()
    app.database = app.mongodb_client.birthdates
    return TestClient(app)


@pytest.fixture
def test_client_with_data(test_client: TestClient) -> TestClient:
    test_client.app.database.users.insert_one({"user": "test_user", "dateOfBirth": "2000-01-30"})
    return test_client


def test_is_alive(test_client: TestClient):
    response = test_client.get("/isAlive")
    assert response.status_code == status.HTTP_200_OK


def test_get_helloworld_no_user_registered(test_client: TestClient):
    response = test_client.get('/hello/empty_user')
    assert response.status_code == status.HTTP_200_OK
    assert json.dumps(response.json()) == '{"message": "Hello, empty_user! Your birthdate is not yet in the system"}'


def test_get_helloworld_user_registered(test_client: TestClient):
    test_client.app.database.users.insert_one({"user": "test_user", "dateOfBirth": "2000-01-30"})
    response = test_client.get('/hello/test_user')
    assert response.status_code == status.HTTP_200_OK
    assert '{"message": "Hello, test_user! Your birthday is in' in json.dumps(response.json())


def test_get_helloworld_user_registered_birthday_today(test_client: TestClient):
    todays_day = datetime.date.today().day
    todays_month = datetime.date.today().month
    test_client.app.database.users.insert_one({"user": "test_user", "dateOfBirth": f"2000-{todays_month}-{todays_day}"})
    response = test_client.get('/hello/test_user')
    assert response.status_code == status.HTTP_200_OK
    assert json.dumps(response.json()) == '{"message": "Hello, test_user! Happy birthday!"}'


def test_put_valid_user_empty(test_client):
    response = test_client.put('hello/test_user', json={"user": "test_user", "dateOfBirth": "2000-01-30"})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    record = test_client.app.database.users.find_one(jsonable_encoder({"user": "test_user"}))
    assert "user" in record
    assert "dateOfBirth" in record
    assert {"user": record["user"], "dateOfBirth": record["dateOfBirth"]} == {"user": "test_user", "dateOfBirth": "2000-01-30"}


def test_put_valid_user_update(test_client):
    test_client.app.database.users.insert_one({"user": "test_user", "dateOfBirth": "2000-01-30"})
    response = test_client.put('hello/test_user', json={"user": "test_user", "dateOfBirth": "2001-01-30"})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    record = test_client.app.database.users.find_one(jsonable_encoder({"user": "test_user"}))
    assert "user" in record
    assert "dateOfBirth" in record
    assert {"user": record["user"], "dateOfBirth": record["dateOfBirth"]} == {"user": "test_user", "dateOfBirth": "2001-01-30"}


def test_put_invalid_user(test_client):
    response = test_client.put('hello/test_user', json={"user": "test_user", "dateOfBirth": "20000130"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "is not a valid date" in response.text
