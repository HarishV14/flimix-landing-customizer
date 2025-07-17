from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Max
from django.views.decorators.http import require_POST
from .models import Movie, Category, MovieInCategory, HeroSettings

def page_data(request):
    # Build the page structure based on database content
    page_json = {
        "type": "page",
        "children": []
    }
    
    # Add hero section from HeroSettings
    try:
        hero_settings = HeroSettings.objects.first()
        if hero_settings and hero_settings.featured_movie:
            hero_movie = hero_settings.featured_movie
            hero_section = {
                "type": "hero",
                "attributes": {
                    "backgroundImage": hero_movie.background_image_url,
                    "title": hero_movie.title,
                    "description": hero_movie.description,
                    "cta": {"text": "Watch Now", "link": hero_movie.link}
                }
            }
            page_json["children"].append(hero_section)
    except HeroSettings.DoesNotExist:
        # If no hero settings exist, don't include a hero section
        pass
    
    # Add carousels for each category
    categories = Category.objects.all().order_by('position')
    for category in categories:
        carousel = {
            "type": "carousel",
            "attributes": {"title": category.name},
            "children": []
        }
        
        # Get movies for this category with ordering
        category_movies = MovieInCategory.objects.filter(category=category).order_by('position')
        for category_movie in category_movies:
            movie = category_movie.movie
            movie_card = {
                "type": "movie-card",
                "attributes": {
                    "title": movie.title,
                    "poster": movie.poster_url,
                    "link": movie.link
                }
            }
            carousel["children"].append(movie_card)
        
        # Only add carousels with movies
        if carousel["children"]:
            page_json["children"].append(carousel)
    
    return JsonResponse(page_json)

# Custom Admin Views    
def admin_dashboard(request):
    # Get hero settings
    try:
        hero_settings = HeroSettings.objects.first()
    except HeroSettings.DoesNotExist:
        hero_settings = None
    
    # Get categories with movie counts
    categories = Category.objects.annotate(
        movie_count=Count('movies')
    ).order_by('position')
    
    return render(request, 'admin/dashboard.html', {
        'hero_settings': hero_settings,
        'categories': categories
    })

def admin_hero(request):
    # Get hero settings
    try:
        hero_settings = HeroSettings.objects.first()
    except HeroSettings.DoesNotExist:
        hero_settings = HeroSettings.objects.create()
    
    # Get all movies
    movies = Movie.objects.all().order_by('title')
    
    # Add category IDs for each movie for filtering
    for movie in movies:
        movie.category_ids = list(MovieInCategory.objects.filter(movie=movie).values_list('category_id', flat=True))
    
    # Get all categories for filtering
    categories = Category.objects.all().order_by('name')
    
    return render(request, 'admin/hero.html', {
        'hero_settings': hero_settings,
        'movies': movies,
        'categories': categories
    })

        
@require_POST
def update_hero(request):
    movie_id = request.POST.get('movie_id')
    if movie_id:
        movie = get_object_or_404(Movie, id=movie_id)
        
        # Get or create hero settings
        hero_settings, created = HeroSettings.objects.get_or_create(id=1)
        hero_settings.featured_movie = movie
        hero_settings.save()
        
        messages.success(request, f"Hero updated to '{movie.title}'")
    else:
        messages.error(request, "No movie selected")
    
    return redirect('admin-hero')


def admin_categories(request):
    if request.method == 'POST' and request.POST.get('action') == 'reorder':
        # Handle category reordering
        category_order = request.POST.get('category_order', '')
        if category_order:
            category_ids = category_order.split(',')
            for position, category_id in enumerate(category_ids):
                try:
                    category = Category.objects.get(id=category_id)
                    category.position = position
                    category.save()
                except Category.DoesNotExist:
                    pass
            
            messages.success(request, "Category order updated successfully")
    
    # Get categories with movie counts
    categories = Category.objects.annotate(
        movie_count=Count('movies')
    ).order_by('position')
    
    return render(request, 'admin/categories.html', {
        'categories': categories
    })

@require_POST
def create_category(request):
    name = request.POST.get('name', '').strip()
    if name:
        # Get the max position for new category
        max_position = Category.objects.all().aggregate(max_pos=Max('position'))['max_pos']
        position = 0 if max_position is None else max_position + 1
        
        # Create the category
        category = Category.objects.create(name=name, position=position)
        messages.success(request, f"Category '{name}' created successfully")
    else:
        messages.error(request, "Category name is required")
    
    return redirect('admin-categories')

@require_POST
def update_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    name = request.POST.get('name', '').strip()
    if name:
        category.name = name
        category.save()
        messages.success(request, f"Category updated to '{name}'")
    else:
        messages.error(request, "Category name is required")
    
    return redirect('admin-categories')

