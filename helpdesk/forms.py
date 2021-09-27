from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from helpdesk.models import User, WishList, Comment


class UserCreation(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', )


class WishCreated(ModelForm):
    class Meta:
        model = WishList
        fields = ('text', 'title', 'importance')


class CommentCreated(ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )


class WishUpdateForm(ModelForm):
    class Meta:
        model = WishList
        fields = ('text', 'importance')
