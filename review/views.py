from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Ticket, Review, UserFollows
from .forms import TicketForm, PostReviewForm, FollowUsersForm, PostReviewAndTicketForm
from django.http import HttpResponse
from django.views import View
from django.db.models import Q, Count
from itertools import chain
from django.contrib import messages
from authentication.models import User


# Views pour Ticket
class TicketCreateView(LoginRequiredMixin, CreateView):
    """Vue pour créer un nouveau ticket.

    Nécessite que l'utilisateur soit connecté.
    Le ticket est automatiquement associé à l'utilisateur connecté.
    """

    model = Ticket
    form_class = TicketForm
    template_name = "review/createticket.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        """Associe l'utilisateur connecté au ticket avant la sauvegarde.

        Args:
            form: Le formulaire validé

        Returns:
            HttpResponse: Redirection vers la page de succès
        """
        form.instance.user = self.request.user
        return super().form_valid(form)


class TicketDetailView(LoginRequiredMixin, DetailView):
    """Vue pour afficher les détails d'un ticket.

    Inclut également les critiques associées à ce ticket.
    Nécessite que l'utilisateur soit connecté.
    """

    model = Ticket
    template_name = "review/detailticket.html"
    context_object_name = "ticket"

    def get_context_data(self, **kwargs):
        """Ajoute les critiques associées au contexte.

        Returns:
            dict: Contexte enrichi avec les critiques associées au ticket
        """
        context = super().get_context_data(**kwargs)
        context["reviews"] = Review.objects.filter(ticket=self.object)
        return context


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    """Vue pour modifier un ticket existant.

    Nécessite que l'utilisateur soit connecté.
    """

    model = Ticket
    form_class = TicketForm
    template_name = "review/updateticket.html"
    success_url = reverse_lazy("home")


class TicketDeleteView(LoginRequiredMixin, DeleteView):
    """Vue pour supprimer un ticket.

    Nécessite que l'utilisateur soit connecté.
    """

    model = Ticket
    success_url = reverse_lazy("home")
    template_name = "review/confirmdelete.html"


# Views pour Review
class ReviewCreateView(LoginRequiredMixin, CreateView):
    """Vue pour créer une critique en réponse à un ticket existant.

    Vérifie qu'il n'existe pas déjà une critique pour ce ticket.
    Nécessite que l'utilisateur soit connecté.
    """

    model = Review
    form_class = PostReviewForm
    template_name = "review/createreview.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        """Vérifie l'unicité de la critique et l'associe au ticket et à l'utilisateur.

        Args:
            form: Le formulaire validé

        Returns:
            HttpResponse: Redirection vers la page de succès ou message d'erreur
        """
        if Review.objects.filter(ticket_id=self.kwargs["ticket_pk"]).exists():
            return HttpResponse("Une critique existe déjà pour ce ticket")

        form.instance.user = self.request.user
        form.instance.ticket_id = self.kwargs["ticket_pk"]
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Ajoute le ticket associé au contexte.

        Returns:
            dict: Contexte enrichi avec le ticket associé
        """
        context = super().get_context_data(**kwargs)
        context["ticket"] = get_object_or_404(Ticket, pk=self.kwargs["ticket_pk"])
        return context


class ReviewDetailView(LoginRequiredMixin, DetailView):
    """Vue pour afficher les détails d'une critique.

    Nécessite que l'utilisateur soit connecté.
    """

    model = Review
    template_name = "review/detailreview.html"
    context_object_name = "review"


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    """Vue pour modifier une critique existante.

    Nécessite que l'utilisateur soit connecté.
    """

    model = Review
    form_class = PostReviewForm
    template_name = "review/updatereview.html"
    success_url = reverse_lazy("home")


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    """Vue pour supprimer une critique.

    Nécessite que l'utilisateur soit connecté.
    """

    model = Review
    success_url = reverse_lazy("home")
    template_name = "review/confirmdelete.html"


@login_required
def create_review_and_ticket(request):
    """Vue pour créer simultanément un ticket et sa critique.

    Nécessite que l'utilisateur soit connecté.

    Args:
        request: La requête HTTP

    Returns:
        HttpResponse: Page de création ou redirection vers l'accueil
    """
    if request.method == "POST":
        form = PostReviewAndTicketForm(request.POST, request.FILES)
        if form.is_valid():
            # Créer le ticket
            ticket = Ticket.objects.create(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                image=form.cleaned_data["image"],
                user=request.user,
            )
            # Créer la critique
            Review.objects.create(
                ticket=ticket,
                rating=form.cleaned_data["rating"],
                headline=form.cleaned_data["title"],
                body=form.cleaned_data["comment"],
                user=request.user,
            )
            return redirect("home")
    else:
        form = PostReviewAndTicketForm()

    return render(request, "review/createreviewandticket.html", {"form": form})


