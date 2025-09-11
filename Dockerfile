# --------------------------
# FRONTEND BUILD STAGE
# --------------------------
FROM node:20-slim as frontend-builder

# Set working dir
WORKDIR /app/frontend

# Install dependencies
COPY frontend/package*.json ./
RUN npm install --frozen-lockfile

# Copy source and build
COPY frontend/ ./
RUN npm run build


# --------------------------
# BACKEND STAGE
# --------------------------
FROM python:3.11-slim as backend

# Set working dir
WORKDIR /app

# Install system deps for psycopg2 & build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Copy built frontend into Django static dir
COPY --from=frontend-builder /app/frontend/dist ./frontend_dist/

# Collect static files (so Django can serve them)
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start Gunicorn + Daphne (for HTTP + WebSockets)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "backend.asgi:application"]
