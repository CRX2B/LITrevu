from django.shortcuts import render, get_object_or_404
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
from .forms import TicketForm, PostReviewForm, FollowUsersForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.db.models import Q
from itertools import chain


# Views pour Ticket
class TicketCreateView(LoginRequiredMixin, CreateView):
    """
    Vue pour créer un nouveau ticket.
    Nécessite que l'utilisateur soit connecté.
    Le ticket est automatiquement associé à l'utilisateur connecté.
    """

    model = Ticket
    form_class = TicketForm
    template_name = "review/createticket.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        """Associe l'utilisateur connecté au ticket avant la sauvegarde"""
        form.instance.user = self.request.user
        return super().form_valid(form)


class TicketDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'un ticket.
    Inclut également les critiques associées à ce ticket.
    """

    model = Ticket
    template_name = "review/detailticket.html"
    context_object_name = "ticket"

    def get_context_data(self, **kwargs):
        """Ajoute les critiques associées au contexte"""
        context = super().get_context_data(**kwargs)
        context["reviews"] = Review.objects.filter(ticket=self.object)
        return context


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = "review/updateticket.html"
    success_url = reverse_lazy("home")


class TicketDeleteView(LoginRequiredMixin, DeleteView):
    model = Ticket
    success_url = reverse_lazy("home")
    template_name = "review/confirmdelete.html"


# Views pour Review
class ReviewCreateView(LoginRequiredMixin, CreateView):
    """
    Vue pour créer une critique en réponse à un ticket existant.
    Vérifie qu'il n'existe pas déjà une critique pour ce ticket.
    """

    model = Review
    form_class = PostReviewForm
    template_name = "review/createreview.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        """
        Vérifie l'unicité de la critique et l'associe au ticket et à l'utilisateur
        """
        if Review.objects.filter(ticket_id=self.kwargs["ticket_pk"]).exists():
            return HttpResponse("une critique existe déjà pour ce ticket")

        form.instance.user = self.request.user
        form.instance.ticket_id = self.kwargs["ticket_pk"]
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Ajoute le ticket associé au contexte"""
        context = super().get_context_data(**kwargs)
        context["ticket"] = get_object_or_404(Ticket, pk=self.kwargs["ticket_pk"])
        return context


class ReviewDetailView(LoginRequiredMixin, DetailView):
    model = Review
    template_name = "review/detailreview.html"
    context_object_name = "review"


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = PostReviewForm
    template_name = "review/updatereview.html"
    success_url = reverse_lazy("home")


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    success_url = reverse_lazy("home")
    template_name = "review/confirmdelete.html"


class CreateReviewWithoutTicketView(LoginRequiredMixin, CreateView):
    """
    Vue pour créer une critique sans ticket associé.
    Permet de créer une critique spontanée sur n'importe quel livre.
    """

    model = Review
    form_class = PostReviewForm
    template_name = "review/createreview.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        """Associe l'utilisateur connecté à la critique"""
        form.instance.user = self.request.user
        return super().form_valid(form)


class FollowUsersView(LoginRequiredMixin, CreateView):
    """
    Vue pour gérer les abonnements entre utilisateurs.
    Permet de suivre d'autres utilisateurs et de voir ses abonnements/abonnés.
    """

    model = UserFollows
    template_name = "review/followpage.html"
    form_class = FollowUsersForm
    success_url = reverse_lazy("home")

    def get_form_kwargs(self):
        """Ajoute l'utilisateur courant aux kwargs du formulaire"""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Vérifie que l'utilisateur ne suit pas déjà la personne"""
        if UserFollows.objects.filter(
            user=self.request.user, followed_user=form.cleaned_data["followed_user"]
        ).exists():
            return HttpResponse("Vous suivez déjà cet utilisateur")
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Ajoute la liste des abonnements et abonnés au contexte"""
        context = super().get_context_data(**kwargs)
        context["following"] = UserFollows.objects.filter(user=self.request.user)
        context["followers"] = UserFollows.objects.filter(
            followed_user=self.request.user
        )
        return context


class UnfollowUserView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        try:
            follow_relation = UserFollows.objects.get(
                user=request.user, followed_user_id=user_id
            )
            follow_relation.delete()
            return redirect("follow_users")
        except UserFollows.DoesNotExist:
            return HttpResponse("Vous ne suivez pas cet utilisateur")


# Views pour la page d'accueil
@login_required
def home(request):
    """
    Vue de la page d'accueil.
    Affiche un flux combiné des tickets et critiques :
    - De l'utilisateur connecté
    - Des utilisateurs qu'il suit
    Les éléments sont triés par date de création décroissante.
    """
    # Récupère les tickets de l'utilisateur et des personnes suivies
    tickets = Ticket.objects.filter(
        Q(user=request.user)
        | Q(
            user__in=UserFollows.objects.filter(user=request.user).values_list(
                "followed_user", flat=True
            )
        )
    ).prefetch_related("review_set")

    # Récupère les critiques sans ticket
    reviews_without_ticket = Review.objects.filter(
        Q(user=request.user)
        | Q(
            user__in=UserFollows.objects.filter(user=request.user).values_list(
                "followed_user", flat=True
            )
        ),
        ticket__isnull=True,
    )

    # Combine et trie les deux types de contenu
    flux = sorted(
        chain(tickets, reviews_without_ticket),
        key=lambda instance: instance.created_at,
        reverse=True,
    )

    context = {
        "flux": flux,
    }
    return render(request, "review/home.html", context)
