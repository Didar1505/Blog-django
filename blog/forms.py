from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from . import models
from django_ckeditor_5.widgets import CKEditor5Widget

class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comment here...', 'class': 'form-control'}),
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ['profile_picture', 'bio', 'website', 'social_twitter', 'location']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class CreatePostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Advanced UI: Adding Bootstrap classes to all fields automatically
        for field in self.fields:
            if field != 'body': # Don't add form-control to body, CKEditor handles its own styling
                self.fields[field].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = models.Post
        fields = ['categories', 'title', 'body', 'featured_image', 'status']
        widgets = {
            # This is the critical line to make the editor appear
            "body": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            )
        }