# Use a base image of Python 3.11 in its "slim" version
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file (requirements.txt) to the working directory
COPY requirements.txt .

# Install the application's dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application content to the working directory
COPY . .

# Run the bot's main script
CMD ["python", "telegram.py"]
