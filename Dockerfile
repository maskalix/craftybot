# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot script
COPY bot.py /app/

# Set environment variables (loaded from .env)
ENV BOT_TOKEN=""
ENV CRAFTY_API_BASE_URL=""
ENV CRAFTY_API_KEY=""
ENV CRAFTY_SERVER_ID=""

# Run the bot
CMD ["python", "bot.py"]
