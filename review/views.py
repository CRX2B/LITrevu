from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Ticket, Review, UserFollows
from .forms import TicketForm, PostReviewForm, FollowUsersForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View


# Views pour Ticket
class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = "review/createticket.html"
    success_url = reverse_lazy("home")
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = "review/detailticket.html"
    context_object_name = "ticket"
    
    def get_context_data(self, **kwargs):
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
    model = Review
    form_class = PostReviewForm
    template_name = "review/createreview.html"
    success_url = reverse_lazy("home")
    
    def form_valid(self, form):
        if Review.objects.filter(ticket_id=self.kwargs["ticket_pk"]).exists():
            return HttpResponse("une critique existe déjà pour ce ticket")
        
        form.instance.user = self.request.user
        form.instance.ticket_id = self.kwargs["ticket_pk"]
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
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
    model = Review
    form_class = PostReviewForm
    template_name = "review/createreview.html"
    success_url = reverse_lazy("home")
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    

class FollowUsersView(LoginRequiredMixin, CreateView):
    model = UserFollows
    template_name = "review/followpage.html"
    form_class = FollowUsersForm
    success_url = reverse_lazy("home")
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        if UserFollows.objects.filter(user=self.request.user, followed_user=form.cleaned_data["followed_user"]).exists():
            return HttpResponse("Vous suivez déjà cet utilisateur")
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["following"] = UserFollows.objects.filter(user=self.request.user)
        context["followers"] = UserFollows.objects.filter(followed_user=self.request.user)
        return context
    
class UnfollowUserView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        try:
            follow_relation = UserFollows.objects.get(user=request.user, followed_user_id=user_id)
            follow_relation.delete()
            return redirect("follow_users")
        except UserFollows.DoesNotExist:
            return HttpResponse("Vous ne suivez pas cet utilisateur")

# Views pour la page d'accueil
@login_required
def home(request):
    tickets = Ticket.objects.all()
    reviews = Review.objects.all()
    return render(request, "review/home.html", {
        "tickets": tickets,
        "reviews": reviews,
    })




