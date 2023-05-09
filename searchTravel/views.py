from django.shortcuts import render

# Create your views here.
def search_travel(request):
    return render(request, 'search_travel.html')