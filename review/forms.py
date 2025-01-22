from django import forms
from .models import Ticket, Review, UserFollows
from django.contrib.auth import get_user_model


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["title", "description", "image"]
        labels = {
            "title": "Titre",
            "description": "Description",
            "image": "Image",
        }


class PostReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["headline", "rating", "body"]
        labels = {
            "headline": "Titre",
            "rating": "Note",
            "body": "Commentaire",
        }
        widgets = {
            "rating": forms.RadioSelect(
                choices=[(0, "0"), (1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")]
            )
        }


class PostReviewAndTicketForm(forms.Form):
    """Formulaire pour créer simultanément un ticket et une critique."""

    # Champs pour le ticket
    title = forms.CharField(
        max_length=128,
        label="Titre",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    description = forms.CharField(
        max_length=2048,
        label="Description",
        widget=forms.Textarea(attrs={"class": "form-control"}),
    )
    image = forms.ImageField(
        label="Image",
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
    )

    # Champs pour la critique
    rating = forms.ChoiceField(
        choices=[(0, "0"), (1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
        label="Note",
        widget=forms.RadioSelect(),
    )
    headline = forms.CharField(
        max_length=128,
        label="Titre de la critique",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    body = forms.CharField(
        max_length=8192,
        label="Commentaire",
        widget=forms.Textarea(attrs={"class": "form-control"}),
    )


class FollowUsersForm(forms.ModelForm):
    class Meta:
        model = UserFollows
        fields = ["followed_user"]
        labels = {
            "followed_user": "Utilisateur à suivre",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["followed_user"].queryset = get_user_model().objects.exclude(
            id=self.user.id
        )
