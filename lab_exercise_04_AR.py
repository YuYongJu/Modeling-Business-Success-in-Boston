# LAB EXERCISE 04
# SET UP BEGINS - Do Not Modify
movie_data = [
["Inception", 2010, 8.8, "Sci-Fi", 829.9],
["The Shawshank Redemption", 1994, 9.3, "Drama", 28.3],
["The Godfather", 1972, 9.2, "Crime", 134.8],
["The Dark Knight", 2008, 9.0, "Action", 1005.0],
["The Matrix", 1999, 8.7, "Sci-Fi", 467.2],
["Interstellar", 2014, 8.6, "Sci-Fi", 701.8],
["Forrest Gump", 1994, 8.8, "Drama", 678.2],
["The Lord of the Rings: The Return of the King", 2003, 8.9, "Fantasy",
1142.5],
["Pulp Fiction", 1994, 8.9, "Crime", 213.9],
["The Lion King", 1994, 8.5, "Animation", 968.5],
["Fight Club", 1999, 8.8, "Drama", 101.2],
["Gladiator", 2000, 8.5, "Action", 460.5],
["Titanic", 1997, 7.9, "Romance", 2187.5],
["Jurassic Park", 1993, 8.2, "Adventure", 1045.7],
["The Avengers", 2012, 8.0, "Action", 1518.8],
["Avatar", 2009, 7.8, "Sci-Fi", 2923.7],
["The Silence of the Lambs", 1991, 8.6, "Thriller", 272.7],
["Saving Private Ryan", 1998, 8.6, "War", 482.3],
["The Departed", 2006, 8.5, "Crime", 291.5],
["Whiplash", 2014, 8.5, "Drama", 49.0]
]
# SET UP ENDS - Do Not Modify
# PROBLEM 01
class Movie:
    """
    Represents a movie with basic metadata and performance information.
    Attributes:
    title (str): The title of the movie.
    year (int): The year the movie was released.
    rating (float): The movie's rating (0.0 to 10.0).
    genre (str): The genre of the movie.
    box_office (float): Box office revenue in millions of dollars.
    Methods:
    __init__(): Initializes all movie attributes.
    is_highly_rated(): Returns True if the movie's rating is 8.0 or above,
    False otherwise.
    """
    def __init__(self, title, year, rating, genre, box_office):
        self.title = title
        self.year = year
        self.rating = rating
        self.genre = genre
        self.box_office = box_office

    def is_highly_rated(self):
        if self.rating >= 8.0:
            return True
        else:
            return False

# PROBLEM 02
def create_movie_objects(lsts):
    """
    Takes a list of lists and returns a list of Movie objects
    
    lsts (list): List of lists of movies
    Returns movies (list): List of movie objects
    """
    movie_objects = []
    for lst in lsts:
        movie = Movie(lst[0], lst[1], lst[2], lst[3], lst[4])
        movie_objects.append(movie)
    return movie_objects

# PROBLEM 03
def get_top_rated_movies(movies_lst, n):
    """
    Returns list of titles of the top n movies sorted by rating high to low.
    
    :param movies_lst (list): List of Movie objects
    :param n (int): Top n movies
    :return (list): List of top n movies highest to lowest rating
    """
    sorted_movies = sorted(movies_lst, key=lambda movie: movie.rating, reverse = True)
    
    top_titles = [movie.title for movie in sorted_movies[:n]]

    return top_titles

# PROBLEM 04
def analyze_genre(movie_objects, genre):
    """
    Returns dictionary with genre information with each movie
    If no movies match the genre, returns dictionary with all values set to 0
    
    :param movie_objects: list of Movie objects
    :param genre: string genre
    :return: Dictionary with "count", "avg_rating", "total_box_office", "highly_rated_count"
    key value pairs
    :rtype: Any
    """
    genre_dict = {}
    rating_total = 0
    count = 0
    total_box_office = 0
    highly_rated_count = 0

    for movie in movie_objects:
        if movie.genre == genre:
            rating_total += movie.rating
            count += 1
            total_box_office += movie.box_office

            if movie.is_highly_rated():
                highly_rated_count += 1

    if count == 0:
        genre_dict["count"] = 0
        genre_dict["avg_rating"] = 0
        genre_dict["total_box_office"] = 0
        genre_dict["highly_rated_count"] = 0
    
    else:
        genre_dict["count"] = count
        genre_dict["avg_rating"] = (rating_total / count)
        genre_dict["total_box_office"] = total_box_office
        genre_dict["highly_rated_count"] = highly_rated_count
    
    return genre_dict

def main():

    # Problem 1
    movie = Movie("Inception", 2010, 8.8, "Sci-Fi", 829.9)
    print(movie.title)
    print(movie.is_highly_rated())

    # Problem 2
    movies = create_movie_objects(movie_data)
    print(movies[0].title)

    # Problem 3
    data = [Movie("Inception", 2010, 8.8, "Sci-Fi", 829.9),
            Movie("The Matrix", 1999, 8.7, "Sci-Fi", 467.2),
            Movie("Interstellar", 2014, 8.6, "Sci-Fi", 701.8)]
    top_movies = get_top_rated_movies(data, 2)
    print(top_movies)
    top_movies = get_top_rated_movies(data, 5)
    print(top_movies)

    # Problem 4
    result = analyze_genre(data, "Sci-Fi")
    print(result)

    result = analyze_genre(data, "News")
    print(result)

if __name__ == '__main__':
    main()