@require_POST
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    name = category.name
    
    # Delete the category
    category.delete()
    messages.success(request, f"Category '{name}' deleted successfully")
    
    return redirect('admin-categories')

def admin_category_movies(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    # Get movies in this category with ordering
    category_movies = MovieInCategory.objects.filter(category=category).order_by('position')
    
    # Get movies not in this category for the add movie modal
    category_movie_ids = category_movies.values_list('movie_id', flat=True)
    available_movies = Movie.objects.exclude(id__in=category_movie_ids).order_by('title')
    
    return render(request, 'admin/category_movies.html', {
        'category': category,
        'category_movies': category_movies,
        'available_movies': available_movies
    })

@require_POST
def add_movie_to_category(request, category_id, movie_id):
    category = get_object_or_404(Category, id=category_id)
    movie = get_object_or_404(Movie, id=movie_id)
    
    # Check if this movie is already in the category
    if not MovieInCategory.objects.filter(category=category, movie=movie).exists():
        # Get max position for new movie
        max_position = MovieInCategory.objects.filter(category=category).aggregate(
            max_pos=Max('position')
        )['max_pos']
        position = 0 if max_position is None else max_position + 1
        
        # Add movie to category
        MovieInCategory.objects.create(category=category, movie=movie, position=position)
        messages.success(request, f"Added '{movie.title}' to '{category.name}'")
    else:
        messages.warning(request, f"'{movie.title}' is already in '{category.name}'")
    
    return redirect('admin-category-movies', category_id=category_id)

@require_POST
def remove_movie_from_category(request, category_id, movie_id):
    category = get_object_or_404(Category, id=category_id)
    movie = get_object_or_404(Movie, id=movie_id)
    
    # Remove movie from category
    try:
        category_movie = MovieInCategory.objects.get(category=category, movie=movie)
        category_movie.delete()
        messages.success(request, f"Removed '{movie.title}' from '{category.name}'")
    except MovieInCategory.DoesNotExist:
        messages.warning(request, f"'{movie.title}' was not in '{category.name}'")
    
    return redirect('admin-category-movies', category_id=category_id)

@require_POST
def reorder_category_movies(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    movie_order = request.POST.get('movie_order', '')
    if movie_order:
        category_movie_ids = movie_order.split(',')
        for position, category_movie_id in enumerate(category_movie_ids):
            try:
                category_movie = MovieInCategory.objects.get(id=category_movie_id)
                category_movie.position = position
                category_movie.save()
            except MovieInCategory.DoesNotExist:
                pass
        
        messages.success(request, "Movie order updated successfully")
    
    return redirect('admin-category-movies', category_id=category_id)

# Movie Management Views
def admin_movies(request):
    # Get all movies with their categories
    movies = Movie.objects.all().order_by('title')
    
    # Add categories for each movie
    for movie in movies:
        movie.categories = Category.objects.filter(movieincategory__movie=movie).distinct()
    
    return render(request, 'admin/movies.html', {
        'movies': movies
    })

@require_POST
def create_movie(request):
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    poster_url = request.POST.get('poster_url', '').strip()
    background_image_url = request.POST.get('background_image_url', '').strip()
    link = request.POST.get('link', '#').strip()
    
    if title and description and poster_url and background_image_url:
        movie = Movie.objects.create(
            title=title,
            description=description,
            poster_url=poster_url,
            background_image_url=background_image_url,
            link=link
        )
        messages.success(request, f"Movie '{title}' created successfully")
    else:
        messages.error(request, "All fields are required")
    
    return redirect('admin-movies')

@require_POST
def edit_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    poster_url = request.POST.get('poster_url', '').strip()
    background_image_url = request.POST.get('background_image_url', '').strip()
    link = request.POST.get('link', '#').strip()
    
    if title and description and poster_url and background_image_url:
        movie.title = title
        movie.description = description
        movie.poster_url = poster_url
        movie.background_image_url = background_image_url
        movie.link = link
        movie.save()
        messages.success(request, f"Movie '{title}' updated successfully")
    else:
        messages.error(request, "All fields are required")
    
    return redirect('admin-movies')

@require_POST
def delete_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    title = movie.title
    
    # Check if this movie is used in hero settings
    hero_settings = HeroSettings.objects.filter(featured_movie=movie).first()
    if hero_settings:
        hero_settings.featured_movie = None
        hero_settings.save()
    
    # Delete the movie (this will cascade delete all MovieInCategory entries)
    movie.delete()
    messages.success(request, f"Movie '{title}' deleted successfully")
    
    return redirect('admin-movies')