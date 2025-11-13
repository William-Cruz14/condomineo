import requests
from django.conf import settings


def verificar_recaptcha(recaptcha_token):
    """
    Envia o token do reCAPTCHA para o Google para verificação.
    """
    if not recaptcha_token:
        return False, "Token não fornecido."

    # URL de verificação do Google
    url = 'https://www.google.com/recaptcha/api/siteverify'

    # Dados que enviaremos ao Google
    data = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,  # Nossa Chave Secreta
        'response': recaptcha_token  # O token do frontend
    }

    try:
        # Fazendo a requisição POST
        response = requests.post(url, data=data)
        result = response.json()

        # O Google responde com 'success': true ou false
        if result.get('success'):
            return True, "reCAPTCHA verificado com sucesso."
        else:
            # Retorna os códigos de erro se houver
            error_codes = result.get('error-codes', [])
            return False, f"Falha na verificação: {error_codes}"

    except requests.RequestException as e:
        # Lidar com erros de rede
        return False, f"Erro ao contatar o serviço reCAPTCHA: {e}"