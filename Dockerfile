# syntax=docker/dockerfile:1

FROM python:3.13

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Install x11-apps for x11 forwarding
RUN apt-get update && apt-get install -y \
    x11-apps \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m pip install scikit-build==0.18.1

# Install other dependencies.
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD ["python", "main.py"]
