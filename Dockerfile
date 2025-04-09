FROM python:3.11-slim

WORKDIR /app

COPY . /app

# Install any needed packages specified in requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt

# RL: Update 2025/04/09
# Install system dependencies for building Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python build tool
RUN pip install --upgrade pip setuptools wheel

# Install requirements, forcing source build for pybloom_live
RUN pip install --no-cache-dir --no-binary pybloom_live -r requirements.txt
# RL: Update 2025/04/09

CMD ["python", "-m", "psl_proof"]
