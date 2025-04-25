from django.shortcuts import render, redirect
from .forms import PreferenceForm
from .models import Preference
from django.contrib.auth.decorators import login_required

@login_required
def edit_preferences(request):
    try:
        preference = Preference.objects.get(user=request.user)
    except Preference.DoesNotExist:
        preference = Preference(user=request.user)
        preference.save()

    if request.method == "POST":
        form = PreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = PreferenceForm(instance=preference)

    return render(request, 'preferences/edit_preferences.html', {'form': form})

def profile_view(request): #nado izmenit
    return render(request, 'preferences/profile.html')

@login_required
def view_preferences(request):
    try:
        preference = Preference.objects.get(user=request.user)
    except Preference.DoesNotExist:
        preference = None

    return render(request, 'preferences/view_preferences.html', {'preference': preference})