class FollowUsersView(LoginRequiredMixin, CreateView):
    """Vue pour gérer les abonnements entre utilisateurs.

    Permet de suivre d'autres utilisateurs et de voir ses abonnements/abonnés.
    Nécessite que l'utilisateur soit connecté.
    """

    model = UserFollows
    template_name = "review/followpage.html"
    form_class = FollowUsersForm
    success_url = reverse_lazy("follow_users")

    def get_form_kwargs(self):
        """Ajoute l'utilisateur courant aux kwargs du formulaire.

        Returns:
            dict: kwargs enrichis avec l'utilisateur courant
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Vérifie et crée la relation d'abonnement.

        Args:
            form: Le formulaire validé

        Returns:
            HttpResponse: Redirection avec message de succès ou d'erreur
        """
        if UserFollows.objects.filter(
            user=self.request.user, followed_user=form.cleaned_data["followed_user"]
        ).exists():
            messages.error(self.request, "Vous suivez déjà cet utilisateur.")
            return redirect("follow_users")

        form.instance.user = self.request.user
        messages.success(
            self.request,
            f"Vous suivez maintenant {form.cleaned_data['followed_user'].username}.",
        )
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        """Gère la recherche et l'ajout d'un utilisateur à suivre.

        Args:
            request: La requête HTTP
            args: Arguments positionnels
            kwargs: Arguments nommés

        Returns:
            HttpResponse: Redirection avec message approprié
        """
        search_user = request.POST.get("search_user")
        if search_user:
            try:
                user = User.objects.get(username=search_user)
                if user == request.user:
                    messages.error(request, "Vous ne pouvez pas vous suivre vous-même.")
                    return redirect("follow_users")
                return super().post(request, *args, **kwargs)
            except User.DoesNotExist:
                messages.error(request, f"L'utilisateur '{search_user}' n'existe pas.")
                return redirect("follow_users")
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Ajoute les listes d'abonnements et d'abonnés au contexte.

        Returns:
            dict: Contexte enrichi avec les relations d'abonnement
        """
        context = super().get_context_data(**kwargs)
        context["following"] = UserFollows.objects.filter(user=self.request.user)
        context["followers"] = UserFollows.objects.filter(
            followed_user=self.request.user
        )
        return context


class UnfollowUserView(LoginRequiredMixin, View):
    """Vue pour se désabonner d'un utilisateur.

    Nécessite que l'utilisateur soit connecté.
    """

    def post(self, request, user_id):
        """Supprime la relation d'abonnement.

        Args:
            request: La requête HTTP
            user_id: L'ID de l'utilisateur à ne plus suivre

        Returns:
            HttpResponse: Redirection ou message d'erreur
        """
        try:
            follow_relation = UserFollows.objects.get(
                user=request.user, followed_user_id=user_id
            )
            follow_relation.delete()
            return redirect("follow_users")
        except UserFollows.DoesNotExist:
            return HttpResponse("Vous ne suivez pas cet utilisateur")


@login_required
def user_posts(request):
    """Vue pour afficher les posts d'un utilisateur.

    Affiche les tickets et critiques créés par l'utilisateur connecté.

    Args:
        request: La requête HTTP

    Returns:
        HttpResponse: Page avec les posts de l'utilisateur
    """
    tickets = Ticket.objects.filter(user=request.user)
    reviews = Review.objects.filter(user=request.user)
    context = {
        "tickets": tickets,
        "reviews": reviews,
    }
    return render(request, "review/userposts.html", context)


# Views pour la page d'accueil
@login_required
def home(request):
    """Vue de la page d'accueil.

    Affiche un flux combiné des tickets et critiques :
    - De l'utilisateur connecté
    - Des utilisateurs qu'il suit
    Les éléments sont triés par date de création décroissante.

    Args:
        request: La requête HTTP

    Returns:
        HttpResponse: Page d'accueil avec le flux d'activité
    """
    # Obtenir les utilisateurs suivis
    followed_users = UserFollows.objects.filter(user=request.user).values_list(
        "followed_user", flat=True
    )

    # Récupérer les tickets de l'utilisateur et des personnes suivies
    tickets = (
        Ticket.objects.filter(Q(user=request.user) | Q(user__in=followed_users))
        .annotate(review_count=Count("review"))
        .filter(review_count=0)
    )

    # Récupérer les critiques associées aux tickets
    reviews_with_ticket = Review.objects.filter(
        Q(user=request.user) | Q(user__in=followed_users)
    ).prefetch_related("ticket")

    flux = sorted(
        chain(tickets, reviews_with_ticket),
        key=lambda instance: instance.created_at,
        reverse=True,
    )

    context = {
        "flux": flux,
    }

    return render(request, "review/home.html", context)
