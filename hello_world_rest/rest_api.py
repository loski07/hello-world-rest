import datetime
import json
from http import HTTPStatus

from flask import Flask, Response, request
from flask_pymongo import PyMongo


def create_app():
    rest_app = Flask(__name__)
    rest_app.config["MONGO_URI"] = "mongodb://localhost:27017/clients"
    return rest_app


app = create_app()
mongo = PyMongo(app)
users = mongo.db.users


@app.route('/hello/<username>')
def get_helloword(username: str) -> Response:
    """
    Rest endpoint that greets the user. It congratulates the user if today is the birthday, if not counts how long till
    the day
    :param username: Name of the user to greet
    :return: HTTP response containing the greetings and the status code
    """
    today = datetime.date.today()
    record = users.find_one({"user": username})
    birth_date = datetime.datetime.strptime(record["dateOfBirth"], '%Y-%m-%d')
    if today == birth_date.date():
        return app.response_class(
            response=json.dumps({"message": f"Hello, {username}! Happy birthday!"}),
            status=HTTPStatus.OK,
            mimetype='application/json')
    else:
        next_birthday = None
        if today > birth_date.date():
            next_birthday = datetime.datetime.strptime(
                f"{birth_date.year.real + 1}-{birth_date.month.real}-{birth_date.day.real}", '%Y-%m-%d')
        else:
            next_birthday = datetime.datetime.strptime(
                f"{birth_date.year.real}-{birth_date.month.real}-{birth_date.day.real}", '%Y-%m-%d')
        days = (next_birthday.date() - today) / datetime.timedelta(days=1)
        return app.response_class(
            response=json.dumps(
                {"message": f"Hello, {username}! Your birthday is in {int(days)} day(s)"}),
            status=HTTPStatus.OK,
            mimetype='application/json')


@app.route('/hello/<username>', methods=['PUT'])
def put_birthdate(username: str) -> Response:
    """
    Rest endpoint that stores the birthdate of the user
    :param username: Name of the user whose birthdate we should store
    :return: HTTP response containing the NO_CONTENT status code
    """
    aux_dict = request.get_json()
    if 'dateOfBirth' in aux_dict:
        birth_date_str = aux_dict['dateOfBirth']
        try:
            birth_date = datetime.datetime.strptime(birth_date_str, '%Y-%m-%d')
            # users.insert_one({"user": username, "dateOfBirth": birth_date_str})
            users.find_one_and_replace({"user": username}, {"user": username, "dateOfBirth": birth_date_str})
            return app.response_class(status=HTTPStatus.NO_CONTENT)
        except ValueError as e:
            return app.response_class(
                response=json.dumps({"message": f"{birth_date_str} is not a valid date", "detail": e}),
                status=HTTPStatus.BAD_REQUEST,
                mimetype='application/json')


if __name__ == '__main__':
    app.run()
