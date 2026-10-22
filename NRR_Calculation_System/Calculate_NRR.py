def Take_Input():
    Number_Of_Teams = int(input("Enter number of teams: "))
    team_list = []
    for i in range(Number_Of_Teams):
        team_list.append(input(f"Enter team {i + 1} name: "))
    return Number_Of_Teams,team_list
team_names = set()
def Team_Registration():
    Number_Of_Teams,team_list=Take_Input()
    if len(team_list) != Number_Of_Teams:
        raise ValueError("Number of team names does not match")
    for Team_Name in team_list:
        if not Team_Name.strip():
            raise ValueError("Team name cannot be empty")
        if Team_Name in team_names:
            raise ValueError("Duplicate team found")
        team_names.add(Team_Name)
def calculate_overs(overs, wickets):
    completed, balls = overs
    if balls < 0 or balls > 5:
        raise ValueError("Remaining balls must be between 0 and 5")
    if completed < 0 or completed > 20:
        raise ValueError("Completed overs must be between 0 and 20")
    if completed == 20 and balls != 0:
        raise ValueError("No balls can be bowled after 20 overs")
    total_balls = completed * 6 + balls
    # All out before completing 20 overs
    if wickets == 10 and total_balls < 120:
        return 120
    return total_balls

def update_nrr(team, runs_scored, balls_faced, runs_conceded, balls_bowled):
    if balls_faced <= 0 or balls_bowled <= 0:
        raise ValueError("Balls faced and bowled must be greater than zero")
    points_dict.setdefault(team, {"points": 0, "nrr": 0.0})
    # Store cumulative runs and balls to calculate accurate tournament NRR
    stats = points_dict[team]
    stats.setdefault("runs_scored", 0)
    stats.setdefault("balls_faced", 0)
    stats.setdefault("runs_conceded", 0)
    stats.setdefault("balls_bowled", 0)

    stats["runs_scored"] += runs_scored
    stats["balls_faced"] += balls_faced
    stats["runs_conceded"] += runs_conceded
    stats["balls_bowled"] += balls_bowled

    stats["nrr"] = round(stats["runs_scored"] / (stats["balls_faced"] / 6)- stats["runs_conceded"] / (stats["balls_bowled"] / 6),3)
points_dict={}
Each_Team_Played={}
team_stats = {}

def initialize_team(team):
    team_stats.setdefault(team, {
        "matches_played": 0,
        "matches_won": 0,
        "matches_lost": 0,
        "matches_tied": 0,
        "total_points": 0,
        "total_runs_scored": 0,
        "total_runs_conceded": 0,
        "total_balls_faced": 0,
        "total_balls_bowled": 0,
        "nrr": 0.0
    })
