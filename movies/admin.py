from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import (
    Movie, Series, Genre, Section, SectionItem, 
    LandingPage, LandingPageSection
)

class SectionItemInline(GenericTabularInline):
    model = SectionItem
    extra = 1
    ct_field = 'content_type'
    ct_fk_field = 'object_id'

class LandingPageSectionInline(admin.TabularInline):
    model = LandingPageSection
    extra = 1

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'duration_minutes', 'created_at')
    search_fields = ('title', 'description')
    filter_horizontal = ('genres',)
    list_filter = ('genres', 'release_year')

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('title', 'seasons', 'episodes_count', 'release_year', 'created_at')
    search_fields = ('title', 'description')
    filter_horizontal = ('genres',)
    list_filter = ('genres', 'release_year')

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'section_type', 'content_selection_type', 'position')
    list_filter = ('section_type', 'content_selection_type')
    search_fields = ('name',)
    inlines = [SectionItemInline]

@admin.register(SectionItem)
class SectionItemAdmin(admin.ModelAdmin):
    list_display = ('section', 'content_object', 'position')
    list_filter = ('section',)

@admin.register(LandingPage)
class LandingPageAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    inlines = [LandingPageSectionInline]

@admin.register(LandingPageSection)
class LandingPageSectionAdmin(admin.ModelAdmin):
    list_display = ('landing_page', 'section', 'position')
    list_filter = ('landing_page', 'section')
