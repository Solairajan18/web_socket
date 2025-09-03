FROM chromadb/chroma:1.0.21.dev53

# Set working directory
WORKDIR /app

# Show Python version and location
RUN python3 --version && \
    which python3 && \
    pip3 --version

# The chromadb image already includes all necessary dependencies
# and has Python with required C++ libraries installed

# Copy requirements first for better cache usage
COPY requirements.txt .

# Upgrade pip and install requirements
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables for Render
ENV PORT=10000
EXPOSE $PORT

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Command to run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT