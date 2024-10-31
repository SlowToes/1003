# given csv file that contains only students from tut 1 with header included:

from pathlib import Path
import random

def read_student_records(filename):
    file_path = Path(__file__).parent / filename
    tut_grps = {}
    with file_path.open("r", encoding="utf-8") as file:
        # students = [] # initialise an empty list "students" to store each student row as dicts later
        file.readline() # skip the header
        for line in file: # for each row in the file
            row = line.split(',') # each row now contains lists for each col. for eg: [G-1], [2417], [Truong Minh Chau], ...
            student = { # creating a dict for each student
                'tutorial_group': row[0],
                'student_id': row[1],
                'school': row[2],
                'name': row[3],
                'gender': row[4],
                'cgpa': float(row[5]), # convert cgpa to float
                'team_cgpa': float(0), # initialize future team's average cgpa
                'team_assigned': "Team 0" # initialize future team number
            }
            
            tut_grp = student['tutorial_group']
            if tut_grp not in tut_grps:
                tut_grps[tut_grp] = []
            tut_grps[tut_grp].append(student)

    return tut_grps

# logic for code:

# calculate avg cgpa for the tut group -> initialize teams -> assign students to teams

def calc_avg_cgpa(students):
    total_cgpa = student_count = float(0)
    for student in students: # iterate the list
        total_cgpa += student['cgpa']
        student_count += 1
    avg_cgpa = total_cgpa / student_count
    return avg_cgpa

# for this tut grp 1:
# ............................................................
# generate a pool of students that can add to team
# initialize team 1 -> 
# as team is empty, candidate pool is the same as the initial list of all students
# add 1 student to team 1, add 1 student to team 2, ...
# as team 1 is not empty anymore, the candidate pool is reduced, and the student from there is added into team 1.
# repeat for team 2,...
# repeat until all students are added

# inputs will be students: the list of dicts
# we want to output the student dict as stated above with mean cgpa and team assigned included
# target:
# tut grp 1: [
#               team1: [{student1}, {student2}, ..., {student5}], 
#               team2: [{student1}, {student2}, ..., {student5}], 
#               ...
#            ]
# tut grp 2: ...
# initialize list for team 1 to n

def can_add_student(student, team, tut_avg_cgpa):
    if len(team) == 0:
        return True

    next_team_size = len(team) + 1

    # cgpa criteria
    curr_total_cgpa = 0
    for member in team:
        curr_total_cgpa += member['cgpa']
    next_total_cgpa = curr_total_cgpa + student['cgpa']
    next_avg_cgpa = next_total_cgpa / next_team_size
    if abs(next_avg_cgpa - tut_avg_cgpa) > 0.5:
        return False
    
    # school criteria, which is essentially a frequency algorithm
    school_freq = {} # dict for key = school, value = frequency/count
    for member in team:
        school_freq[member['school']] = school_freq.get(member['school'], 0) + 1 # if dont have, return 0+1
    school_freq[student['school']] = school_freq.get(student['school'], 0) + 1 # add the student's school into the freq
    if max(school_freq.values()) > next_team_size // 2:
        return False
    
    # gender criteria
    gender_freq = {}
    for member in team:
        gender_freq[member['gender']] = gender_freq.get(member['gender'], 0) + 1
    gender_freq[student['gender']] = gender_freq.get(student['gender'], 0) + 1 # add the student's gender into the freq
    if max(gender_freq.values()) > next_team_size // 2:
        return False

    return True

def form_teams(students):
    tut_avg_cgpa = calc_avg_cgpa(students)
    team_size = 5
    num_of_teams = len(students) // team_size
    teams = [ [] for _ in range(num_of_teams)]

    candidates = students.copy() # dont change the original list; to pop the list later
    random.shuffle(candidates) # randomize the copied list

    while len(candidates) != 0: # once again, candidates is the list of student dicts in the tut grp
        team_num = 0
        for team in teams: # interate through every teams as we are adding 1 student to every team for 1 round
            team_num += 1
            candidate_pool = [] # we will always have a new list / pool of students to choose from for each team
            
            for student in candidates: # to get the candidate pool
                if can_add_student(student, team, tut_avg_cgpa):
                    candidate_pool.append(student)
            
            if len(candidate_pool) != 0: # simply select a random students from the list of eligible students to add
                selected_student = random.choice(candidate_pool)
                team.append(selected_student)
                candidates.remove(selected_student)
                selected_student['team_assigned'] = f'Team {team_num}'

            elif len(candidate_pool) == 0: # select from the candidates list if pool is empty
                selected_student = candidates.pop() # returns removed student, who is the last person in list
                team.append(selected_student)
                selected_student['team_assigned'] = f'Team {team_num}'

    for team in teams:
        for student in team:
            student['team_cgpa'] = calc_avg_cgpa(team) # get team cgpa

    return teams

