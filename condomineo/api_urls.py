from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularSwaggerView,
    SpectacularRedocView
)
from dj_rest_auth.views import (
    LoginView, LogoutView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView
)

from users.views import GoogleLogin
urlpatterns = [
    # Schema OpenAPI
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Redoc UI
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('auth/login/', LoginView.as_view(), name='rest_login'),
    path('auth/logout/', LogoutView.as_view(), name='rest_logout'),
    path('auth/google/', GoogleLogin.as_view(), name='google_login'),
# --- ADICIONE ESTA LINHA ---
    # Isso "silencia" o erro NoReverseMatch ao registrar as views
    # padrão do allauth (mesmo que não as usemos).
    path('accounts/', include('allauth.urls')),
    path('auth/password/change/', PasswordChangeView.as_view(), name='rest_password_change'),
    path('auth/password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('auth/password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('core/', include('core.urls')),
    path('users/', include('users.urls')),
]