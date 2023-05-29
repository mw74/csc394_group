from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth.models import User


def home_redirect(request):
    return redirect('/home')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('/home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            
            if User.objects.filter(username=username).exists():
                error_message = 'Username already exists. Please choose a different username.'
            elif User.objects.filter(email=email).exists():
                error_message = 'Email already exists. Please use a different email.'
            else:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password1'])
                user.save()
                
                regular_user_group = Group.objects.get(name='Regular User')
                user.groups.add(regular_user_group)
                
                messages.success(request, 'Registration successful. You can now login.')
                return redirect('/home')
        else:
            error_message = "Invalid form submission. Please check the provided information."
    else:
        form = UserCreationForm()
        error_message = None

    return render(request, 'register.html', {'form': form, 'error_message': error_message})
