# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Install system dependencies for Tkinter and Pygame
# These are necessary for GUI applications and audio to work in a Linux environment
RUN apt-get update && apt-get install -y \
    python3-tk \
    libsdl2-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-ttf-2.0-0 \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Set a default display environment variable
# Note: For GUI apps to work, you usually need to map your host's X11 socket
# or use a tool like Xming/VcXsrv on Windows.
ENV DISPLAY=:0

# Command to run the application (Version 3)
CMD ["python", "Slot-machine version 3/Slot_Machine_v3.py"]
