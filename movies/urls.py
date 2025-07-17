from django.urls import path
from . import views

urlpatterns = [
    path('page-data/', views.page_data, name='page-data'),
    
    # Custom admin URLs
    path('custom-admin/', views.admin_dashboard, name='admin-dashboard'),
    
    # Landing Page Management
    path('custom-admin/landing-pages/', views.admin_landing_pages, name='admin-landing-pages'),
    path('custom-admin/landing-pages/create/', views.create_landing_page, name='create-landing-page'),
    path('custom-admin/landing-pages/activate/<int:landing_page_id>/', views.activate_landing_page, name='activate-landing-page'),
    path('custom-admin/landing-pages/delete/<int:landing_page_id>/', views.delete_landing_page, name='delete-landing-page'),
    path('custom-admin/landing-pages/<int:landing_page_id>/sections/', views.admin_landing_page_sections, name='admin-landing-page-sections'),
    path('custom-admin/landing-pages/<int:landing_page_id>/sections/add/<int:section_id>/', views.add_section_to_landing_page, name='add-section-to-landing-page'),
    path('custom-admin/landing-pages/<int:landing_page_id>/sections/remove/<int:section_id>/', views.remove_section_from_landing_page, name='remove-section-from-landing-page'),
    path('custom-admin/landing-pages/<int:landing_page_id>/sections/reorder/', views.reorder_landing_page_sections, name='reorder-landing-page-sections'),
    
    # Section Management
    path('custom-admin/sections/', views.admin_sections, name='admin-sections'),
    path('custom-admin/sections/create/', views.create_section, name='create-section'),
    path('custom-admin/sections/update/<int:section_id>/', views.update_section, name='update-section'),
    path('custom-admin/sections/delete/<int:section_id>/', views.delete_section, name='delete-section'),
    path('custom-admin/sections/reorder/', views.reorder_sections, name='reorder-sections'),
    path('custom-admin/sections/<int:section_id>/content/', views.admin_section_content, name='admin-section-content'),
    path('custom-admin/sections/<int:section_id>/content/add/', views.add_content_to_section, name='add-content-to-section'),
    path('custom-admin/sections/<int:section_id>/content/remove/<int:item_id>/', views.remove_content_from_section, name='remove-content-from-section'),
    path('custom-admin/sections/<int:section_id>/content/reorder/', views.reorder_section_content, name='reorder-section-content'),
    
    # Genre Management
    path('custom-admin/genres/', views.admin_genres, name='admin-genres'),
    path('custom-admin/genres/create/', views.create_genre, name='create-genre'),
    path('custom-admin/genres/update/<int:genre_id>/', views.update_genre, name='update-genre'),
    path('custom-admin/genres/delete/<int:genre_id>/', views.delete_genre, name='delete-genre'),
    
    # Movie Management
    path('custom-admin/movies/', views.admin_movies, name='admin-movies'),
    path('custom-admin/movies/create/', views.create_movie, name='create-movie'),
    path('custom-admin/movies/update/<int:movie_id>/', views.update_movie, name='update-movie'),
    path('custom-admin/movies/delete/<int:movie_id>/', views.delete_movie, name='delete-movie'),
    
    # Series Management
    path('custom-admin/series/', views.admin_series, name='admin-series'),
    path('custom-admin/series/create/', views.create_series, name='create-series'),
    path('custom-admin/series/update/<int:series_id>/', views.update_series, name='update-series'),
    path('custom-admin/series/delete/<int:series_id>/', views.delete_series, name='delete-series'),
]