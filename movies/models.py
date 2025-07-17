from django.db import models

# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    poster_url = models.URLField(max_length=1000)
    background_image_url = models.URLField(max_length=1000)
    link = models.CharField(max_length=255, default="#")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=255)
    position = models.IntegerField(default=0)
    movies = models.ManyToManyField(Movie, through='MovieInCategory')
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['position']
        verbose_name_plural = 'Categories'

class MovieInCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    position = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['position']
        unique_together = ('category', 'movie')
        
    def __str__(self):
        return f"{self.category.name} - {self.movie.title}"

class HeroSettings(models.Model):
    featured_movie = models.ForeignKey(Movie, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Hero Settings'
        verbose_name_plural = 'Hero Settings'
        
    def __str__(self):
        return f"Hero Settings - {self.featured_movie.title if self.featured_movie else 'No movie selected'}"
