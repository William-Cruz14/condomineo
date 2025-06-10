from unfold.forms import UserCreationForm as UnfoldUserCreationForm
from .models import Profile

class CustomUserCreationForm(UnfoldUserCreationForm):
    class Meta:
        model = Profile
        fields = ('email', 'name')
