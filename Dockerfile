# --------------------------
# FRONTEND BUILD STAGE
# --------------------------
FROM node:20-slim as frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install --frozen-lockfile

COPY frontend/ ./
RUN npm run build


# --------------------------
# BACKEND STAGE
# --------------------------
FROM python:3.11-slim as backend

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./

# Copy built frontend into Django static dir
COPY --from=frontend-builder /app/frontend/dist ./frontend_dist/

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# ✅ FIXED: Use PORT env variable (Render requires this)
CMD sh -c "daphne -b 0.0.0.0 -p ${PORT:-8000} project.asgi:application"
