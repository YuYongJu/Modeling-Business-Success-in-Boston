# HW 02 Abigail Rillovick
# 2/27/2026
import csv
import math
import matplotlib.pyplot as plt

ABBR_MAP = {
"Arsenal": "ARS",
"Aston Villa": "AVL",
"Brighton and Hove Albion": "BHA",
"Bristol City": "BCFC",
"Chelsea": "CHEE",
"Everton": "EFC",
"Leicester City": "LCFC",
"Liverpool": "LFC",
"Manchester City": "MCFC",
"Manchester United": "MUFC",
"Tottenham Hotspur": "THFC",
"West Ham United": "WHU"
}

COLOR_MAP = {
"Arsenal": "red",
"Aston Villa": "lightskyblue",
"Brighton and Hove Albion": "mediumblue",
"Bristol City": "darkred",
"Chelsea": "blue",
"Everton": "darkblue",
"Leicester City": "orange",
"Liverpool": "orangered",
"Manchester City": "steelblue",
"Manchester United": "yellow",
"Tottenham Hotspur": "navy",
"West Ham United": "brown"
}

class Team:
    # class attribute shared by all instances
    def __init__(self, name):
        """ instance attributes, unique to each object """
        self.name = name
        self.goals = []

    def add_goals(self, goals):
        """ appends given goals to team's list of goals """
        self.goals.append(goals)
        return self.goals

    def get_total_goals(self):
        """ returns total goals of all the goals in the goals list """
        total = sum(self.goals)
        return total
    
    def __str__(self):
        """ return a string you'd like to be used when calling print()"""
        return(f"Team: {self.name} with {self.get_total_goals()} total goals.")
    

def create_team_objects_from_csv():
    team_objects = []
    with open("wsl_goals_2324.csv", "r") as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            # create a Team object corresponding to the given team
            team = Team(name = row[0])
            # If a team didn’t score any goals, it shows up in the .csv file as empty. 
            # Convert those to zeroes to ensure correct computations.
            for g in row[1:]:
                team.add_goals(float(g) if g != "" else 0)
            team_objects.append(team)

    # have the function return a list of all Team objects.
    return team_objects

# Part 2
# 1) Write a function called get_team_with_most_goals that takes in a list of
# team objects as a parameter and returns a tuple consisting of the name 
# and total goals of the team that scored the most goals in the season

def get_team_with_most_goals(teams):
    """Takes a list of team objects and returns tuple of the name and total 
    goals of the team that scored the most goals in the season
    Parameter: teams (list): list of Team objects
    Return: team_most_goals (tuple): Team name and number of goals with most goals """
    team_most_goals = ("", 0)
    for team in teams:
        if team.get_total_goals() >= team_most_goals[1]:
            team_most_goals = (team.name, team.get_total_goals())
    return team_most_goals

# 2) Write a function called get_mean_season_goals that takes in a list of
# team objects as a parameter and returns the average (mean) across 
# teams of total goals scored during the season. Only use built-in Python functions.
def get_mean_season_goals(teams):
    """Calculates average (mean) number of goals across all teams in a season
    Parameters: teams (lists): list of Team objects
    Returns: avg_goals (int): average goals for season"""
    total_goals = 0

    for team in teams:
        total_goals += team.get_total_goals()

    avg_goals = total_goals / len(teams)

    return avg_goals

# 3) Write a function called get_variance_season_goals that takes in a list
# of team objects as a parameter and returns the population variance
#  of total goals scored during the season.Only use built-in Python functions
def get_variance_season_goals(teams):
    """Calculates population variance of total goals scored 
    by all teams during a season
    Parameters: teams (list): list of Team objects
    Return: variance (int): population variance of total goals"""
    mean = get_mean_season_goals(teams)
    variance = sum((team.get_total_goals() - mean) ** 2 for team in teams) / len(teams)
    return variance

