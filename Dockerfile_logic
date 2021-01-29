FROM python:3

WORKDIR /


COPY . ./backend
RUN pip install -r backend/logic/requirements_logic.txt

ENV PYTHONPATH /


WORKDIR /backend/logic



CMD ["python3","app.py"]
