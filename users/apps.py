from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    def ready(self):
        pass
        # Importando os sinais para garantir que sejam registrados
        import users.signals
