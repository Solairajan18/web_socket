FROM chromadb/chroma:1.0.21.dev53

# Set working directory
WORKDIR /app

# Check for existing Python installation
RUN echo "=== Checking for Python installations ===" && \
    echo "\nTesting 'python3' command:" && \
    if command -v python3; then \
        python3 --version; \
    else \
        echo "python3 not found"; \
    fi && \
    echo "\nTesting 'python' command:" && \
    if command -v python; then \
        python --version; \
    else \
        echo "python not found"; \
    fi && \
    echo "\nTesting 'py' command:" && \
    if command -v py; then \
        py --version; \
    else \
        echo "py not found"; \
    fi && \
    echo "\nTesting pip installations:" && \
    echo "\nTesting 'pip3' command:" && \
    if command -v pip3; then \
        pip3 --version; \
    else \
        echo "pip3 not found"; \
    fi && \
    echo "\nTesting 'pip' command:" && \
    if command -v pip; then \
        pip --version; \
    else \
        echo "pip not found"; \
    fi && \
    echo "\nChecking Python path:" && \
    which python3 || which python || which py && \
    echo "\nChecking Python packages location:" && \
    python3 -c "import sys; print('Python packages location:', sys.path)" || \
    python -c "import sys; print('Python packages location:', sys.path)" && \
    echo "\n=== Python check complete ===" && \
    # Ensure at least one Python version is available
    (command -v python3 || command -v python || command -v py || (echo "No Python installation found" && exit 1))
# Verify Python packages and dependencies
RUN python3 -m pip install --upgrade pip
RUN python3 --version && \
    python3 -m pip --version

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