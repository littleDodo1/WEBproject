from django.shortcuts import render, redirect
from .forms import PreferenceForm
from .models import Preference

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
