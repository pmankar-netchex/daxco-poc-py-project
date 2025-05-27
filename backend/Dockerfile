FROM python:3.10-slim-bullseye
# or
FROM ubuntu:20.04

WORKDIR /app

# Set environment variable to indicate Docker environment
ENV DOCKER_CONTAINER=true

# Install system dependencies and Microsoft ODBC Driver 17
RUN apt-get update && apt-get install -y --no-install-recommends \
    unixodbc \
    unixodbc-dev \
    gnupg \
    curl \
    locales \
    tdsodbc \
    freetds-bin \
    freetds-dev \
    libodbc1 \
    odbcinst \
    apt-transport-https \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Add Microsoft repository and install ODBC Driver 17 using modern GPG approach
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

# Configure FreeTDS as fallback in odbcinst.ini
RUN echo "\n[FreeTDS]\nDescription=FreeTDS Driver\nDriver=/usr/lib/$(uname -m)-linux-gnu/odbc/libtdsodbc.so\nUsageCount=1" >> /etc/odbcinst.ini \
    && echo "[global]\ntds version = 7.3\nclient charset = UTF-8\ntext size = 20971520" > /etc/freetds/freetds.conf

# Install Python requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Security configuration
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]