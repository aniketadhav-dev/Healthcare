# Base Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the backend requirements file first (for better caching)
COPY backend/requirements.txt ./backend/

# Install backend dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the rest of the project files into the container
COPY . .

# Expose the ports for Backend (8000) and Frontend (3000)
EXPOSE 8000 3000

# Run bot.py when the container starts
CMD ["python", "bot.py"]
