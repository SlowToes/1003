# given csv file that contains only students from tut 1 with header included:

from pathlib import Path
import random

def read_student_records(filename):
    file_path = Path(__file__).parent / filename
    with file_path.open("r", encoding="utf-8") as file:
        students = [] # initialise an empty list "students" to store each student row as dicts later
        file.readline() # skip the header
        for line in file: # for each row in the file
            row = line.split(',') # each row now contains lists for each col. for eg: [G-1], [2417], [Truong Minh Chau], ...
            student = { # creating a dict for each student
                'tutorial_group': row[0],
                'student_id': row[1],
                'name': row[2],
                'school': row[3],
                'gender': row[4],
                'cgpa': float(row[5]), # convert cgpa to float
                'team_cgpa': float(0), # initialize future team's average cgpa
                'team_assigned': "Team 0" # initialize future team number
            }
            students.append(student) # store the student dict into the students list
    return students

# logic for code:

# calculate avg cgpa for the tut group -> initialize teams -> assign students to teams

def calc_avg_cgpa(students):
    tut_total_cgpa = float(0)
    student_count = float(0)
    for student in students: # iterate the list
        tut_total_cgpa += student['cgpa']
        student_count += 1
    tut_avg_cgpa = float(tut_total_cgpa / student_count)
    return tut_avg_cgpa

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
            
            for student in candidates:
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

import csv
def write_student_records(teams):
    output_rows = []
    for team in teams:
        for student in team:
            output_row = [
                student['tutorial_group'],
                student['student_id'],
                student['name'],
                student['school'],
                student['gender'],
                student['cgpa'],
                student['team_cgpa'],
                student['team_assigned'],
            ]
            output_rows.append(output_row)

    output_file_path = Path(__file__).parent / "balanced_teams.csv"
    with output_file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(['Tutorial Group', 'Student ID', 'Name', 'School', 'Gender', 'CGPA', 'Team CGPA', 'Team Assigned'])
        writer.writerows(output_rows)

students = read_student_records("minirecords.csv")
teams = form_teams(students)
write_student_records(teams)