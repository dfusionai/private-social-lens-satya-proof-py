FROM python:3.11-slim

WORKDIR /app

COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN python initialize_models.py

CMD ["python", "-m", "psl_proof"]
