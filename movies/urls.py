from django.urls import path
from . import views

urlpatterns = [
    path('page-data/', views.page_data, name='page-data'),
    
    # Custom admin URLs
    path('custom-admin/', views.admin_dashboard, name='admin-dashboard'),
    
    # Movie management
    path('custom-admin/movies/', views.admin_movies, name='admin-movies'),
    path('custom-admin/movies/create/', views.create_movie, name='create-movie'),
    path('custom-admin/movies/edit/<int:movie_id>/', views.edit_movie, name='edit-movie'),
    path('custom-admin/movies/delete/<int:movie_id>/', views.delete_movie, name='delete-movie'),
    
    # Hero management
    path('custom-admin/hero/', views.admin_hero, name='admin-hero'),
    path('custom-admin/hero/update/', views.update_hero, name='update-hero'),
    
    # Category management
    path('custom-admin/categories/', views.admin_categories, name='admin-categories'),
    path('custom-admin/categories/create/', views.create_category, name='create-category'),
    path('custom-admin/categories/update/<int:category_id>/', views.update_category, name='update-category'),
    path('custom-admin/categories/delete/<int:category_id>/', views.delete_category, name='delete-category'),
    path('custom-admin/category/<int:category_id>/movies/', views.admin_category_movies, name='admin-category-movies'),
    path('custom-admin/category/<int:category_id>/movies/add/<int:movie_id>/', views.add_movie_to_category, name='add-movie-to-category'),
    path('custom-admin/category/<int:category_id>/movies/remove/<int:movie_id>/', views.remove_movie_from_category, name='remove-movie-from-category'),
    path('custom-admin/category/<int:category_id>/movies/reorder/', views.reorder_category_movies, name='reorder-category-movies'),
]