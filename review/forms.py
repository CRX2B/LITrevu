from django import forms
from .models import Ticket, Review, UserFollows
from authentication.models import User


class TicketForm(forms.ModelForm):
    edit_ticket = forms.BooleanField(
        widget=forms.HiddenInput, initial=True, required=False
    )

    class Meta:
        model = Ticket
        fields = ["title", "description", "image"]


class PostReviewForm(forms.ModelForm):
    edit_review = forms.BooleanField(
        widget=forms.HiddenInput, initial=True, required=False
    )

    class Meta:
        model = Review
        fields = ["headline", "rating", "body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4}),
            "rating": forms.RadioSelect(choices=Review.RATING_CHOICES),
        }
  
        
class PostReviewAndTicketForm(forms.Form):
    title = forms.CharField(max_length=128, label="Titre du ticket")
    description = forms.CharField(widget=forms.Textarea, required=False, label="Description du ticket")
    image = forms.ImageField(required=False)
    
    rating = forms.ChoiceField(choices=[(i, str(i)) for i in range(1, 6)], label="Note")
    comment = forms.CharField(widget=forms.Textarea, label="Commentaires")


class FollowUsersForm(forms.ModelForm):
    class Meta:
        model = UserFollows
        fields = ["followed_user"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["followed_user"].queryset = User.objects.exclude(pk=user.pk)
