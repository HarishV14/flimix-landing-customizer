from django.contrib import admin
from .models import Movie, Category, MovieInCategory, HeroSettings

class MovieInCategoryInline(admin.TabularInline):
    model = MovieInCategory
    extra = 1

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'position')
    inlines = [MovieInCategoryInline]

@admin.register(HeroSettings)
class HeroSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'featured_movie')
    
    def has_add_permission(self, request):
        # Only allow one instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
