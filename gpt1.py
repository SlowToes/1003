from pathlib import Path
import csv
import random
import matplotlib.pyplot as plt

# Function to read student records from the CSV file
def read_student_records(filename):
    students = []
    file_path = Path(__file__).parent / "records.csv"
    with file_path.open("r", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = next(reader)  # Skip header
        for row in reader:
            student = {
                'tutorial_group': row[0],
                'student_id': row[1],
                'name': row[2],
                'school': row[3],
                'gender': row[4],
                'cgpa': float(row[5])
            }
            students.append(student)
    return students

# Function to group students by tutorial group
def group_students_by_tutorial(students):
    tutorial_groups = {}
    for student in students:
        tg = student['tutorial_group']
        if tg not in tutorial_groups:
            tutorial_groups[tg] = []
        tutorial_groups[tg].append(student)
    return tutorial_groups

# Function to check if a student can be added to a team based on the criteria
def can_add_student(team, student, overall_avg_cgpa):
    if not team:
        return True

    team_size = len(team) + 1  # Including the new student

    # Criteria 1: School Affiliation
    school_counts = {}
    for member in team:
        school = member['school']
        school_counts[school] = school_counts.get(school, 0) + 1
    school_counts[student['school']] = school_counts.get(student['school'], 0) + 1
    if max(school_counts.values()) > team_size // 2:
        return False

    # Criteria 2: Gender
    gender_counts = {}
    for member in team:
        gender = member['gender']
        gender_counts[gender] = gender_counts.get(gender, 0) + 1
    gender_counts[student['gender']] = gender_counts.get(student['gender'], 0) + 1
    if max(gender_counts.values()) > team_size // 2:
        return False

    # Criteria 3: CGPA Balance
    avg_cgpa = sum(member['cgpa'] for member in team) / len(team)
    new_avg_cgpa = (avg_cgpa * len(team) + student['cgpa']) / team_size
    if abs(new_avg_cgpa - overall_avg_cgpa) > 0.5:  # CGPA tolerance
        return False

    return True

# Function to form teams using the greedy stochastic algorithm
def form_teams_greedy_stochastic(students_in_group, overall_avg_cgpa):
    team_size = 5
    num_teams = len(students_in_group) // team_size
    teams = [[] for _ in range(num_teams)]

    candidates = students_in_group.copy()
    random.shuffle(candidates)

    while candidates:
        for team in teams:
            if not candidates:
                break
            candidate_pool = [student for student in candidates if can_add_student(team, student, overall_avg_cgpa)]
            if candidate_pool:
                selected_student = random.choice(candidate_pool)
                team.append(selected_student)
                candidates.remove(selected_student)
            elif candidates:  # If no candidates, tolerate imbalances
                selected_student = candidates.pop()
                team.append(selected_student)

    return teams

def evaluate_team_balance(team, overall_avg_cgpa):
    school_counts = {}
    gender_counts = {}
    cgpas = [student['cgpa'] for student in team]

    for student in team:
        school = student['school']
        gender = student['gender']
        school_counts[school] = school_counts.get(school, 0) + 1
        gender_counts[gender] = gender_counts.get(gender, 0) + 1

    school_penalty = max(school_counts.values()) / len(team)
    gender_penalty = max(gender_counts.values()) / len(team)
    avg_cgpa = sum(cgpas) / len(cgpas)
    cgpa_deviation = abs(avg_cgpa - overall_avg_cgpa)

    return (1 - school_penalty) + (1 - gender_penalty) - cgpa_deviation

def attempt_swap(team1, team2, overall_avg_cgpa):
    best_swap = None
    best_improvement = 0

    for student1 in team1:
        for student2 in team2:
            temp_team1 = team1.copy()
            temp_team2 = team2.copy()
            temp_team1.remove(student1)
            temp_team2.remove(student2)
            temp_team1.append(student2)
            temp_team2.append(student1)

            pre_swap_score = evaluate_team_balance(team1, overall_avg_cgpa) + evaluate_team_balance(team2, overall_avg_cgpa)
            post_swap_score = evaluate_team_balance(temp_team1, overall_avg_cgpa) + evaluate_team_balance(temp_team2, overall_avg_cgpa)

            if post_swap_score > pre_swap_score:
                improvement = post_swap_score - pre_swap_score
                if improvement > best_improvement:
                    best_improvement = improvement
                    best_swap = (student1, student2)

    return best_swap

def swap_teams_to_optimize(teams, overall_avg_cgpa):
    swap_made = True
    while swap_made:
        swap_made = False
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                best_swap = attempt_swap(teams[i], teams[j], overall_avg_cgpa)
                if best_swap:
                    student1, student2 = best_swap
                    teams[i].remove(student1)
                    teams[j].remove(student2)
                    teams[i].append(student2)
                    teams[j].append(student1)
                    swap_made = True
    return teams

def write_team_assignments(filename, final_team_assignments):
    output_rows = []
    team_number = 1

    for tg, teams in final_team_assignments.items():
        for team in teams:
            cgpas = [student['cgpa'] for student in team]
            mean_cgpa = sum(cgpas) / len(cgpas)

            for student in team:
                output_row = [
                    student['tutorial_group'],
                    student['student_id'],
                    student['school'],
                    student['name'],
                    student['gender'],
                    student['cgpa'],
                    f'Team {team_number}',
                    mean_cgpa
                ]
                output_rows.append(output_row)
            team_number += 1

    output_file_path = Path(__file__).parent / "balanced_teams.csv"
    with output_file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(['Tutorial Group', 'Student ID', 'School', 'Name', 'Gender', 'CGPA', 'Team Assigned', 'Mean CGPA'])
        writer.writerows(output_rows)

def visualize_team_diversity(teams):
    team_numbers = []
    school_diversity = []
    gender_diversity = []
    cgpa_averages = []

    for team_number, team in enumerate(teams, start=1):
        team_numbers.append(team_number)
        schools = [member['school'] for member in team]
        school_counts = len(set(schools))
        school_diversity.append(school_counts)

        genders = [member['gender'] for member in team]
        gender_counts = len(set(genders))
        gender_diversity.append(gender_counts)

        cgpas = [member['cgpa'] for member in team]
        avg_cgpa = sum(cgpas) / len(cgpas)
        cgpa_averages.append(avg_cgpa)

    plt.figure(figsize=(12, 4))

    plt.subplot(1, 3, 1)
    plt.bar(team_numbers, school_diversity)
    plt.xlabel('Team Number')
    plt.ylabel('Number of Schools Represented')
    plt.title('School Diversity per Team')

    plt.subplot(1, 3, 2)
    plt.bar(team_numbers, gender_diversity)
    plt.xlabel('Team Number')
    plt.ylabel('Number of Genders Represented')
    plt.title('Gender Diversity per Team')

    plt.subplot(1, 3, 3)
    plt.bar(team_numbers, cgpa_averages)
    plt.xlabel('Team Number')
    plt.ylabel('Average CGPA')
    plt.title('Average CGPA per Team')

    plt.tight_layout()
    plt.show()

# Main workflow
if __name__ == "__main__":
    students = read_student_records("records.csv")
    tutorial_groups = group_students_by_tutorial(students)
    
    final_team_assignments = {}

    for tg, students_in_group in tutorial_groups.items():
        overall_avg_cgpa = sum(student['cgpa'] for student in students_in_group) / len(students_in_group)
        teams = form_teams_greedy_stochastic(students_in_group, overall_avg_cgpa)
        optimized_teams = swap_teams_to_optimize(teams, overall_avg_cgpa)
        final_team_assignments[tg] = optimized_teams

    write_team_assignments("balanced_teams.csv", final_team_assignments)
    
    # Uncomment to visualize team diversity
    # visualize_team_diversity([team for teams in final_team_assignments.values() for team in teams])
