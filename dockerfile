FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install .

COPY . .

EXPOSE 5000

CMD [ "sh", "-c", "python3 -m gunicorn -w 4 webapp.app:prod --bind 0.0.0.0:5000" ]
