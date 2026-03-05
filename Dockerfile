#1. Lightweight Python base image
from python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the dependencies file and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy script and the dataset into the container
COPY producer.py .
COPY faa_sdr_data.xls .

# 5. Command to run when the container starts
CMD ["python", "-u", "producer.py"]
