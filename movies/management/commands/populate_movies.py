import random
from django.core.management.base import BaseCommand
from movies.models import Movie, Category, MovieInCategory, HeroSettings

SAMPLE_MOVIES = [
    {
        "title": "Dune: Part Two",
        "description": "Paul Atreides unites with the Fremen to wage war against House Harkonnen.",
        "poster_url": "https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/9Gtg2DzBhmYamXBS1hKAhiwbBKS.jpg"
    },
    {
        "title": "Oppenheimer",
        "description": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
        "poster_url": "https://image.tmdb.org/t/p/w500/ptpr0kGAckfQkJeJIt8st5dglvd.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/rLb2cwF3Pazuxaj0sRXQ037tGI1.jpg"
    },
    {
        "title": "The Batman",
        "description": "When the Riddler, a sadistic serial killer, begins murdering key political figures in Gotham, Batman is forced to investigate.",
        "poster_url": "https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/b0PlSFdDwbyK0cf5RxwDpaOJQvQ.jpg"
    },
    {
        "title": "John Wick 4",
        "description": "With the price on his head ever increasing, John Wick uncovers a path to defeating The High Table.",
        "poster_url": "https://image.tmdb.org/t/p/w500/vZloFAK7NmvMGKE7VkF5UHaz0I.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/h8gHn0OzBoaefsYseUByqsmEDMY.jpg"
    },
    {
        "title": "Extraction 2",
        "description": "After barely surviving his grievous wounds from his mission in Bangladesh, Tyler Rake is back as a black ops mercenary.",
        "poster_url": "https://image.tmdb.org/t/p/w500/7gKI9hpEMcZUQpNgKrkDzJpbnNS.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/9m161GawbY3cWxe6txd1NOHTbdg.jpg"
    },
    {
        "title": "Superbad",
        "description": "Two co-dependent high school seniors are forced to deal with separation anxiety after their plan to stage a booze-soaked party goes awry.",
        "poster_url": "https://image.tmdb.org/t/p/original/wtvVhfivpIKePhVtvlZdYwUrLbD.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/uUcsYJgXjpNTcKhzlViDZJ1tE3w.jpg"
    },
    {
        "title": "Barbie",
        "description": "Barbie and Ken are having the time of their lives in the colorful and seemingly perfect world of Barbie Land.",
        "poster_url": "https://image.tmdb.org/t/p/w500/iuFNMS8U5cb6xfzi51Dbkovj7vM.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/ctMserH8g2SeOAnCw5gFjdQF8mo.jpg"
    },
    {
        "title": "Inception",
        "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        "poster_url": "https://image.tmdb.org/t/p/w500/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/s3TBrRGB1iav7gFOCNx3H31MoES.jpg"
    },
    {
        "title": "Interstellar",
        "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
        "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/xu9zaAevzQ5nnrsXN6JcahLnG4i.jpg"
    },
    {
        "title": "The Dark Knight",
        "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological tests of his ability to fight injustice.",
        "poster_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/nMKdUUepR0i5zn0y1T4CsSB5chy.jpg"
    },
    {
        "title": "Pulp Fiction",
        "description": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
        "poster_url": "https://image.tmdb.org/t/p/w500/fIE3lAGcZDV1G6XM5KmuWnNsPp1.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg"
    },
    {
        "title": "Fight Club",
        "description": "An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more.",
        "poster_url": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/hZkgoQYus5ve9vM38mBBDJnUzXG.jpg"
    },
    {
        "title": "The Shawshank Redemption",
        "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "poster_url": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/kXfqcdQKsToO0OUXHcrrNCHDBzO.jpg"
    },
    {
        "title": "The Godfather",
        "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
        "poster_url": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/rSPw7tgCH9c6NqICZef4kZjFOQ5.jpg"
    },
    {
        "title": "The Matrix",
        "description": "When a beautiful stranger leads computer hacker Neo to a forbidding underworld, he discovers the shocking truth--the life he knows is the elaborate deception of an evil cyber-intelligence.",
        "poster_url": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/gynBNzwyaHKtXqlEKKLioNkjKgN.jpg"
    },
    {
        "title": "Forrest Gump",
        "description": "The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.",
        "poster_url": "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/qdIMHd4sEfJSckfVJfKQvisL02a.jpg"
    },
    {
        "title": "Goodfellas",
        "description": "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners Jimmy Conway and Tommy DeVito.",
        "poster_url": "https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/sw7morLZJfLuiVXSDr8mHyyBtta.jpg"
    },
    {
        "title": "The Silence of the Lambs",
        "description": "A young F.B.I. cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer.",
        "poster_url": "https://image.tmdb.org/t/p/w500/uS9m8OBk1A8eM9I042bx8vaz8vx.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/mfwq2nMBzArzQ7Y9RKE8SKeeTkg.jpg"
    },
    {
        "title": "Schindler's List",
        "description": "In German-occupied Poland during World War II, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce after witnessing their persecution by the Nazis.",
        "poster_url": "https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/loRmLlopszkGfcwclSACRvpppNn.jpg"
    },
    {
        "title": "Star Wars: Episode IV - A New Hope",
        "description": "Luke Skywalker joins forces with a Jedi Knight, a cocky pilot, a Wookiee and two droids to save the galaxy from the Empire's world-destroying battle station.",
        "poster_url": "https://image.tmdb.org/t/p/w500/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg",
        "background_image_url": "https://image.tmdb.org/t/p/original/zqkmTXzjkAgXmEWLRsY4UpTWCeo.jpg"
    }
]

DEFAULT_CATEGORIES = [
    {"name": "Trending Now", "position": 0},
    {"name": "Action & Adventure", "position": 1},
    {"name": "Comedy", "position": 2},
    {"name": "Drama", "position": 3},
    {"name": "Sci-Fi & Fantasy", "position": 4}
]

class Command(BaseCommand):
    help = 'Populates the database with sample movies and categories'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))
        
        # Create movies
        movies = []
        for movie_data in SAMPLE_MOVIES:
            movie, created = Movie.objects.get_or_create(
                title=movie_data['title'],
                defaults={
                    'description': movie_data['description'],
                    'poster_url': movie_data['poster_url'],
                    'background_image_url': movie_data['background_image_url'],
                    'link': '#'
                }
            )
            movies.append(movie)
            if created:
                self.stdout.write(f'Created movie: {movie.title}')
            else:
                self.stdout.write(f'Movie already exists: {movie.title}')
        
        # Create categories
        categories = []
        for category_data in DEFAULT_CATEGORIES:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={'position': category_data['position']}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
            else:
                self.stdout.write(f'Category already exists: {category.name}')
        
        # Add movies to categories randomly
        for category in categories:
            # Clear existing movies in category to avoid duplicates
            MovieInCategory.objects.filter(category=category).delete()
            
            # Select 3-6 random movies for each category
            selected_movies = random.sample(movies, min(random.randint(3, 6), len(movies)))
            
            # Add selected movies to category
            for position, movie in enumerate(selected_movies):
                MovieInCategory.objects.create(category=category, movie=movie, position=position)
                self.stdout.write(f'Added {movie.title} to {category.name} at position {position}')
        
        # Create hero settings with a random movie if it doesn't exist
        if not HeroSettings.objects.exists():
            hero_movie = random.choice(movies)
            HeroSettings.objects.create(featured_movie=hero_movie)
            self.stdout.write(f'Created hero settings with movie: {hero_movie.title}')
        
        self.stdout.write(self.style.SUCCESS('Database population completed successfully!')) 