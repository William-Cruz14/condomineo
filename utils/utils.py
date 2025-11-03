from django.core.mail import send_mail
from django.template.loader import render_to_string
from decouple import config


def send_custom_email(subject, template_name, context, recipient_list):
    """
    Função reutilizável para enviar e-mails formatados com templates HTML.

    :param subject: Assunto do e-mail.
    :param template_name: Caminho do arquivo de template HTML.
    :param context: Dicionário de contexto para renderizar no template.
    :param recipient_list: Lista de e-mails dos destinatários.
    """
    try:
        # Renderiza a mensagem HTML a partir de um template
        html_message = render_to_string(template_name, context)

        # Mensagem de texto simples como fallback
        plain_message = "Este e-mail requer um cliente com suporte a HTML."

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=config('EMAIL_HOST_USER'),
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False  # Mantenha False para ver erros durante o desenvolvimento
        )
        print(f"E-mail enviado com sucesso para: {recipient_list}")
    except Exception as e:
        # Em um ambiente de produção, você pode querer logar este erro
        print(f"Erro ao enviar e-mail: {e}")
