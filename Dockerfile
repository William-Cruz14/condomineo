# Estágio de build
FROM python:3.11-slim

LABEL authors="william"

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instala dependências do sistema (úteis para compilar uWSGI)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Expõe a porta usada pelo uWSGI
EXPOSE 8000

# Comando de inicialização
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && uwsgi --ini uwsgi.ini"]
