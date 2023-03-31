# HelloWorld REST API

## Abstract
Python application that implements a rest api exposing 3 endpoints:
- Greet the user
- Set the user's birthdate
- Is Alive

## Description
### Greet the user 
Returns hello birthday message for the given user
Request: `Get /hello/<username>`
Response: `200 OK`
Response Examples:
- If the birthdate of the user is not yet in the system:
```json
{"message": "Hello, {username}! Your birthdate is not yet in the system"}
```
- If username’s birthday is in N days:
```json
{ "message": "Hello, {username}! Your birthday is in N day(s)" }
```
- If username’s birthday is today:
```json
{ "message": "Hello, {username}! Happy birthday!" }
```

### Set the user's birthdate
Saves/updates the given user’s name and date of birth in the database.
Request: `PUT /hello/<username> { "dateOfBirth": "YYYY-MM-DD" }`
Response: `204 No Content`


### Is Alive
Is alive endpoint for health checks
Request: `Get /isAlive`
Response: `200 OK`

## Building the app
The application can be installed in any virtual environment following the steps:
```shell
# optionally you can set the following env vars if you don't want to use the on-default values
# export MONGODB_URL="mongodb://database:27017/hello_world_rest_db"
# export LISTENING_PORT="8000"
pip install -r requirements.txt
python api/rest_api.py
```
We also provide a Dockerfile that encapsulates all the operations for you