# 4) Write a function called get_standard_deviation_season_goals that
# takes in a list of team objects as a parameter and returns the population standard
# deviation of total goals scored during the season. 
# Inside this function you are allowed to use the math.sqrt function.
def get_standard_deviation_season_goals(teams):
    """Calculates population standard deviation of the total goals
    scored during the season
    Parameters: teams (list): a list of Team objects
    Returns: std_dev (float): population standard deviation of total goals """
    std_dev = math.sqrt(get_variance_season_goals(teams))
    return std_dev

# 5) Write a function called get_median_for_team that takes in a team name
# and a list of team objects as parameters and returns the median of goals
# scored by the specified team. Use “Arsenal” as the team name when calling this 
# function from main. Only use built-in Python functions.
def get_median_for_team(name, teams):
    """Returns median of goals scored by a specific team
    Parameters: name (str): team name
                teams (list): list of teams objects
    Returns: median (int): median number of goals scored by specified team"""
    goal_list = []
    for team in teams:
        if team.name == name:
            goal_list = sorted(team.goals)
            break

    n = len(goal_list)
    mid_index = n // 2

    if n % 2 == 0:
        median = (goal_list[mid_index - 1] + goal_list[mid_index]) / 2
    else: 
        median = goal_list[mid_index]

    return median

# 6) Write a function called get_mode_for_team that takes in a team name
# and a list of team objects as parameters and returns the mode of goals
#  scored by the specified team. 
# You can assume that every team has exactly one mode (unimodal). 
# Use “Tottenham Hotspur” as the team name when calling this function from main. 
# Only use built-in Python functions.
def get_mode_for_team(name, teams):
    """Returns mode of goals scored by specified team
    Parameters: name (str): team name
                teams (list): list of Team objects
    Returns: mode (int): mode of goals scored by specified team"""
    goals_list = []
    for team in teams:
        if team.name == name:
            goals_list = team.goals
            break
    
    mode = goals_list[0]
    highest_count = 0

    for goal in goals_list:
        count = goals_list.count(goal)
        if count > highest_count:
            highest_count = count
            mode = goal
    
    return mode

# 7) Write a function called get_most_consistent_team that takes in a list of
# team objects as a parameter and returns a tuple consisting of the name 
# and coefficient of variation of the team with the most consistent goal-scoring
#  pattern. The coefficient of variation is calculated by dividing the standard 
# deviation by the mean for each team -- the team with the lowest value is the most 
# consistent. If multiple teams have the same lowest coefficient of variation, 
# return the first one encountered.
# Note: The coefficient of variation gives you relative consistency 
# i.e., how much a team's performance varies as a percentage of their typical 
# performance. This is much more meaningful for comparing teams with different 
# scoring capabilities as it is a normalized measure.

def get_most_consistent_team(teams):
    """Finds name and coefficient of variation for team with the most 
    consistent goal-scoring pattern
    Parameters: teams (list): list of Team objects
    Returns: most_consistent (tuple): contains team name and coeff. of variation"""
    most_consistent_team = ("", 100000000000.0)

    for team in teams:
        mean = team.get_total_goals() / len(team.goals)
        var = sum((goal - mean) ** 2 for goal in team.goals) / len(team.goals)
        std_dev = var ** 0.5
        cv = float(std_dev / mean)

        if cv < most_consistent_team[1]:
            most_consistent_team = (team.name, cv)

    return most_consistent_team

# 8) Write a function called get_longest_streak_team that takes in a list of
# team objects as a parameter and returns a tuple consisting of the name and streak
# length of the team with the longest consecutive streak of games 
# where they scored at least 2 goals a game.
def get_longest_streak_team(teams):
    """Finds the team and length of streak for the team with the longest 
    consecutive streak of games scoring at least 2 goals a gam
    Parameters: teams (list): list of Team objects
    Returns: longest_streak_team (tuple): tuple with name of team and streak"""
    longest_streak_team = ("", 0)

    for team in teams:
        current_streak = 0
        best_streak = 0
        
        for goals in team.goals:
            if goals >= 2:
                current_streak += 1
                if current_streak > best_streak:
                    best_streak = current_streak
            else:
                current_streak = 0

        if best_streak > longest_streak_team[1]:
            longest_streak_team = (team.name, best_streak)

    return longest_streak_team

