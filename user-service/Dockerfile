FROM python:3.10-slim

WORKDIR /app

# Copier requirements d'abord (optimisation cache)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du projet
COPY . .

EXPOSE 5001

CMD ["python", "run.py"]