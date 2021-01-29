FROM python:3 

WORKDIR /


COPY . ./backend
RUN pip install --upgrade pip
RUN pip install -r /backend/requirements_logic.txt

ENV PYTHONPATH /


WORKDIR /backend/logic



CMD ["python3","app.py"]
