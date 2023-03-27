FROM python:3-alpine3.11
ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app
ADD hello_world_rest /app/
RUN pip install --upgrade pip && pip install -e .
EXPOSE 8000
CMD [ "gunicorn", "wsgi:app", "-w", "6", "--bind", "0.0.0.0:8000" ]
