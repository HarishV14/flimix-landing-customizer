from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import json

class Content(models.Model):
    """Base model for all content types (movies, series, etc.)"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    poster_url = models.URLField(max_length=1000)
    background_image_url = models.URLField(max_length=1000)
    link = models.CharField(max_length=255, default="#")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return self.title

class Movie(models.Model):
    """Movie content type"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    poster_url = models.URLField(max_length=1000)
    background_image_url = models.URLField(max_length=1000)
    link = models.CharField(max_length=255, default="#")
    created_at = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    release_year = models.PositiveIntegerField(null=True, blank=True)
    # Add specific related_name to avoid conflicts
    genres = models.ManyToManyField('Genre', related_name='movies')
    
    def __str__(self):
        return self.title
    
    def get_content_type(self):
        return "movie"

class Series(models.Model):
    """Series content type"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    poster_url = models.URLField(max_length=1000)
    background_image_url = models.URLField(max_length=1000)
    link = models.CharField(max_length=255, default="#")
    created_at = models.DateTimeField(auto_now_add=True)
    seasons = models.PositiveIntegerField(default=1)
    episodes_count = models.PositiveIntegerField(default=0)
    release_year = models.PositiveIntegerField(null=True, blank=True)
    # Add specific related_name to avoid conflicts
    genres = models.ManyToManyField('Genre', related_name='series')
    
    def __str__(self):
        return self.title
    
    def get_content_type(self):
        return "series"

class Genre(models.Model):
    """Genres for content categorization"""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Section(models.Model):
    """A section in the landing page layout"""
    SECTION_TYPES = [
        ('hero', 'Hero Section'),
        ('carousel', 'Carousel'),
        ('grid', 'Grid'),
        ('featured', 'Featured Content'),
    ]
    
    CONTENT_SELECTION_TYPES = [
        ('manual', 'Manual Selection'),
        ('automatic', 'Automatic Selection'),
    ]
    
    name = models.CharField(max_length=255)
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    position = models.IntegerField(default=0)
    content_selection_type = models.CharField(
        max_length=20, 
        choices=CONTENT_SELECTION_TYPES,
        default='manual'
    )
    
    # For automatic selection
    auto_genre = models.ForeignKey(
        Genre, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="If automatic selection, content will be filtered by this genre"
    )
    
    # Additional settings as JSON
    settings = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['position']
    
    def __str__(self):
        return f"{self.name} ({self.get_section_type_display()})"
    
    def get_content(self):
        """Get content for this section based on selection type"""
        if self.content_selection_type == 'manual':
            # Filter out None content objects (deleted content)
            content_items = []
            for item in self.sectionitem_set.all().order_by('position'):
                if item.content_object is not None:
                    content_items.append(item.content_object)
            return content_items
        elif self.content_selection_type == 'automatic' and self.auto_genre:
            # Get all content with this genre
            movies = Movie.objects.filter(genres=self.auto_genre)
            series = Series.objects.filter(genres=self.auto_genre)
            
            # Combine and sort by created_at (most recent first)
            # This is a simplified approach - in production you'd want to paginate
            movie_list = [(movie, 'movie') for movie in movies]
            series_list = [(series, 'series') for series in series]
            combined = movie_list + series_list
            
            # Sort by created_at (most recent first)
            # Note: This is inefficient for large datasets
            return sorted(combined, key=lambda x: x[0].created_at, reverse=True)
        
        return []

class SectionItem(models.Model):
    """An item in a section, using GenericForeignKey to support different content types"""
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    position = models.IntegerField(default=0)
    
    # Generic relation to content
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        ordering = ['position']
        unique_together = ('section', 'content_type', 'object_id')
    
    def __str__(self):
        content_name = str(self.content_object) if self.content_object else "Unknown"
        return f"{self.section.name} - {content_name} (Pos: {self.position})"

class LandingPage(models.Model):
    """Landing page configuration"""
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    sections = models.ManyToManyField(Section, through='LandingPageSection')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.name} ({status})"
    
    def activate(self):
        """Make this landing page active and deactivate others"""
        LandingPage.objects.exclude(id=self.id).update(is_active=False)
        self.is_active = True
        self.save()
    
    @classmethod
    def get_active(cls):
        """Get the active landing page or create a default one"""
        active = cls.objects.filter(is_active=True).first()
        if not active:
            active = cls.objects.create(name="Default Landing Page", is_active=True)
        return active

class LandingPageSection(models.Model):
    """Association between landing pages and sections with position ordering"""
    landing_page = models.ForeignKey(LandingPage, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    position = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['position']
        unique_together = ('landing_page', 'section')
    
    def __str__(self):
        return f"{self.landing_page.name} - {self.section.name} (Pos: {self.position})"
