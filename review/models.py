from django.db import models
from authentication.models import User
from django.conf import settings
from PIL import Image
from django.core.validators import MinValueValidator, MaxValueValidator


class Ticket(models.Model):
    """
    Modèle représentant un ticket de demande de critique.
    Un ticket est créé par un utilisateur pour demander des critiques sur un livre/article.

    Attributes:
        title (str): Titre du livre/article (max 128 caractères)
        description (str): Description détaillée du livre/article (max 2048 caractères)
        created_at (datetime): Date et heure de création (automatique)
        updated_at (datetime): Date et heure de dernière modification (automatique)
        user (User): Utilisateur ayant créé le ticket
        image (ImageField): Image optionnelle du livre/article
    """

    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="tickets/", null=True, blank=True)

    IMAGE_MAX_SIZE = (500, 500)

    def resize_image(self):
        """Redimensionne l'image téléchargée aux dimensions maximales définies"""
        if self.image:
            image = Image.open(self.image)
            image.thumbnail(self.IMAGE_MAX_SIZE)
            image.save(self.image.path)

    def save(self, *args, **kwargs):
        """Surcharge de la méthode save pour redimensionner l'image avant sauvegarde"""
        super().save(*args, **kwargs)
        self.resize_image()

    def __str__(self):
        return f"{self.title}"


class Review(models.Model):
    """
    Modèle représentant une critique.
    Une critique peut être liée à un ticket existant ou créée indépendamment.

    Attributes:
        ticket (Ticket): Ticket associé à la critique (optionnel)
        rating (int): Note donnée de 1 à 5
        headline (str): Titre de la critique (max 128 caractères)
        body (str): Corps de la critique (max 8192 caractères)
        user (User): Utilisateur ayant créé la critique
        created_at (datetime): Date et heure de création (automatique)
    """

    RATING_CHOICES = [(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")]

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.headline}"


class UserFollows(models.Model):
    """
    Modèle gérant les relations d'abonnement entre utilisateurs.
    Permet à un utilisateur de suivre d'autres utilisateurs.

    Attributes:
        user (User): Utilisateur qui suit
        followed_user (User): Utilisateur qui est suivi

    Meta:
        unique_together assure qu'un utilisateur ne peut pas suivre deux fois la même personne
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following"
    )
    followed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followed_by"
    )

    class Meta:
        # Garantit qu'un utilisateur ne peut suivre un autre utilisateur qu'une seule fois
        unique_together = ("user", "followed_user")

    def __str__(self):
        return f"{self.user} suit {self.followed_user}"
