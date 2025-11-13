from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = sociallogin.user

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        if first_name and last_name:
            user.name = f"{first_name} {last_name}"
        elif first_name:
            user.name = first_name

        user.is_active = False

        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Sobrescrevemos este método para salvar o Usuário (Person) ANTES
        de salvar o SocialLogin (SocialAccount).

        Isso corrige o bug onde o 'user' (Foreign Key) ficava nulo.
        """
        user = sociallogin.user
        user.set_unusable_password()

        # 1. Salva o Usuário (Person) PRIMEIRO.
        #    Isso garante que ele tenha um 'pk' (ID).
        user.save()

        # 2. Salva o SocialLogin (SocialAccount) DEPOIS.
        #    Agora, 'sociallogin.save()' verá que 'user.pk' existe
        #    e fará o link corretamente no banco de dados.
        sociallogin.save(request)

        return user