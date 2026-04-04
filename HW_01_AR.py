# Name: Abigail Rillovick
# Course: DS 2500
# Assignment: HW_01
# Date: 1/30/26
# pylint: skip-file
# type: ignore
# import library
import csv

valid_ratings = ['G', 'PG', 'PG-13', 'R']

# PROBLEM 1
def load_pixar_data(filename):
    """
    Loads Pixar films data from a CSV file. 

    Args:
    filename (str): Path to the CSV file containing Pixar films data.
    
    Returns:
    data (list): List of dictionaries with film data.
    """
    data = []
    with open(filename, encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def clean_pixar_data(data):
    """
    Cleans Pixar films data from a CSV file. 
    Removes rows with empty string value in 'film'.
    Converts numeric fields ('run_time', 'rotten_tomatoes', 'metacritic') to float if they are not empty strings.
    
    Args:
    data (list): list of dictionaries 
    
    Returns:
    tuple: a tuple containing:
        - clean_data_list (list): List of dictionaries with cleaned film data.
        - original_count (int): Integer of original number of rows in the CSV file.
        - removed_count (int): Integer of number of rows removed due to missing data.
        - final_count (int): Integer of final number of rows after cleaning.
    """
    original_count = len(data)
    removed_count = 0
    clean_data_list = []

    for row in data:
        if row['film'] == "":
            removed_count += 1
        else:
            # convert fields to float
            if row['rotten_tomatoes'] != "":
                # cast string as float value
                row['rotten_tomatoes'] = (
                    float(row['rotten_tomatoes'])
                )
            else: 
                # set empty string to None
                row['rotten_tomatoes'] = None
            if row['run_time'] != "":
                # cast string as float value
                row['run_time'] = float(row['run_time'])
            else: 
                # set empty string to None
                row['run_time'] = None
            if row['metacritic'] != "":
                # cast string as float value
                row['metacritic'] = (
                    float(row['metacritic'])
                )
            else: 
                # set empty string to None
                row['metacritic'] = None
            clean_data_list.append(row)

    final_count = original_count - removed_count

    return(
        clean_data_list, 
        original_count, 
        removed_count, 
        final_count
        )

# PROBLEM 2
def calculate_rt_score_statistics(data):
    """
    Analyzes Pixar films data to calculate Rotten Tomatoes scores statistics.
    Cannot use sort(), min(), max(), mean(), or sum() functions.
    Can use round() function to round the average score to 1 decimal place.

    Args:
    data (list): List of dictionaries containing cleaned Pixar films data.
    
    Returns:
    dictionary: A dictionary containing the following keys and values:
        - min_score (float): Minimum Rotten Tomatoes score.
        - max_score (float): Maximum Rotten Tomatoes score.
        - avg_score (float): Average Rotten Tomatoes score rounded to 1 decimal place.
    """
    min_score = None
    max_score = None

    score_total = 0.0
    score_count = 0

    for row in data:
        score = row['rotten_tomatoes']
        # Handle None values by skipping them

        if score is None:
            continue
        if min_score is None or score < min_score:
            min_score = score
        if max_score is None or score > max_score:
            max_score = score

        score_total += score
        score_count += 1

    # calculate avg score to 1 decimal place
    avg_score = round(score_total / score_count, 1)

    return {
        "min_score": min_score,
        "max_score": max_score,
        "avg_score": avg_score
    }

# PROBLEM 3
# SETUP
num2month = {
    '01' : 'January',
    '02' : 'February',
    '03' : 'March',
    '04' : 'April',
    '05' : 'May',
    '06' : 'June',
    '07' : 'July',
    '08' : 'August',
    '09' : 'September',
    '10' : 'October',
    '11' : 'November',
    '12' : 'December'
}
# END SETUP

def get_most_popular_release_month(data):
    """
    Returns the most popular release month and the number of films released in that month.
    max() or sort() functions cannot be used.

    Args:
    data (list): List of dictionaries containing cleaned Pixar films data.

    Returns:
    tuple: A tuple containing:
        - most_popular_month (str): The month with the highest number of films released. 
                                    The month is represented as a string (e.g., "January").
        - total_films (int): The total number of films released in that month.
    """
    month_count = {}

    for row in data:
        month = row['release_date'][5:7]
        if month in month_count:
            month_count[month] += 1
        else:
            month_count[month] = 1

    most_popular_month = ''
    total_films = 0

    for month, count in month_count.items():
        if count > total_films:
            total_films = count
            most_popular_month = month

    most_popular_month = num2month[
        most_popular_month
        ]
    
    return (
        most_popular_month,
        total_films
        )

# PROBLEM 4(a)
def get_longest_and_shortest_films(data):
    """
    Analyzes Pixar films data to find the longest and shortest films.
    max(), min(), and sort() functions cannot be used.

    Args:
    data (list): List of dictionaries containing Pixar films data.

    Returns:
    dictionary: A dictionary with the following keys and values:
        - shortest_film (str): The title of the shortest film.
        - longest_film (str): The title of the longest film.
    """
    shortest_time = None
    shortest_film = ""

    longest_time = None
    longest_film = ""

    for row in data:
        # skip None values
        if row['run_time'] is None:
            continue
        if shortest_time is None or (
            row['run_time'] < shortest_time
        ):
            shortest_time = row['run_time']
            shortest_film = row['film']
        if longest_time is None or (
            row['run_time'] > longest_time
        ):
            longest_time = row['run_time']
            longest_film = row['film']
        
    return {
        "shortest_film": shortest_film,
        "longest_film": longest_film
    }

# PROBLEM 4(b)
def get_runtime_category_counts(data):
    """
    Analyzes Pixar films data to categorize runtimes and count occurrences.

    Args:
    data (list): List of dictionaries containing Pixar films data.

    Returns:
    dictionary: A dictionary with runtime categories as keys and their counts as values.
        - 'short': Count of films with runtime < 90 minutes
        - 'medium': Count of films with runtime between 90 and 110 minutes (inclusive)
        - 'long': Count of films with runtime > 110 minutes
    """
    runtime = {
        'short': 0,
        'medium': 0,
        'long': 0
        }
    
    for row in data:

        # skip any None values
        if row['run_time'] is None:
            continue

        if row['run_time'] < 90.0:
            runtime['short'] += 1
        elif row['run_time'] <= 110.0:
            runtime['medium'] += 1
        else:
            runtime['long'] += 1

    return runtime

# PROBLEM 4(c)
def get_runtime_by_rating(data, rating):
    """
    Returns the average runtime of films with a specific rating (e.g., 'G', 'PG', 'PG-13', 'R').
    Returns None if the rating is not valid or if there are no films with that rating.
    Can use round() function to round the average score to 1 decimal place.
    
    Args:
    data (list): List of dictionaries containing Pixar films data.
    rating (str): The film rating to filter by (options can be: 'G', 'PG', 'PG-13', 'R').

    Returns:
    float: The average runtime of films with the specified rating. Rounded to 1 decimal place.
    """
    total_time = 0
    num_films = 0

    # check if rating is valid
    if rating not in valid_ratings:
        return None

    for row in data:
        if row['film_rating'] == rating:

            # check for None values
            if row['run_time'] is not None:

                total_time += row['run_time']
                num_films += 1
        
        # account for potential division by 0
    if num_films == 0:
        return None

    avg_runtime = round(
        total_time / num_films, 1
        )
    return avg_runtime

# PROBLEM 5(a)
def get_films_by_type(data, type_filter):
    """
    Filters the Pixar films data to get a list films by type (either 'original' or 'sequel').
    Sequels are films that are not original and can be the second or later in a series.
    Use remove_punctuation_and_articles function implemented above as a helper function.

    Args:
    data (list): List of dictionaries containing Pixar films data.
    type_filter (str): The type of film to filter by ('original' or 'sequel').

    Returns:
    list: A list of dictionaries containing only original films.
    """
    originals = []
    sequels = []
    past_titles = []

    for row in data:
        # extract title from row
        title = row['film']

        # find important words from titles by splitting words apart
        # remove common words and punctuation, make lowercase
        words = []
        for word in (
            title.lower().replace(',', '').replace('.', '').split()
        ):
            # remove short words
            if len(word) > 3 and word not in ['the', 'and']:
                words.append(word)

        # create variable to set as sequel or not
        is_sequel = False

        # check past titles
        for past_title in past_titles:
            past_words = []

            for word in (
                past_title.lower().replace(',', '').replace('.', '').split()
            ):
                if len(word) > 3 and (
                    word not in ['the', 'and']
                ):
                    past_words.append(word)

            # find word matches
            for word in words:
                if word in past_words:
                    is_sequel = True
                    break

            if is_sequel:
                break

        if is_sequel:
            sequels.append(row)
        else: 
            originals.append(row)
            past_titles.append(title)

    if type_filter == 'original':
        return originals
    elif type_filter == 'sequel':
        return sequels
    else:
        return []

# PROBLEM 5(b)
def calculate_originals_and_sequels_rt_scores(data):
    """
    Calculate the originals and sequals average Rotten Tomatoes scores.
    Uses the get_films_by_type functions to filter the data.
    Use lambda fucntion which uses sum() to calculate the average RT score.
    Can use round() function to round the average score to 1 decimal place.

    Args:
    data (list): List of dictionaries containing Pixar films data.

    Returns:
    dictionary: A dictionary with the following keys and values:
        - original_avg_rt_score (float): Average Rotten Tomatoes score for original films. Rounded to 1 decimal place.
        - sequel_avg_rt_score (float): Average Rotten Tomatoes score for sequels. Rounded to 1 decimal place.
    """

    # find original films
    original_films = get_films_by_type(data, 'original')

    # find sequel films
    sequel_films = get_films_by_type(data, 'sequel')
    
    # avg rt for original films 
    original_scores = [
        film['rotten_tomatoes'] for film in original_films if film['rotten_tomatoes'] is not None
        ]
    original_avg = round(
        sum(original_scores) / len(original_scores), 1
        ) if original_scores else 0

    # avg rt for sequel films
    sequel_scores = [
        film['rotten_tomatoes'] for film in sequel_films if film['rotten_tomatoes'] is not None
        ]
    sequel_avg = round(
        sum(sequel_scores) / len(sequel_scores), 1
        ) if sequel_scores else 0

    return {
        "original_avg_rt_score": original_avg,
        "sequel_avg_rt_score": sequel_avg
    }

# PROBLEM 6
def filter_top_five_films(data):
    """
    Filter the top five films based on their composite scores.
    This function should use lambda function for calculating the composite score.
    Use map() and sorted() to help sort your data based on composite score.

    Args:
    data (list): List of dictionaries containing Pixar films data.

    Returns:
    list: A list of dictionaries containing the top five films with their composite scores.
          The list is sorted in descending order by composite score. The dictionary contains:
            - 'film': The title of the film.
            - 'composite_score': The composite score of the film.
    """

    # create new dictionary with composite scores and handle None values
    films_comp_scores = map(
        lambda film: {
            'film': film['film'],
            'composite_score': (
                0 if film['rotten_tomatoes'] is None or film['metacritic'] is None
                else 0.4 * film['rotten_tomatoes'] + 0.6 * film['metacritic']
            )
        },
        data
    )

    # make films and scores into a list
    new_films = list(films_comp_scores)

    # sort by composite_score in descending order (highest to lowest)
    films_sorted = sorted(
        new_films, key=lambda x: x['composite_score'], reverse=True
        )

    # return top 5 films by score
    return films_sorted[:5]


if __name__ == "__main__":
    print("HW 01: PIXAR FILMS DATA ANALYSIS")

    # Use this main function to call your functions and test them.

    # PROBLEM 1 - calling
    print('\nProblem 1')
    data = load_pixar_data('pixar_films.csv')
    print(f"Loaded {len(data)} rows")
    clean_data, original_count, removed_count, final_count = clean_pixar_data(data)
    print(f"Original: {original_count}, Removed: {removed_count}, Final: {final_count}")
    
    # PROBLEM 2 - calling
    print("\nProblem 2")
    rt_stats = calculate_rt_score_statistics(clean_data)
    print(f"rt statistics: {rt_stats}")

    # Problem 3 - calling
    print("\nProblem 3")
    month, count = get_most_popular_release_month(clean_data)
    print(f"Most popular month: {month}; {count} total films")

    # Problem 4 - calling
    print("\nProblem 4")

    # 4a
    films = get_longest_and_shortest_films(clean_data)
    print(f"Longest film: {films['longest_film']}")
    print(f"Shortest film: {films['shortest_film']}")

    # 4b
    runtimes = get_runtime_category_counts(clean_data)
    print(f"Short runtimes: {runtimes['short']}")
    print(f"Medium runtimes: {runtimes['medium']}")
    print(f"Long runtimes: {runtimes['long']}")

    # 4c
    g_runtime = get_runtime_by_rating(clean_data, 'G')
    print(f"Average runtime for G-rated: {g_runtime}")

    # Problem 5 - calling
    print("\nProblem 5")

    # 5a
    original_films = get_films_by_type(clean_data, 'original')
    sequel_films = get_films_by_type(clean_data, 'sequel')
    print(f"Original films: {original_films}")
    print(f"Sequel films: {sequel_films}")

    # 5b
    all_scores = calculate_originals_and_sequels_rt_scores(clean_data)
    print(f"Original average rt: {all_scores['original_avg_rt_score']}")
    print(f"sequel average rt: {all_scores['sequel_avg_rt_score']}")

    # PROBLEM 6 - calling
    print("\nProblem 6")

    top_films = filter_top_five_films(clean_data)
    print(f"Top 5 films: {top_films}")