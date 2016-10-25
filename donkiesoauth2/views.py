from rest_framework import generics, viewsets, views
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import auth
from donkiesoauth2.permissions import IsAuthenticatedOrCreate
from donkiesoauth2.serializers import SignUpSerializer
from donkiesoauth2.models import DonkiesUser
from donkiesoauth2.forms import DevUserRegForm


class DevSignUp(viewsets.GenericViewSet):
    queryset = DonkiesUser.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (IsAuthenticatedOrCreate, )


def register_user(request):
    next = request.POST.get('next', request.GET.get('next', ''))
    if request.method == "POST":
        user_form = DevUserRegForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.save()
            if next:
                return HttpResponseRedirect(next)
            return HttpResponseRedirect('/api/v1/')
    else:
        user_form = DevUserRegForm()

    context = {
        "user_form": user_form,
    }

    return render(request, 'registration/register.html', context)


# def logout(request):
#     auth.logout(request)
#     # Redirect back to login page
#     return HttpResponseRedirect(settings.LOGIN_URL)