def Match_Details(Match_Number,First_Team_Name,Second_Team_Name,First_Team_Runs,First_Team_Wickets,First_Team_Overs_Faced,Second_Team_Runs,Second_Team_Wickets,Second_Team_Overs_Faced):
    teams = frozenset([First_Team_Name, Second_Team_Name])
   
    try:
        if  First_Team_Name not in team_names or  Second_Team_Name not in team_names:
            raise ValueError("Team Name Not Found")
        if First_Team_Name==Second_Team_Name:
            raise ValueError("A team cannot play against itself")
        if Each_Team_Played.get(teams, 0) >= 2:
            raise ValueError("Each team must play every other team exactly twice") 
        first_balls = calculate_overs(First_Team_Overs_Faced, First_Team_Wickets)
        second_balls = calculate_overs(Second_Team_Overs_Faced, Second_Team_Wickets) 
        if first_balls <= 0 or second_balls <= 0:
            raise ValueError("Overs faced must be greater than zero")  
    except ValueError as e:
        print(e)
        return False
    Each_Team_Played[teams] = Each_Team_Played.get(teams, 0) + 1
    points_dict.setdefault(First_Team_Name, {"points": 0, "nrr": 0.0})
    points_dict.setdefault(Second_Team_Name, {"points": 0, "nrr": 0.0})
    if First_Team_Runs > Second_Team_Runs:
        points_dict[First_Team_Name]["points"] += 2
    elif Second_Team_Runs > First_Team_Runs:
        points_dict[Second_Team_Name]["points"] += 2
    else:
        points_dict[First_Team_Name]["points"] += 1
        points_dict[Second_Team_Name]["points"] += 1
    
    update_nrr(First_Team_Name,First_Team_Runs,first_balls,Second_Team_Runs,second_balls)
    update_nrr(Second_Team_Name,Second_Team_Runs,second_balls,First_Team_Runs,first_balls)
    initialize_team(First_Team_Name)
    initialize_team(Second_Team_Name)

    first = team_stats[First_Team_Name]
    second = team_stats[Second_Team_Name]
    # Matches played
    first["matches_played"] += 1
    second["matches_played"] += 1
    # Runs scored and conceded
    first["total_runs_scored"] += First_Team_Runs
    first["total_runs_conceded"] += Second_Team_Runs
    second["total_runs_scored"] += Second_Team_Runs
    second["total_runs_conceded"] += First_Team_Runs

    # Overs for NRR, stored as legal balls
    first["total_balls_faced"] += first_balls
    first["total_balls_bowled"] += second_balls
    second["total_balls_faced"] += second_balls
    second["total_balls_bowled"] += first_balls
    # Match result and points
    if First_Team_Runs > Second_Team_Runs:
        first["matches_won"] += 1
        second["matches_lost"] += 1
        first["total_points"] += 2
    elif Second_Team_Runs > First_Team_Runs:
        second["matches_won"] += 1
        first["matches_lost"] += 1
        second["total_points"] += 2
    else:
        first["matches_tied"] += 1
        second["matches_tied"] += 1
        first["total_points"] += 1
        second["total_points"] += 1
    # Calculate cumulative NRR
    for stats in (first, second):
        stats["nrr"] = round(stats["total_runs_scored"] / (stats["total_balls_faced"] / 6)- stats["total_runs_conceded"] / (stats["total_balls_bowled"] / 6),3)
    return True
def standings():
    teams = list(team_stats.keys())
    # Bubble sort by points, then NRR
    for i in range(len(teams)):
        for j in range(0, len(teams) - i - 1):
            team1 = team_stats[teams[j]]
            team2 = team_stats[teams[j + 1]]
            if (team1["total_points"] < team2["total_points"] or
                (team1["total_points"] == team2["total_points"] and team1["nrr"] < team2["nrr"])):
                teams[j], teams[j + 1] = teams[j + 1], teams[j]
    print("Team".ljust(20),
    "Played".rjust(8),
    "Won".rjust(8),
    "Lost".rjust(8),
    "Tied".rjust(8),
    "Points".rjust(8),
    "Runs Scored".rjust(14),
    "Runs Conceded".rjust(16),
    "NRR".rjust(10))

    for team in teams:
        stats = team_stats[team]
        print(team.ljust(20),
            str(stats["matches_played"]).rjust(8),
            str(stats["matches_won"]).rjust(8),
            str(stats["matches_lost"]).rjust(8),
            str(stats["matches_tied"]).rjust(8),
            str(stats["total_points"]).rjust(8),
            str(stats["total_runs_scored"]).rjust(14),
            str(stats["total_runs_conceded"]).rjust(16),
            f"{stats['nrr']:.3f}".rjust(10))
Team_Registration()
# Each pair of teams must play twice
total_matches = len(team_names) * (len(team_names) - 1)
match_number = 1
while match_number <= total_matches:
    print(f"\nEnter details for Match {match_number}")
    try:
        first_team = input("Enter first team name: ").strip()
        second_team = input("Enter second team name: ").strip()

        first_runs = int(input("Enter first team's runs: "))
        first_wickets = int(input("Enter first team's wickets lost: "))
        first_overs = int(input("Enter completed overs for first team: "))
        first_balls = int(input("Enter remaining legal balls for first team: "))

        second_runs = int(input("Enter second team's runs: "))
        second_wickets = int(input("Enter second team's wickets lost: "))
        second_overs = int(input("Enter completed overs for second team: "))
        second_balls = int(input("Enter remaining legal balls for second team: "))

        Match_Details(
            match_number,
            first_team,
            second_team,
            first_runs,
            first_wickets,
            (first_overs, first_balls),
            second_runs,
            second_wickets,
            (second_overs, second_balls)
        )

        # Continue only if the match was successfully recorded
        teams = frozenset([first_team, second_team])
        if Each_Team_Played.get(teams, 0) == 0:
            continue

        match_number += 1

    except ValueError as e:
        print("Invalid input:", e)

standings()

# A. Team Registration