FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=regluit.settings.docker

WORKDIR /opt/regluit

# System deps for mysqlclient, Pillow, lxml, cairocffi, libsass
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    default-libmysqlclient-dev \
    pkg-config \
    libjpeg-dev \
    libxml2-dev \
    libxslt1-dev \
    libcairo2-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install git-based editable deps to /usr/local/src (not the workdir which gets volume-mounted)
RUN pip install --no-cache-dir --src /usr/local/src -r requirements.txt && \
    pip install --no-cache-dir libsass

COPY . .

# Add project parent to Python path so `import regluit` resolves
ENV PYTHONPATH=/opt

# Create directories
RUN mkdir -p logs /var/www/static

# Copy dummy keys so settings can load
RUN cp -r settings/dummy settings/keys 2>/dev/null || true

# Collect static files
RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
