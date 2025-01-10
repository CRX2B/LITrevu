from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modèle personnalisé d'utilisateur héritant de AbstractUser de Django.
    Étend le modèle utilisateur par défaut pour ajouter des fonctionnalités supplémentaires.

    Attributes:
        profile_picture (ImageField): Photo de profil optionnelle de l'utilisateur

    Note:
        Hérite de tous les champs standard de AbstractUser (username, email, password, etc.)
    """

    profile_picture = models.ImageField(
        upload_to="profile_pictures", null=True, blank=True
    )

    def __str__(self):
        """Représentation textuelle de l'utilisateur (son nom d'utilisateur)"""
        return self.username
