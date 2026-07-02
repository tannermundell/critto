# Mock inference API — container image.
# The real GPU server will reuse this same structure (swap the model code in).
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app and the species CSV (place a copy of sa_species_list.csv in this
# folder before building — see README). The app also falls back gracefully if missing.
COPY . .

ENV SPECIES_CSV=/app/sa_species_list.csv
EXPOSE 8000

# Use $PORT if the host provides one (e.g. Render), else default to 8000 (local).
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
