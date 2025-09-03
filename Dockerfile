FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and C++ tools
RUN apt-get update --fix-missing && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    cmake \
    gcc \
    g++ \
    git \
    curl \
    libssl-dev \
    pkg-config \
    libtool \
    autoconf \
    automake \
    python3-dev \
    libstdc++-9-dev \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (needed for some Python packages)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

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