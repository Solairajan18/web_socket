FROM amazonlinux:2

# Set working directory
WORKDIR /app

# Install system dependencies and Python
RUN yum update -y && \
    yum groupinstall "Development Tools" -y && \
    yum install -y \
    python3.11 \
    python3.11-devel \
    python3-pip \
    cmake \
    gcc \
    gcc-c++ \
    make \
    git \
    curl \
    openssl-devel \
    && yum clean all

# Install Rust (needed for some Python packages)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Set Python 3.11 as default
RUN alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    alternatives --set python3 /usr/bin/python3.11

# Copy requirements first for better cache usage
COPY requirements.txt .

# Upgrade pip and install requirements
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port
ENV PORT=8000
EXPOSE 8000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Command to run the application
CMD ["sh", "-c", "python3 -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]