FROM python:3-alpine3.11
ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app
ADD hello_world_rest /app/
RUN pip install -e /app
EXPOSE 8000
CMD [ "python", "/app/api/rest_api.py" ]
