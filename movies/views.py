from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Max
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import (
    Movie, Series, Genre, Section, SectionItem, 
    LandingPage, LandingPageSection
)
import json

# API Views for React Frontend
@csrf_exempt
@require_http_methods(["GET"])
def api_landing_pages(request):
    """API endpoint for landing pages list"""
    try:
        landing_pages = LandingPage.objects.all().order_by('-is_active', '-updated_at')
        data = []
        for lp in landing_pages:
            landing_page_sections = LandingPageSection.objects.filter(
                landing_page=lp
            ).select_related('section').order_by('position')
            data.append({
                'id': lp.id,
                'name': lp.name,
                'is_active': lp.is_active,
                'created_at': lp.created_at.isoformat(),
                'updated_at': lp.updated_at.isoformat(),
                'landingpagesection_set': [
                    {
                        'id': lp_section.id,
                        'position': lp_section.position,
                        'section': {
                            'id': lp_section.section.id,
                            'name': lp_section.section.name,
                            'section_type': lp_section.section.section_type,
                            'content_selection_type': lp_section.section.content_selection_type,
                        }
                    }
                    for lp_section in landing_page_sections
                ]
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_sections(request):
    """API endpoint for sections list"""
    try:
        sections = Section.objects.annotate(
            content_count=Count('sectionitem')
        ).order_by('position')
        
        data = [
            {
                'id': section.id,
                'name': section.name,
                'section_type': section.section_type,
                'content_selection_type': section.content_selection_type,
                'position': section.position,
                'content_count': section.content_count,
            }
            for section in sections
        ]
        
        return JsonResponse(data, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_movies(request):
    """API endpoint for movies list"""
    try:
        movies = Movie.objects.all().order_by('title')
        
        data = [
            {
                'id': movie.id,
                'title': movie.title,
                'description': movie.description,
                'poster_url': movie.poster_url,
                'background_image_url': movie.background_image_url,
                'link': movie.link,
                'duration_minutes': movie.duration_minutes,
                'release_year': movie.release_year,
                'created_at': movie.created_at.isoformat(),
                'genres': [genre.name for genre in movie.genres.all()],
            }
            for movie in movies
        ]
        
        return JsonResponse(data, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_series(request):
    """API endpoint for series list"""
    try:
        series_list = Series.objects.all().order_by('title')
        
        data = [
            {
                'id': series.id,
                'title': series.title,
                'description': series.description,
                'poster_url': series.poster_url,
                'background_image_url': series.background_image_url,
                'link': series.link,
                'seasons': series.seasons,
                'episodes_count': series.episodes_count,
                'release_year': series.release_year,
                'created_at': series.created_at.isoformat(),
                'genres': [genre.name for genre in series.genres.all()],
            }
            for series in series_list
        ]
        
        return JsonResponse(data, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def page_data(request):
    """
    API endpoint that returns the landing page structure as JSON
    for the React frontend to render
    """
    try:
        # Get the active landing page or create a default one
        landing_page = LandingPage.get_active()
        
        # Build the page structure based on database content
        page_json = {
            "type": "page",
            "children": []
        }
        
        # Get all sections for this landing page in order
        landing_page_sections = LandingPageSection.objects.filter(
            landing_page=landing_page
        ).select_related('section').order_by('position')
        
        for lp_section in landing_page_sections:
            section = lp_section.section
            
            # Always use section.name as the title
            print(section.settings)
            print(section.name)
            section_json = {
                "type": section.section_type,
                "attributes": {
                    "title": section.settings.get('title', section.name),
                    **section.settings  # Include any additional settings
                },
                "children": []
            }
            
            # Get content for this section
            content_items = section.get_content()
            
            # Process content items based on section type
            if section.section_type == 'hero' and content_items:
                # For hero, we just use the first item
                if content_items:
                    hero_content = content_items[0]
                    if isinstance(hero_content, tuple):  # For automatic selection
                        content, content_type = hero_content
                    else:  # For manual selection
                        content = hero_content
                        content_type = content.get_content_type() if hasattr(content, 'get_content_type') else 'unknown'
                    
                    # Check if content is not None before accessing attributes
                    if content is not None:
                        section_json["attributes"].update({
                            "backgroundImage": content.background_image_url,
                            "title": content.title,  # This is the movie/series title
                            "description": content.description,
                            "contentType": content_type,
                            "cta": {"text": "Watch Now", "link": content.link}
                        })
                
            else:
                # For other section types (carousel, grid, etc.)
                for item in content_items:
                    if isinstance(item, tuple):  # For automatic selection
                        content, content_type = item
                    else:  # For manual selection
                        content = item
                        content_type = content.get_content_type() if hasattr(content, 'get_content_type') else 'unknown'
                    
                    # Check if content is not None before creating JSON
                    if content is not None:
                        content_json = {
                            "type": f"{content_type}-card",
                            "attributes": {
                                "title": content.title,
                                "poster": content.poster_url,
                                "link": content.link,
                                "contentType": content_type,
                            }
                        }
                        
                        # Add content type specific attributes
                        if content_type == 'movie' and hasattr(content, 'duration_minutes'):
                            content_json["attributes"]["duration"] = content.duration_minutes
                            content_json["attributes"]["releaseYear"] = content.release_year
                        elif content_type == 'series' and hasattr(content, 'seasons'):
                            content_json["attributes"]["seasons"] = content.seasons
                            content_json["attributes"]["episodes"] = content.episodes_count
                            content_json["attributes"]["releaseYear"] = content.release_year
                        
                        section_json["children"].append(content_json)
            
            # Only add sections with content
            if section.section_type == 'hero' or section_json["children"]:
                page_json["children"].append(section_json)
        
        return JsonResponse(page_json)
    
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in page_data view: {str(e)}")
        
        # Return a basic error response
        return JsonResponse({
            "error": "Failed to load page data",
            "message": str(e)
        }, status=500)

# Admin Dashboard
@staff_member_required
def admin_dashboard(request):
    # Get active landing page
    landing_page = LandingPage.get_active()
    
    # Get all landing pages
    landing_pages = LandingPage.objects.all()
    
    # Get sections with content counts
    sections = Section.objects.annotate(
        content_count=Count('sectionitem')
    ).order_by('position')
    
    # Get content counts by type
    movie_count = Movie.objects.count()
    series_count = Series.objects.count()
    
    return render(request, 'admin/dashboard.html', {
        'landing_page': landing_page,
        'landing_pages': landing_pages,
        'sections': sections,
        'movie_count': movie_count,
        'series_count': series_count
    })

# Landing Page Management
@staff_member_required
def admin_landing_pages(request):
    landing_pages = LandingPage.objects.all().order_by('-is_active', '-updated_at')
    
    return render(request, 'admin/landing_pages.html', {
        'landing_pages': landing_pages
    })

@staff_member_required
@require_POST
def create_landing_page(request):
    name = request.POST.get('name', '').strip()
    if name:
        landing_page = LandingPage.objects.create(name=name)
        messages.success(request, f"Landing page '{name}' created successfully")
    else:
        messages.error(request, "Landing page name is required")
    
    return redirect('admin-landing-pages')

@staff_member_required
@require_POST
def activate_landing_page(request, landing_page_id):
    landing_page = get_object_or_404(LandingPage, id=landing_page_id)
    landing_page.activate()
    messages.success(request, f"Landing page '{landing_page.name}' is now active")
    
    return redirect('admin-landing-pages')

@staff_member_required
@require_POST
def delete_landing_page(request, landing_page_id):
    landing_page = get_object_or_404(LandingPage, id=landing_page_id)
    
    # Don't allow deleting the active landing page
    if landing_page.is_active:
        messages.error(request, "Cannot delete the active landing page")
        return redirect('admin-landing-pages')
    
    name = landing_page.name
    landing_page.delete()
    messages.success(request, f"Landing page '{name}' deleted successfully")
    
    return redirect('admin-landing-pages')

@staff_member_required
def admin_landing_page_sections(request, landing_page_id):
    landing_page = get_object_or_404(LandingPage, id=landing_page_id)
    
    # Get sections in this landing page with ordering
    landing_page_sections = LandingPageSection.objects.filter(
        landing_page=landing_page
    ).select_related('section').order_by('position')
    
    # Get sections not in this landing page
    section_ids = landing_page_sections.values_list('section_id', flat=True)
    available_sections = Section.objects.exclude(id__in=section_ids).order_by('name')
    
    return render(request, 'admin/landing_page_sections.html', {
        'landing_page': landing_page,
        'landing_page_sections': landing_page_sections,
        'available_sections': available_sections
    })

@staff_member_required
@require_POST
def add_section_to_landing_page(request, landing_page_id, section_id):
    landing_page = get_object_or_404(LandingPage, id=landing_page_id)
    section = get_object_or_404(Section, id=section_id)
    
    # Check if this section is already in the landing page
    if not LandingPageSection.objects.filter(landing_page=landing_page, section=section).exists():
        # Get max position for new section
        max_position = LandingPageSection.objects.filter(landing_page=landing_page).aggregate(
            max_pos=Max('position')
        )['max_pos']
        position = 0 if max_position is None else max_position + 1
        
        # Add section to landing page
        LandingPageSection.objects.create(landing_page=landing_page, section=section, position=position)
        messages.success(request, f"Added '{section.name}' to '{landing_page.name}'")
    else:
        messages.warning(request, f"'{section.name}' is already in '{landing_page.name}'")
    
    return redirect('admin-landing-page-sections', landing_page_id=landing_page_id)

@staff_member_required
@require_POST
def remove_section_from_landing_page(request, landing_page_id, section_id):
    landing_page = get_object_or_404(LandingPage, id=landing_page_id)
    section = get_object_or_404(Section, id=section_id)
    
    # Remove section from landing page
    try:
        landing_page_section = LandingPageSection.objects.get(landing_page=landing_page, section=section)
        landing_page_section.delete()
        messages.success(request, f"Removed '{section.name}' from '{landing_page.name}'")
    except LandingPageSection.DoesNotExist:
        messages.warning(request, f"'{section.name}' was not in '{landing_page.name}'")
    
    return redirect('admin-landing-page-sections', landing_page_id=landing_page_id)

@staff_member_required
@require_POST
def reorder_landing_page_sections(request, landing_page_id):
    landing_page = get_object_or_404(LandingPage, id=landing_page_id)
    
    section_order = request.POST.get('section_order', '')
    if section_order:
        landing_page_section_ids = section_order.split(',')
        for position, landing_page_section_id in enumerate(landing_page_section_ids):
            try:
                landing_page_section = LandingPageSection.objects.get(id=landing_page_section_id)
                landing_page_section.position = position
                landing_page_section.save()
            except LandingPageSection.DoesNotExist:
                pass
        
        messages.success(request, "Section order updated successfully")
    
    return redirect('admin-landing-page-sections', landing_page_id=landing_page_id)

# Section Management
@staff_member_required
def admin_sections(request):
    # Get sections with content counts
    sections = Section.objects.annotate(
        content_count=Count('sectionitem')
    ).order_by('position')
    
    # Get genres for automatic selection
    genres = Genre.objects.all().order_by('name')
    
    return render(request, 'admin/sections.html', {
        'sections': sections,
        'genres': genres
    })

@staff_member_required
@require_POST
def create_section(request):
    name = request.POST.get('name', '').strip()
    section_type = request.POST.get('section_type', '').strip()
    content_selection_type = request.POST.get('content_selection_type', 'manual').strip()
    auto_genre_id = request.POST.get('auto_genre_id')
    
    if name and section_type:
        # Get the max position for new section
        max_position = Section.objects.all().aggregate(max_pos=Max('position'))['max_pos']
        position = 0 if max_position is None else max_position + 1
        
        # Create section
        section = Section(
            name=name, 
            section_type=section_type,
            position=position,
            content_selection_type=content_selection_type
        )
        
        # Set auto genre if automatic selection
        if content_selection_type == 'automatic' and auto_genre_id:
            try:
                genre = Genre.objects.get(id=auto_genre_id)
                section.auto_genre = genre
            except Genre.DoesNotExist:
                pass
        
        section.save()
        messages.success(request, f"Section '{name}' created successfully")
    else:
        messages.error(request, "Section name and type are required")
    
    return redirect('admin-sections')

@staff_member_required
@require_POST
def update_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    
    name = request.POST.get('name', '').strip()
    content_selection_type = request.POST.get('content_selection_type', 'manual').strip()
    auto_genre_id = request.POST.get('auto_genre_id')
    
    if name:
        section.name = name
        section.content_selection_type = content_selection_type
        
        # Update auto genre if automatic selection
        if content_selection_type == 'automatic' and auto_genre_id:
            try:
                genre = Genre.objects.get(id=auto_genre_id)
                section.auto_genre = genre
            except Genre.DoesNotExist:
                section.auto_genre = None
        else:
            section.auto_genre = None
            
        section.save()
        messages.success(request, f"Section updated to '{name}'")
    else:
        messages.error(request, "Section name is required")
    
    return redirect('admin-sections')

@staff_member_required
@require_POST
def delete_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    name = section.name
    
    # Delete the section
    section.delete()
    messages.success(request, f"Section '{name}' deleted successfully")
    
    return redirect('admin-sections')

@staff_member_required
@require_POST
def reorder_sections(request):
    section_order = request.POST.get('section_order', '')
    if section_order:
        section_ids = section_order.split(',')
        for position, section_id in enumerate(section_ids):
            try:
                section = Section.objects.get(id=section_id)
                section.position = position
                section.save()
            except Section.DoesNotExist:
                pass
        
        messages.success(request, "Section order updated successfully")
    
    return redirect('admin-sections')

# Section Content Management
@staff_member_required
def admin_section_content(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    
    # If automatic selection, just show the genre and content
    if section.content_selection_type == 'automatic':
        if section.auto_genre:
            movies = Movie.objects.filter(genres=section.auto_genre).order_by('-created_at')
            series = Series.objects.filter(genres=section.auto_genre).order_by('-created_at')
        else:
            movies = []
            series = []
        
        return render(request, 'admin/section_content_auto.html', {
            'section': section,
            'movies': movies,
            'series': series
        })
    
    # For manual selection
    # Get content in this section with ordering
    section_items = SectionItem.objects.filter(section=section).order_by('position')
    
    # Get all content not in this section
    movie_content_type = ContentType.objects.get_for_model(Movie)
    series_content_type = ContentType.objects.get_for_model(Series)
    
    # Get IDs of content already in the section
    movie_ids_in_section = section_items.filter(
        content_type=movie_content_type
    ).values_list('object_id', flat=True)
    
    series_ids_in_section = section_items.filter(
        content_type=series_content_type
    ).values_list('object_id', flat=True)
    
    # Get available content
    available_movies = Movie.objects.exclude(id__in=movie_ids_in_section).order_by('title')
    available_series = Series.objects.exclude(id__in=series_ids_in_section).order_by('title')
    
    return render(request, 'admin/section_content.html', {
        'section': section,
        'section_items': section_items,
        'available_movies': available_movies,
        'available_series': available_series
    })

@staff_member_required
@require_POST
def add_content_to_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    
    # Check if this is a manual selection section
    if section.content_selection_type != 'manual':
        messages.error(request, "Cannot manually add content to an automatic section")
        return redirect('admin-section-content', section_id=section_id)
    
    content_type = request.POST.get('content_type', '').strip()
    content_id = request.POST.get('content_id')
    
    if content_type and content_id:
        # Get the content type model
        if content_type == 'movie':
            model = Movie
            content_type_obj = ContentType.objects.get_for_model(Movie)
        elif content_type == 'series':
            model = Series
            content_type_obj = ContentType.objects.get_for_model(Series)
        else:
            messages.error(request, "Invalid content type")
            return redirect('admin-section-content', section_id=section_id)
        
        # Get the content object
        try:
            content = model.objects.get(id=content_id)
        except model.DoesNotExist:
            messages.error(request, "Content not found")
            return redirect('admin-section-content', section_id=section_id)
        
        # Check if this content is already in the section
        if not SectionItem.objects.filter(
            section=section, 
            content_type=content_type_obj,
            object_id=content_id
        ).exists():
            # Get max position for new content
            max_position = SectionItem.objects.filter(section=section).aggregate(
                max_pos=Max('position')
            )['max_pos']
            position = 0 if max_position is None else max_position + 1
            
            # Add content to section
            SectionItem.objects.create(
                section=section,
                content_type=content_type_obj,
                object_id=content_id,
                position=position
            )
            messages.success(request, f"Added '{content.title}' to '{section.name}'")
        else:
            messages.warning(request, f"'{content.title}' is already in '{section.name}'")
    else:
        messages.error(request, "Content type and ID are required")
    
    return redirect('admin-section-content', section_id=section_id)

@staff_member_required
@require_POST
def remove_content_from_section(request, section_id, item_id):
    section = get_object_or_404(Section, id=section_id)
    section_item = get_object_or_404(SectionItem, id=item_id, section=section)
    
    # Get content name for message
    content_name = str(section_item.content_object) if section_item.content_object else "Unknown"
    
    # Remove content from section
    section_item.delete()
    messages.success(request, f"Removed '{content_name}' from '{section.name}'")
    
    return redirect('admin-section-content', section_id=section_id)

@staff_member_required
@require_POST
def reorder_section_content(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    
    content_order = request.POST.get('content_order', '')
    if content_order:
        section_item_ids = content_order.split(',')
        for position, section_item_id in enumerate(section_item_ids):
            try:
                section_item = SectionItem.objects.get(id=section_item_id, section=section)
                section_item.position = position
                section_item.save()
            except SectionItem.DoesNotExist:
                pass
        
        messages.success(request, "Content order updated successfully")
    
    return redirect('admin-section-content', section_id=section_id)

# Genre Management
@staff_member_required
def admin_genres(request):
    # Get genres with content counts
    genres = Genre.objects.annotate(
        movie_count=Count('movies'),
        series_count=Count('series')
    ).order_by('name')
    
    return render(request, 'admin/genres.html', {
        'genres': genres
    })

@staff_member_required
@require_POST
def create_genre(request):
    name = request.POST.get('name', '').strip()
    if name:
        # Check if genre already exists
        if not Genre.objects.filter(name__iexact=name).exists():
            genre = Genre.objects.create(name=name)
            messages.success(request, f"Genre '{name}' created successfully")
        else:
            messages.error(request, f"Genre '{name}' already exists")
    else:
        messages.error(request, "Genre name is required")
    
    return redirect('admin-genres')

@staff_member_required
@require_POST
def update_genre(request, genre_id):
    genre = get_object_or_404(Genre, id=genre_id)
    
    name = request.POST.get('name', '').strip()
    if name:
        # Check if another genre with this name exists
        if not Genre.objects.filter(name__iexact=name).exclude(id=genre_id).exists():
            genre.name = name
            genre.save()
            messages.success(request, f"Genre updated to '{name}'")
        else:
            messages.error(request, f"Another genre with name '{name}' already exists")
    else:
        messages.error(request, "Genre name is required")
    
    return redirect('admin-genres')

@staff_member_required
@require_POST
def delete_genre(request, genre_id):
    genre = get_object_or_404(Genre, id=genre_id)
    name = genre.name
    
    # Delete the genre
    genre.delete()
    messages.success(request, f"Genre '{name}' deleted successfully")
    
    return redirect('admin-genres')

# Content Management (Movies and Series)
@staff_member_required
def admin_movies(request):
    # Get all movies with their genres
    movies = Movie.objects.all().order_by('title')
    
    # Get all genres for the form
    genres = Genre.objects.all().order_by('name')
    
    return render(request, 'admin/movies.html', {
        'movies': movies,
        'genres': genres
    })

@staff_member_required
@require_POST
def create_movie(request):
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    poster_url = request.POST.get('poster_url', '').strip()
    background_image_url = request.POST.get('background_image_url', '').strip()
    link = request.POST.get('link', '#').strip()
    duration_minutes = request.POST.get('duration_minutes', 0)
    release_year = request.POST.get('release_year')
    genre_ids = request.POST.getlist('genre_ids')
    
    if title and description and poster_url and background_image_url:
        # Create movie
        movie = Movie.objects.create(
            title=title,
            description=description,
            poster_url=poster_url,
            background_image_url=background_image_url,
            link=link,
            duration_minutes=duration_minutes,
            release_year=release_year if release_year else None
        )
        
        # Add genres
        if genre_ids:
            genres = Genre.objects.filter(id__in=genre_ids)
            movie.genres.set(genres)
        
        messages.success(request, f"Movie '{title}' created successfully")
    else:
        messages.error(request, "Title, description, and image URLs are required")
    
    return redirect('admin-movies')

@staff_member_required
@require_POST
def update_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    poster_url = request.POST.get('poster_url', '').strip()
    background_image_url = request.POST.get('background_image_url', '').strip()
    link = request.POST.get('link', '#').strip()
    duration_minutes = request.POST.get('duration_minutes', 0)
    release_year = request.POST.get('release_year')
    genre_ids = request.POST.getlist('genre_ids')
    
    if title and description and poster_url and background_image_url:
        # Update movie
        movie.title = title
        movie.description = description
        movie.poster_url = poster_url
        movie.background_image_url = background_image_url
        movie.link = link
        movie.duration_minutes = duration_minutes
        movie.release_year = release_year if release_year else None
        movie.save()
        
        # Update genres
        genres = Genre.objects.filter(id__in=genre_ids)
        movie.genres.set(genres)
        
        messages.success(request, f"Movie '{title}' updated successfully")
    else:
        messages.error(request, "Title, description, and image URLs are required")
    
    return redirect('admin-movies')

@staff_member_required
@require_POST
def delete_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    title = movie.title
    
    # Delete the movie
    movie.delete()
    messages.success(request, f"Movie '{title}' deleted successfully")
    
    return redirect('admin-movies')

@staff_member_required
def admin_series(request):
    # Get all series with their genres
    series_list = Series.objects.all().order_by('title')
    
    # Get all genres for the form
    genres = Genre.objects.all().order_by('name')
    
    return render(request, 'admin/series.html', {
        'series_list': series_list,
        'genres': genres
    })

@staff_member_required
@require_POST
def create_series(request):
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    poster_url = request.POST.get('poster_url', '').strip()
    background_image_url = request.POST.get('background_image_url', '').strip()
    link = request.POST.get('link', '#').strip()
    seasons = request.POST.get('seasons', 1)
    episodes_count = request.POST.get('episodes_count', 0)
    release_year = request.POST.get('release_year')
    genre_ids = request.POST.getlist('genre_ids')
    
    if title and description and poster_url and background_image_url:
        # Create series
        series = Series.objects.create(
            title=title,
            description=description,
            poster_url=poster_url,
            background_image_url=background_image_url,
            link=link,
            seasons=seasons,
            episodes_count=episodes_count,
            release_year=release_year if release_year else None
        )
        
        # Add genres
        if genre_ids:
            genres = Genre.objects.filter(id__in=genre_ids)
            series.genres.set(genres)
        
        messages.success(request, f"Series '{title}' created successfully")
    else:
        messages.error(request, "Title, description, and image URLs are required")
    
    return redirect('admin-series')

@staff_member_required
@require_POST
def update_series(request, series_id):
    series = get_object_or_404(Series, id=series_id)
    
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    poster_url = request.POST.get('poster_url', '').strip()
    background_image_url = request.POST.get('background_image_url', '').strip()
    link = request.POST.get('link', '#').strip()
    seasons = request.POST.get('seasons', 1)
    episodes_count = request.POST.get('episodes_count', 0)
    release_year = request.POST.get('release_year')
    genre_ids = request.POST.getlist('genre_ids')
    
    if title and description and poster_url and background_image_url:
        # Update series
        series.title = title
        series.description = description
        series.poster_url = poster_url
        series.background_image_url = background_image_url
        series.link = link
        series.seasons = seasons
        series.episodes_count = episodes_count
        series.release_year = release_year if release_year else None
        series.save()
        
        # Update genres
        genres = Genre.objects.filter(id__in=genre_ids)
        series.genres.set(genres)
        
        messages.success(request, f"Series '{title}' updated successfully")
    else:
        messages.error(request, "Title, description, and image URLs are required")
    
    return redirect('admin-series')

@staff_member_required
@require_POST
def delete_series(request, series_id):
    series = get_object_or_404(Series, id=series_id)
    title = series.title
    
    # Delete the series
    series.delete()
    messages.success(request, f"Series '{title}' deleted successfully")
    
    return redirect('admin-series')

# API CRUD Views for React Frontend

# Movie CRUD
@csrf_exempt
@require_http_methods(["GET"])
def api_movie_detail(request, movie_id):
    """API endpoint for single movie detail"""
    try:
        movie = get_object_or_404(Movie, id=movie_id)
        data = {
            'id': movie.id,
            'title': movie.title,
            'description': movie.description,
            'poster_url': movie.poster_url,
            'background_image_url': movie.background_image_url,
            'link': movie.link,
            'duration_minutes': movie.duration_minutes,
            'release_year': movie.release_year,
            'created_at': movie.created_at.isoformat(),
            'genres': [genre.name for genre in movie.genres.all()],
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_create_movie(request):
    """API endpoint for creating a movie"""
    try:
        data = json.loads(request.body)
        movie = Movie.objects.create(
            title=data['title'],
            description=data['description'],
            poster_url=data['poster_url'],
            background_image_url=data['background_image_url'],
            link=data.get('link', '#'),
            duration_minutes=data.get('duration_minutes', 0),
            release_year=data.get('release_year')
        )
        
        # Add genres
        if 'genre_ids' in data and data['genre_ids']:
            genres = Genre.objects.filter(id__in=data['genre_ids'])
            movie.genres.set(genres)
        
        return JsonResponse({'id': movie.id, 'message': 'Movie created successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
def api_update_movie(request, movie_id):
    """API endpoint for updating a movie"""
    try:
        movie = get_object_or_404(Movie, id=movie_id)
        data = json.loads(request.body)
        
        movie.title = data['title']
        movie.description = data['description']
        movie.poster_url = data['poster_url']
        movie.background_image_url = data['background_image_url']
        movie.link = data.get('link', '#')
        movie.duration_minutes = data.get('duration_minutes', 0)
        movie.release_year = data.get('release_year')
        movie.save()
        
        # Update genres
        if 'genre_ids' in data:
            genres = Genre.objects.filter(id__in=data['genre_ids'])
            movie.genres.set(genres)
        
        return JsonResponse({'message': 'Movie updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def api_delete_movie(request, movie_id):
    """API endpoint for deleting a movie"""
    try:
        movie = get_object_or_404(Movie, id=movie_id)
        movie.delete()
        return JsonResponse({'message': 'Movie deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Series CRUD
@csrf_exempt
@require_http_methods(["GET"])
def api_series_detail(request, series_id):
    """API endpoint for single series detail"""
    try:
        series = get_object_or_404(Series, id=series_id)
        data = {
            'id': series.id,
            'title': series.title,
            'description': series.description,
            'poster_url': series.poster_url,
            'background_image_url': series.background_image_url,
            'link': series.link,
            'seasons': series.seasons,
            'episodes_count': series.episodes_count,
            'release_year': series.release_year,
            'created_at': series.created_at.isoformat(),
            'genres': [genre.name for genre in series.genres.all()],
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_create_series(request):
    """API endpoint for creating a series"""
    try:
        data = json.loads(request.body)
        series = Series.objects.create(
            title=data['title'],
            description=data['description'],
            poster_url=data['poster_url'],
            background_image_url=data['background_image_url'],
            link=data.get('link', '#'),
            seasons=data.get('seasons', 1),
            episodes_count=data.get('episodes_count', 0),
            release_year=data.get('release_year')
        )
        
        # Add genres
        if 'genre_ids' in data and data['genre_ids']:
            genres = Genre.objects.filter(id__in=data['genre_ids'])
            series.genres.set(genres)
        
        return JsonResponse({'id': series.id, 'message': 'Series created successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
def api_update_series(request, series_id):
    """API endpoint for updating a series"""
    try:
        series = get_object_or_404(Series, id=series_id)
        data = json.loads(request.body)
        
        series.title = data['title']
        series.description = data['description']
        series.poster_url = data['poster_url']
        series.background_image_url = data['background_image_url']
        series.link = data.get('link', '#')
        series.seasons = data.get('seasons', 1)
        series.episodes_count = data.get('episodes_count', 0)
        series.release_year = data.get('release_year')
        series.save()
        
        # Update genres
        if 'genre_ids' in data:
            genres = Genre.objects.filter(id__in=data['genre_ids'])
            series.genres.set(genres)
        
        return JsonResponse({'message': 'Series updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def api_delete_series(request, series_id):
    """API endpoint for deleting a series"""
    try:
        series = get_object_or_404(Series, id=series_id)
        series.delete()
        return JsonResponse({'message': 'Series deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Genre CRUD
@csrf_exempt
@require_http_methods(["GET"])
def api_genre_detail(request, genre_id):
    """API endpoint for single genre detail"""
    try:
        genre = get_object_or_404(Genre, id=genre_id)
        data = {
            'id': genre.id,
            'name': genre.name,
            'movie_count': genre.movies.count(),
            'series_count': genre.series.count(),
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_create_genre(request):
    """API endpoint for creating a genre"""
    try:
        data = json.loads(request.body)
        genre = Genre.objects.create(name=data['name'])
        return JsonResponse({'id': genre.id, 'message': 'Genre created successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
def api_update_genre(request, genre_id):
    """API endpoint for updating a genre"""
    try:
        genre = get_object_or_404(Genre, id=genre_id)
        data = json.loads(request.body)
        genre.name = data['name']
        genre.save()
        return JsonResponse({'message': 'Genre updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def api_delete_genre(request, genre_id):
    """API endpoint for deleting a genre"""
    try:
        genre = get_object_or_404(Genre, id=genre_id)
        genre.delete()
        return JsonResponse({'message': 'Genre deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Section CRUD
@csrf_exempt
@require_http_methods(["GET"])
def api_section_detail(request, section_id):
    """API endpoint for single section detail"""
    try:
        section = get_object_or_404(Section, id=section_id)
        data = {
            'id': section.id,
            'name': section.name,
            'section_type': section.section_type,
            'content_selection_type': section.content_selection_type,
            'position': section.position,
            'content_count': section.sectionitem_set.count(),
            'auto_genre_id': section.auto_genre.id if section.auto_genre else None,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_create_section(request):
    """API endpoint for creating a section"""
    try:
        data = json.loads(request.body)
        
        # Get max position for new section
        max_position = Section.objects.all().aggregate(max_pos=Max('position'))['max_pos']
        position = 0 if max_position is None else max_position + 1
        
        section = Section.objects.create(
            name=data['name'],
            section_type=data['section_type'],
            content_selection_type=data.get('content_selection_type', 'manual'),
            position=position
        )
        
        # Set auto genre if automatic selection
        if data.get('content_selection_type') == 'automatic' and data.get('auto_genre_id'):
            try:
                genre = Genre.objects.get(id=data['auto_genre_id'])
                section.auto_genre = genre
                section.save()
            except Genre.DoesNotExist:
                pass
        
        return JsonResponse({'id': section.id, 'message': 'Section created successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
def api_update_section(request, section_id):
    """API endpoint for updating a section"""
    try:
        section = get_object_or_404(Section, id=section_id)
        data = json.loads(request.body)
        section.name = data.get('name', section.name)
        section.content_selection_type = data.get('content_selection_type', 'manual')
        # Save settings if present
        if 'settings' in data:
            section.settings = data['settings']
        # Update auto genre if automatic selection
        if data.get('content_selection_type') == 'automatic' and data.get('auto_genre_id'):
            try:
                genre = Genre.objects.get(id=data['auto_genre_id'])
                section.auto_genre = genre
            except Genre.DoesNotExist:
                section.auto_genre = None
        else:
            section.auto_genre = None
        section.save()
        return JsonResponse({'message': 'Section updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def api_delete_section(request, section_id):
    """API endpoint for deleting a section"""
    try:
        section = get_object_or_404(Section, id=section_id)
        section.delete()
        return JsonResponse({'message': 'Section deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_reorder_sections(request):
    """API endpoint for reordering sections"""
    try:
        data = json.loads(request.body)
        section_order = data.get('section_order', '')
        if section_order:
            section_ids = section_order.split(',')
            for position, section_id in enumerate(section_ids):
                try:
                    section = Section.objects.get(id=section_id)
                    section.position = position
                    section.save()
                except Section.DoesNotExist:
                    pass
        return JsonResponse({'message': 'Section order updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Section Content Management
@csrf_exempt
@require_http_methods(["GET"])
def api_section_content(request, section_id):
    """API endpoint for section content"""
    try:
        section = get_object_or_404(Section, id=section_id)
        section_items = SectionItem.objects.filter(section=section).order_by('position')
        
        data = []
        for item in section_items:
            content_data = {
                'id': item.id,
                'position': item.position,
                'content_type': item.content_type.model,
                'content_id': item.object_id,
            }
            
            # Add content details
            if item.content_object:
                content_data['content'] = {
                    'title': item.content_object.title,
                    'poster_url': item.content_object.poster_url,
                    'description': item.content_object.description,
                }
            
            data.append(content_data)
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_add_content_to_section(request, section_id):
    """API endpoint for adding content to section"""
    try:
        section = get_object_or_404(Section, id=section_id)
        data = json.loads(request.body)
        
        content_type = data.get('content_type')
        content_id = data.get('content_id')
        
        if content_type and content_id:
            if content_type == 'movie':
                content_type_obj = ContentType.objects.get_for_model(Movie)
            elif content_type == 'series':
                content_type_obj = ContentType.objects.get_for_model(Series)
            else:
                return JsonResponse({'error': 'Invalid content type'}, status=400)
            
            # Check if content already exists in section
            if not SectionItem.objects.filter(
                section=section, 
                content_type=content_type_obj,
                object_id=content_id
            ).exists():
                # Get max position for new content
                max_position = SectionItem.objects.filter(section=section).aggregate(
                    max_pos=Max('position')
                )['max_pos']
                position = 0 if max_position is None else max_position + 1
                
                # Add content to section
                SectionItem.objects.create(
                    section=section,
                    content_type=content_type_obj,
                    object_id=content_id,
                    position=position
                )
                return JsonResponse({'message': 'Content added to section successfully'})
            else:
                return JsonResponse({'error': 'Content already exists in section'}, status=400)
        else:
            return JsonResponse({'error': 'Content type and ID are required'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def api_remove_content_from_section(request, section_id, item_id):
    """API endpoint for removing content from section"""
    try:
        section_item = get_object_or_404(SectionItem, id=item_id, section_id=section_id)
        section_item.delete()
        return JsonResponse({'message': 'Content removed from section successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_reorder_section_content(request, section_id):
    """API endpoint for reordering section content"""
    try:
        data = json.loads(request.body)
        content_order = data.get('content_order', '')
        if content_order:
            section_item_ids = content_order.split(',')
            for position, section_item_id in enumerate(section_item_ids):
                try:
                    section_item = SectionItem.objects.get(id=section_item_id, section_id=section_id)
                    section_item.position = position
                    section_item.save()
                except SectionItem.DoesNotExist:
                    pass
        return JsonResponse({'message': 'Content order updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Landing Page CRUD
@csrf_exempt
@require_http_methods(["GET"])
def api_landing_page_detail(request, landing_page_id):
    """API endpoint for single landing page detail"""
    try:
        landing_page = get_object_or_404(LandingPage, id=landing_page_id)
        landing_page_sections = LandingPageSection.objects.filter(
            landing_page=landing_page
        ).select_related('section').order_by('position')
        
        data = {
            'id': landing_page.id,
            'name': landing_page.name,
            'is_active': landing_page.is_active,
            'created_at': landing_page.created_at.isoformat(),
            'updated_at': landing_page.updated_at.isoformat(),
            'landingpagesection_set': [
                {
                    'id': lp_section.id,
                    'position': lp_section.position,
                    'section': {
                        'id': lp_section.section.id,
                        'name': lp_section.section.name,
                        'section_type': lp_section.section.section_type,
                        'content_selection_type': lp_section.section.content_selection_type,
                    }
                }
                for lp_section in landing_page_sections
            ]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_create_landing_page(request):
    """API endpoint for creating a landing page"""
    try:
        data = json.loads(request.body)
        landing_page = LandingPage.objects.create(name=data['name'])
        return JsonResponse({'id': landing_page.id, 'message': 'Landing page created successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
def api_update_landing_page(request, landing_page_id):
    """API endpoint for updating a landing page"""
    try:
        landing_page = get_object_or_404(LandingPage, id=landing_page_id)
        data = json.loads(request.body)
        landing_page.name = data['name']
        landing_page.save()
        return JsonResponse({'message': 'Landing page updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def api_delete_landing_page(request, landing_page_id):
    """API endpoint for deleting a landing page"""
    try:
        landing_page = get_object_or_404(LandingPage, id=landing_page_id)
        if landing_page.is_active:
            return JsonResponse({'error': 'Cannot delete active landing page'}, status=400)
        landing_page.delete()
        return JsonResponse({'message': 'Landing page deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_activate_landing_page(request, landing_page_id):
    """API endpoint for activating a landing page"""
    try:
        landing_page = get_object_or_404(LandingPage, id=landing_page_id)
        landing_page.activate()
        return JsonResponse({'message': 'Landing page activated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Landing Page Sections Management
@csrf_exempt
@require_http_methods(["POST"])
def api_add_section_to_landing_page(request, landing_page_id, section_id):
    """API endpoint for adding section to landing page"""
    try:
        landing_page = get_object_or_404(LandingPage, id=landing_page_id)
        section = get_object_or_404(Section, id=section_id)
        
        # Check if section already exists in landing page
        if not LandingPageSection.objects.filter(landing_page=landing_page, section=section).exists():
            # Get max position for new section
            max_position = LandingPageSection.objects.filter(landing_page=landing_page).aggregate(
                max_pos=Max('position')
            )['max_pos']
            position = 0 if max_position is None else max_position + 1
            
            # Add section to landing page
            LandingPageSection.objects.create(landing_page=landing_page, section=section, position=position)
            return JsonResponse({'message': 'Section added to landing page successfully'})
        else:
            return JsonResponse({'error': 'Section already exists in landing page'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def api_remove_section_from_landing_page(request, landing_page_id, section_id):
    """API endpoint for removing section from landing page"""
    try:
        landing_page_section = get_object_or_404(LandingPageSection, landing_page_id=landing_page_id, section_id=section_id)
        landing_page_section.delete()
        return JsonResponse({'message': 'Section removed from landing page successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_reorder_landing_page_sections(request, landing_page_id):
    """API endpoint for reordering landing page sections"""
    try:
        data = json.loads(request.body)
        section_order = data.get('section_order', '')
        if section_order:
            landing_page_section_ids = section_order.split(',')
            for position, landing_page_section_id in enumerate(landing_page_section_ids):
                try:
                    landing_page_section = LandingPageSection.objects.get(id=landing_page_section_id, landing_page_id=landing_page_id)
                    landing_page_section.position = position
                    landing_page_section.save()
                except LandingPageSection.DoesNotExist:
                    pass
        return JsonResponse({'message': 'Section order updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)