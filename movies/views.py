import requests
from django.shortcuts import render
from django.conf import settings


def landing_page(request):
    category = request.GET.get('category', 'popular')
    search_query = request.GET.get('search', '')

    API_KEY = settings.TMDB_API_KEY
    base_url = 'https://api.themoviedb.org/3/movie/'
    error_message = ""

    if search_query:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={search_query}"
    else:
        url = f"{base_url}{category}?api_key={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get('results', [])
    except Exception as e:
        data=[]
        error_message = "Something went wrong !"
    # print(data)

    context = {"movies": data, "category": category, "search_query": search_query, "error_message": error_message}

    if request.headers.get('HX-Request'):
        return render(request, "movies/partials/_movie_list.html", context)
    return render(request, "movies/landing.html", context)
