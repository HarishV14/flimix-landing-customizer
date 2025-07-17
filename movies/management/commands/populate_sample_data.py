from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from movies.models import (
    Movie, Series, Genre, Section, SectionItem, 
    LandingPage, LandingPageSection
)
import random

class Command(BaseCommand):
    help = 'Populates the database with sample data for the landing page system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        LandingPageSection.objects.all().delete()
        LandingPage.objects.all().delete()
        SectionItem.objects.all().delete()
        Section.objects.all().delete()
        Movie.objects.all().delete()
        Series.objects.all().delete()
        Genre.objects.all().delete()
        
        # Create genres
        self.stdout.write('Creating genres...')
        genres = [
            Genre.objects.create(name='Action'),
            Genre.objects.create(name='Comedy'),
            Genre.objects.create(name='Drama'),
            Genre.objects.create(name='Sci-Fi'),
            Genre.objects.create(name='Horror'),
            Genre.objects.create(name='Romance'),
            Genre.objects.create(name='Thriller'),
            Genre.objects.create(name='Documentary'),
        ]
        
        # Create movies
        self.stdout.write('Creating movies...')
        movies = []
        movie_data = [
            {
                'title': 'The Matrix',
                'description': 'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.',
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg',
                'background_image_url': 'https://wallpapercave.com/wp/wp2378918.jpg',
                'duration_minutes': 136,
                'release_year': 1999,
                'genres': ['Action', 'Sci-Fi']
            },
            {
                'title': 'Inception',
                'description': 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_.jpg',
                'background_image_url': 'https://wallpaperaccess.com/full/1264681.jpg',
                'duration_minutes': 148,
                'release_year': 2010,
                'genres': ['Action', 'Sci-Fi', 'Thriller']
            },
            {
                'title': 'The Shawshank Redemption',
                'description': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BMDFkYTc0MGEtZmNhMC00ZDIzLWFmNTEtODM1ZmRlYWMwMWFmXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_.jpg',
                'background_image_url': 'https://wallpapercave.com/wp/wp8423418.jpg',
                'duration_minutes': 142,
                'release_year': 1994,
                'genres': ['Drama']
            },
            {
                'title': 'The Dark Knight',
                'description': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.',
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_.jpg',
                'background_image_url': 'https://wallpaperaccess.com/full/781011.jpg',
                'duration_minutes': 152,
                'release_year': 2008,
                'genres': ['Action', 'Thriller']
            },
            {
                'title': 'Pulp Fiction',
                'description': 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.',
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BNGNhMDIzZTUtNTBlZi00MTRlLWFjM2ItYzViMjE3YzI5MjljXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_.jpg',
                'background_image_url': 'https://wallpapercave.com/wp/wp3442599.jpg',
                'duration_minutes': 154,
                'release_year': 1994,
                'genres': ['Crime', 'Drama']
            },
            {
                'title': 'Forrest Gump',
                'description': 'The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75, whose only desire is to be reunited with his childhood sweetheart.',
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BNWIwODRlZTUtY2U3ZS00Yzg1LWJhNzYtMmZiYmEyNmU1NjMzXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_.jpg',
                'background_image_url': 'https://wallpapercave.com/wp/wp2012499.jpg',
                'duration_minutes': 142,
                'release_year': 1994,
                'genres': ['Drama', 'Romance']
            },
            {
                'title': 'The Godfather',
                'description': 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.',
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_.jpg',
                'background_image_url': 'https://wallpapercave.com/wp/wp3093582.jpg',
                'duration_minutes': 175,
                'release_year': 1972,
                'genres': ['Crime', 'Drama']
            },
            {
                'title': 'Fight Club',
                'description': 'An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more.',
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BMmEzNTkxYjQtZTc0MC00YTVjLTg5ZTEtZWMwOWVlYzY0NWIwXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_.jpg',
                'background_image_url': 'https://wallpapercave.com/wp/wp4782018.jpg',
                'duration_minutes': 139,
                'release_year': 1999,
                'genres': ['Drama', 'Thriller']
            },
        ]
        
        for movie_info in movie_data:
            movie = Movie.objects.create(
                title=movie_info['title'],
                description=movie_info['description'],
                poster_url=movie_info['poster_url'],
                background_image_url=movie_info['background_image_url'],
                duration_minutes=movie_info['duration_minutes'],
                release_year=movie_info['release_year']
            )
            
            # Add genres
            for genre_name in movie_info['genres']:
                try:
                    genre = Genre.objects.get(name=genre_name)
                except Genre.DoesNotExist:
                    genre = Genre.objects.create(name=genre_name)
                movie.genres.add(genre)
            
            movies.append(movie)
        
        # Create series
        self.stdout.write('Creating series...')
        series_list = []
        series_data = [
            {
                'title': 'Stranger Things',
                'description': 'When a young boy disappears, his mother, a police chief, and his friends must confront terrifying supernatural forces in order to get him back.',
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BN2ZmYjg1YmItNWQ4OC00YWM0LWE0ZDktYThjOTZiZjhhN2Q2XkEyXkFqcGdeQXVyNjgxNTQ3Mjk@._V1_.jpg',
                'background_image_url': 'https://wallpapercave.com/wp/wp1917154.jpg',
                'seasons': 4,
                'episodes_count': 34,
                'release_year': 2016,
                'genres': ['Drama', 'Horror', 'Sci-Fi']
            },
            {
                'title': 'Breaking Bad',
                'description': 'A high school chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine in order to secure his family\'s future.',
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BMjhiMzgxZTctNDc1Ni00OTIxLTlhMTYtZTA3ZWFkODRkNmE2XkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_.jpg',
                'background_image_url': 'https://wallpapercave.com/wp/wp3373292.jpg',
                'seasons': 5,
                'episodes_count': 62,
                'release_year': 2008,
                'genres': ['Crime', 'Drama', 'Thriller']
            },
            {
                'title': 'Game of Thrones',
                'description': 'Nine noble families fight for control over the lands of Westeros, while an ancient enemy returns after being dormant for millennia.',
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BYTRiNDQwYzAtMzVlZS00NTI5LWJjYjUtMzkwNTUzMWMxZTllXkEyXkFqcGdeQXVyNDIzMzcwNjc@._V1_.jpg',
                'background_image_url': 'https://wallpapercave.com/wp/wp1917111.jpg',
                'seasons': 8,
                'episodes_count': 73,
                'release_year': 2011,
                'genres': ['Action', 'Adventure', 'Drama']
            },
            {
                'title': 'The Office',
                'description': 'A mockumentary on a group of typical office workers, where the workday consists of ego clashes, inappropriate behavior, and tedium.',
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BMDNkOTE4NDQtMTNmYi00MWE0LWE4ZTktYTc0NzhhNWIzNzJiXkEyXkFqcGdeQXVyMzQ2MDI5NjU@._V1_.jpg',
                'background_image_url': 'https://wallpapercave.com/wp/wp7097951.jpg',
                'seasons': 9,
                'episodes_count': 201,
                'release_year': 2005,
                'genres': ['Comedy']
            },
            {
                'title': 'The Mandalorian',
                'description': 'The travels of a lone bounty hunter in the outer reaches of the galaxy, far from the authority of the New Republic.',
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BZDhlMzY0ZGItZTcyNS00ZTAxLWIyMmYtZGQ2ODg5OWZiYmJkXkEyXkFqcGdeQXVyODkzNTgxMDg@._V1_.jpg',
                'background_image_url': 'https://wallpapercave.com/wp/wp5296604.jpg',
                'seasons': 3,
                'episodes_count': 24,
                'release_year': 2019,
                'genres': ['Action', 'Adventure', 'Sci-Fi']
            },
            {
                'title': 'Friends',
                'description': 'Follows the personal and professional lives of six twenty to thirty-something-year-old friends living in Manhattan.',
                'poster_url': 'https://m.media-amazon.com/images/M/MV5BNDVkYjU0MzctMWRmZi00NTkxLTgwZWEtOWVhYjZlYjllYmU4XkEyXkFqcGdeQXVyNTA4NzY1MzY@._V1_.jpg',
                'background_image_url': 'https://wallpapercave.com/wp/wp7422004.jpg',
                'seasons': 10,
                'episodes_count': 236,
                'release_year': 1994,
                'genres': ['Comedy', 'Romance']
            },
        ]
        
        for series_info in series_data:
            series = Series.objects.create(
                title=series_info['title'],
                description=series_info['description'],
                poster_url=series_info['poster_url'],
                background_image_url=series_info['background_image_url'],
                seasons=series_info['seasons'],
                episodes_count=series_info['episodes_count'],
                release_year=series_info['release_year']
            )
            
            # Add genres
            for genre_name in series_info['genres']:
                try:
                    genre = Genre.objects.get(name=genre_name)
                except Genre.DoesNotExist:
                    genre = Genre.objects.create(name=genre_name)
                series.genres.add(genre)
            
            series_list.append(series)
        
        # Create sections
        self.stdout.write('Creating sections...')
        
        # Hero section
        hero_section = Section.objects.create(
            name='Featured Content',
            section_type='hero',
            position=0,
            content_selection_type='manual'
        )
        
        # Manual carousels
        trending_section = Section.objects.create(
            name='Trending Now',
            section_type='carousel',
            position=1,
            content_selection_type='manual'
        )
        
        popular_section = Section.objects.create(
            name='Popular Movies',
            section_type='carousel',
            position=2,
            content_selection_type='manual'
        )
        
        # Automatic carousels by genre
        action_genre = Genre.objects.get(name='Action')
        action_section = Section.objects.create(
            name='Action Hits',
            section_type='carousel',
            position=3,
            content_selection_type='automatic',
            auto_genre=action_genre
        )
        
        comedy_genre = Genre.objects.get(name='Comedy')
        comedy_section = Section.objects.create(
            name='Comedy Collection',
            section_type='carousel',
            position=4,
            content_selection_type='automatic',
            auto_genre=comedy_genre
        )
        
        # Create landing page
        self.stdout.write('Creating landing page...')
        landing_page = LandingPage.objects.create(
            name='Main Landing Page',
            is_active=True
        )
        
        # Add sections to landing page
        LandingPageSection.objects.create(landing_page=landing_page, section=hero_section, position=0)
        LandingPageSection.objects.create(landing_page=landing_page, section=trending_section, position=1)
        LandingPageSection.objects.create(landing_page=landing_page, section=popular_section, position=2)
        LandingPageSection.objects.create(landing_page=landing_page, section=action_section, position=3)
        LandingPageSection.objects.create(landing_page=landing_page, section=comedy_section, position=4)
        
        # Add content to manual sections
        self.stdout.write('Adding content to sections...')
        
        # Add hero content (first movie)
        movie_content_type = ContentType.objects.get_for_model(Movie)
        series_content_type = ContentType.objects.get_for_model(Series)
        
        # Add a movie to hero
        SectionItem.objects.create(
            section=hero_section,
            content_type=movie_content_type,
            object_id=movies[0].id,
            position=0
        )
        
        # Add content to trending section (mix of movies and series)
        trending_items = [
            (movies[1], movie_content_type),
            (series_list[0], series_content_type),
            (movies[2], movie_content_type),
            (series_list[1], series_content_type),
            (movies[3], movie_content_type),
        ]
        
        for position, (content, content_type) in enumerate(trending_items):
            SectionItem.objects.create(
                section=trending_section,
                content_type=content_type,
                object_id=content.id,
                position=position
            )
        
        # Add content to popular movies section (movies only)
        for position, movie in enumerate(movies[4:]):
            SectionItem.objects.create(
                section=popular_section,
                content_type=movie_content_type,
                object_id=movie.id,
                position=position
            )
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!')) 