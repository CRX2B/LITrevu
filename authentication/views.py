from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import SignupForm, UserUpdateForm
from django.conf import settings

def signup(request):
    form = SignupForm()
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, "authentication/signup.html", context={"form": form})


def update_user(request):
    form = UserUpdateForm(instance=request.user)
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("home")
    return render(request, "authentication/updateuser.html", context={"form": form})