# implement a post-processing optimization algorithm that can further refine team balance by slightly adjusting student allocations
# pairwise swap optimization algorithm. iteratively swapping students between teams to see if these swaps improve team balance

def calculate_team_imbalance(team, tut_avg_cgpa):
    # calc cgpa imbalance
    team_cgpa = calc_avg_cgpa(team)
    cgpa_imbalance = abs(team_cgpa - tut_avg_cgpa)

    # calc school imbalance: eg max= 3 - 2; if max is only 2, then 2-2 means no imbalance basically; 
    # however, if 1 of each school, need to account for negative
    school_freq = {}
    for student in team:
        school_freq[student['school']] = school_freq.get(student['school'], 0) + 1
    max_school_count = max(school_freq.values())
    school_imbalance = max_school_count - (len(team) // 2)
    if school_imbalance < 0:
        school_imbalance = 0

    # calc gender imbalance: same logic as school calc
    gender_freq = {}
    for student in team:
        gender_freq[student['gender']] = gender_freq.get(student['gender'], 0) + 1
    max_gender_count = max(gender_freq.values())
    gender_imbalance = max_gender_count - (len(team) // 2)
    if gender_imbalance < 0:
        gender_imbalance = 0

    # simply return the sum for that team of 5
    return cgpa_imbalance + school_imbalance + gender_imbalance

def optimize_teams(teams, tut_avg_cgpa, max_rounds):
    # one iteration of the outer loop attempts all possible swaps between all team pairs 
    # evaluate whether any of these swaps improve balance
    for _ in range(max_rounds): # we simply want to run for a specific number of times, so _ is used just for iteration
        improved = False

        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                team1, team2 = teams[i], teams[j]

                for student1 in team1:
                    for student2 in team2:
                        # Swap students and calculate new imbalance
                        team1.remove(student1)
                        team2.remove(student2)
                        team1.append(student2)
                        team2.append(student1)

                        new_team1_imbalance = calculate_team_imbalance(team1, tut_avg_cgpa)
                        new_team2_imbalance = calculate_team_imbalance(team2, tut_avg_cgpa)

                        # Check if swap improves team balance
                        if new_team1_imbalance + new_team2_imbalance < calculate_team_imbalance(team1, tut_avg_cgpa) + calculate_team_imbalance(team2, tut_avg_cgpa):
                            improved = True
                        else:
                            # Revert swap if no improvement
                            team1.remove(student2)
                            team2.remove(student1)
                            team1.append(student1)
                            team2.append(student2)

        # Stop if no further improvements
        if not improved:
            break

    return teams

def write_student_records(tut_grps):
    output_rows = []
    
    # Prepare header row
    output_rows.append("Tutorial Group,Student ID,School,Name,Gender,CGPA,Team CGPA,Team Assigned")
    
    # Prepare data rows
    for tut_grp, teams in tut_grps.items():
        for team in teams:
            for student in team:
                # Create a comma-separated row for each student
                output_row = ",".join([
                    student['tutorial_group'],
                    student['student_id'],
                    student['school'],
                    student['name'],
                    student['gender'],
                    f"{student['cgpa']:.2f}",
                    f"{student['team_cgpa']:.2f}",
                    student['team_assigned']
                ])
                output_rows.append(output_row)
    
    output_file_path = Path(__file__).parent / "balanced_teams.csv"
    with output_file_path.open("w", encoding="utf-8") as file:
        for row in output_rows:
            file.write(row + "\n")



all_students = read_student_records("records.csv")
optimized_tut_grps = {}

for tut_group, students in all_students.items():
    teams = form_teams(students)
    optimized_teams = optimize_teams(teams, calc_avg_cgpa(students), max_rounds=100) # to get the whole tut grp's cgpa for compare
    optimized_tut_grps[tut_group] = optimized_teams

write_student_records(optimized_tut_grps)