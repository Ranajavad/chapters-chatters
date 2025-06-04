
from django import forms
from .models import Review, Comment, Book, BookClubGroup,DiscussionPost,Comment, Schedule, Suggestion
from django.contrib.auth.models import User


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import BookClubGroup, Suggestion, MeetingPollOption

class BookClubGroupForm(forms.ModelForm):
    class Meta:
        model = BookClubGroup
        fields = ['name', 'description', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Name of Club'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe the prupose of group...'
            }),
        }


class BookForm(forms.ModelForm):
    class Meta:
        model =Book
        fields = ['title', 'author', 'description', 'group', 'cover_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'author': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea'}),
            'group': forms.Select(attrs={'class': 'form-select'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }


class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['title', 'author', 'group','book_cover']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'author': forms.TextInput(attrs={'class': 'form-input'}),
            'group': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['group'].queryset = BookClubGroup.objects.filter(members=user)



class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput()
    )
    text = forms.CharField(
        label='Review',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    class Meta:
        model = Review
        fields = ['rating', 'text']


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label='Comment',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )

    class Meta:
        model = Comment
        fields = ['content']

class InvitationForm(forms.Form):  
    email = forms.EmailField(
        required=False,
        label='Invitee Email Address',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'})
    )
    username = forms.CharField(
        required=False,
        label='Or Username',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'})
    )
    group = forms.ModelChoiceField(
        queryset=None,
        label='Invite to Group',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['group'].queryset = BookClubGroup.objects.filter(members=user)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')

     
        if not email and not username:
            raise forms.ValidationError("You must provide either an email or a username.")

        
        if username and not email:
            try:
                user = User.objects.get(username=username)
                cleaned_data['email'] = user.email
            except User.DoesNotExist:
                raise forms.ValidationError(f"No user found with username '{username}'.")

        return cleaned_data


class DiscussionPostForm(forms.ModelForm):
    class Meta:
        model = DiscussionPost
        fields = ['title', 'content']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['title', 'description', 'date', 'time', 'location']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)

class EditBookClubGroupForm(forms.ModelForm):
    class Meta:
        model = BookClubGroup
        fields = ['name', 'description']

class MeetingPollOptionForm(forms.ModelForm):
    class Meta:
        model = MeetingPollOption
        fields = ['date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }