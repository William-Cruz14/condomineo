FROM python:3.11-slim

LABEL authors="william"

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Expõe a porta usada pelo Gunicorn
EXPOSE 8000

# Comando de inicialização com Gunicorn
CMD ["sh", "-c", "\
    python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn condomineo.wsgi:application --bind 0.0.0.0:8000\
    "]