# 9) Write a function called get_most_improved_mean_goals_team that 
# takes in a list of team objects as a parameter and returns a tuple consisting 
# of the name and improvement in mean goals of the team that improved their 
# average goals per game the most from the first half to the second half of 
# the season (you can assume that the season has a known fixed length equal 
# to the number of games in the original data table).
def get_most_improved_mean_goals_team(teams):
    """Returns the name and improvement in mean goals of the team that improved
    their average goals per game the most from the first half to the second 
    half of the season 
    Parameters: teams (list): list of Team objects
    Returns: most_improved (tuple): tuple containing name of team and 
            improvement in mean goals for most improved"""
    season_length = len(teams[0].goals)
    half = season_length // 2
    most_improved = ("", 0)
    # find mean for first half
    for team in teams:
        first_half = team.goals[:half]
        second_half = team.goals[half:]
        first_mean = sum(first_half) / len(first_half)
        second_mean = sum(second_half) / len(second_half)
        improvement = second_mean - first_mean

        if improvement > most_improved[1]:
            most_improved = (team.name, improvement)

    return most_improved

# 10) Write a function called plot_teams that takes in a list of team objects as a 
# parameter and generates an animated scatter plot of each team’s goal progression
# throughout the 2023-2024 season. For each game of the season, the function should
# render a new plot showing all teams’ positions, updating each team’s x-value by the
# number of goals they scored in that game. When rendered in sequence, the plots should 
# look like a mini-animation.
def plot_teams(teams):
    """Generates an animated scatter plot of each team's in teams goal progression
     throughout the 2023-2024 season. Renders a new plot for each game of the 
      season showing all the teams' positions, updating each team's x-value by 
       the number of goals they scored in that game.
        Parameters: teams (list): list of Team objects
        Returns: None """
    season_length = len(teams[0].goals)
    y_pos = {team.name: i for i, team in enumerate(teams)}

    plt.figure(figsize=(12, 6))
    plt.show(block=False)

    for game in range(season_length):
        plt.clf()

        for team in teams:
            cum_goals = sum(team.goals[:game + 1])
            y = y_pos[team.name]

            plt.scatter(cum_goals, y, color=COLOR_MAP[team.name], label = team.name, s=100)

        plt.yticks(list(y_pos.values()), 
                   [ABBR_MAP[name] for name in y_pos.keys()])
        plt.xlabel("Cumulative Goals")
        plt.ylabel("Team")
        plt.title("WSL 2023-2024 Season Goal Progression")
        plt.legend(bbox_to_anchor=(1.05, 1), loc="right")
        plt.tight_layout()
        plt.pause(0.5)

    plt.show(block=True)

if __name__ == '__main__':
    teams = create_team_objects_from_csv()

    for team in teams:
        print(team)

    # 1) get team with most goals
    print("Team with most goals: ", get_team_with_most_goals(teams))

    # 2) calculate mean of season goals
    print("Mean of season goals: ", get_mean_season_goals(teams))

    # 3) calculate variance of season goals
    print("Variance of season goals: ", get_variance_season_goals(teams))

    # 4) calculate standard deviation of season goals
    print("Standard deviation of season goals: ", get_standard_deviation_season_goals(teams))

    # 5) find median of goals for specified team
    print("Median of goals scored by Arsenal", get_median_for_team("Arsenal", teams))

    # 6) find mode of goals for specified team
    print("Mode of goals scored by Tottenham Hotspur", get_mode_for_team("Tottenham Hotspur", teams))

    # 7) find most consistent team
    print("Most consistent team: ", get_most_consistent_team(teams))
    
    # 8) find longest streak team
    print("Longest streak team: ", get_longest_streak_team(teams))

    # 9) find most improved team
    print("Most improved team: ", get_most_improved_mean_goals_team(teams))

    # 10) plot teams
    plot_teams(teams)