# Estágio de build
FROM python:3.11-slim

LABEL authors="william"

# Working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Expose the server port
EXPOSE 8000

# Command to start the server

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "condomineo.wsgi"]