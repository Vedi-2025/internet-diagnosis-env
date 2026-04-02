# ─────────────────────────────────────────────
# What is this file?
# A Dockerfile is like a recipe that tells Docker
# how to package your entire project into a
# container — a self-contained box that runs
# anywhere, on any computer, without any setup.
# ─────────────────────────────────────────────

# Start with a Python base image
# Think of this as "start with a computer that
# already has Python installed"
FROM python:3.12-slim

# Set the working directory inside the container
# All our files will live here
WORKDIR /app

# Copy requirements first (for faster rebuilds)
COPY requirements.txt .

# Install all Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Tell Docker this container uses port 7860
# HuggingFace Spaces specifically needs port 7860
EXPOSE 7860

# The command that runs when container starts
# This starts your FastAPI server
CMD ["python", "server.py"]