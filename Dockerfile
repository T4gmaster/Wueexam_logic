FROM python:3.9-alpine

WORKDIR /


COPY . ./backend
RUN pip install -r backend/requirements_logic.txt

ENV PYTHONPATH /


WORKDIR /backend/logic



CMD ["python3","app.py"]
