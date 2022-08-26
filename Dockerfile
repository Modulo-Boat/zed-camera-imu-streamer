FROM stereolabs/zed:3.7-py-runtime-jetson-jp4.6.1

WORKDIR /app

RUN python3 -m pip install --upgrade pip setuptools

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt


COPY templates/ templates/
COPY metrics.py .
COPY camera.py .
COPY app.py .

EXPOSE 5000
EXPOSE 9090

CMD ["python3", "app.py"]