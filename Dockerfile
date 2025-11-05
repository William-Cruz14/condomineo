# Estágio de build
FROM python:3.11-slim

# Metadados do mantenedor
LABEL authors="william"

# Define o diretório de trabalho
WORKDIR /app

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos do projeto
COPY . .
# Expõe a porta 8000
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]