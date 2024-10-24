import csv
import random
import matplotlib.pyplot as plt
from pathlib import Path

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
    # If the team is empty, any student can be added
    if not team:
        return True

    team_size = len(team) + 1  # Including the new student

    # Criteria 1: School Affiliation
    school_counts = {}
    for member in team:
        school = member['school']
        school_counts[school] = school_counts.get(school, 0) + 1
    # Add the new student
    school_counts[student['school']] = school_counts.get(student['school'], 0) + 1
    # Check for majority
    if max(school_counts.values()) > team_size // 2:
        return False

    # Criteria 2: Gender
    gender_counts = {}
    for member in team:
        gender = member['gender']
        gender_counts[gender] = gender_counts.get(gender, 0) + 1
    # Add the new student
    gender_counts[student['gender']] = gender_counts.get(student['gender'], 0) + 1
    # Check for majority
    if max(gender_counts.values()) > team_size // 2:
        return False

    # Criteria 3: CGPA Balance
    # Calculate the average CGPA of the team
    cgpas = [member['cgpa'] for member in team]
    avg_cgpa = sum(cgpas) / len(cgpas)
    # Adding the new student's CGPA
    new_avg_cgpa = (sum(cgpas) + student['cgpa']) / team_size
    # Allowable CGPA deviation (tolerance can be adjusted)
    cgpa_tolerance = 0.5
    if abs(new_avg_cgpa - overall_avg_cgpa) > cgpa_tolerance:
        return False

    return True

# Function to form teams using the greedy stochastic algorithm
def form_teams_greedy_stochastic(students_in_group, overall_avg_cgpa):
    team_size = 5
    num_teams = len(students_in_group) // team_size
    teams = [[] for _ in range(num_teams)]

    # Shuffle students to introduce randomness
    candidates = students_in_group.copy()
    random.shuffle(candidates)

    # Initialize team indices
    team_indices = list(range(num_teams))

    # While there are candidates to assign
    while candidates:
        for team_index in team_indices:
            if not candidates:
                break  # No more candidates to assign
            # Get the team
            team = teams[team_index]

            # Generate candidate students for this team
            candidate_pool = []
            for student in candidates:
                if can_add_student(team, student, overall_avg_cgpa):
                    candidate_pool.append(student)

            if candidate_pool:
                # Randomly select a student from the candidate pool
                selected_student = random.choice(candidate_pool)
                team.append(selected_student)
                candidates.remove(selected_student)
            else:
                # If no suitable candidate, pick any student (tolerate imbalances)
                selected_student = candidates.pop()
                team.append(selected_student)
    return teams

# Function to write the final team assignments to a CSV file with Mean CGPA for each team
def write_team_assignments(filename, final_team_assignments):
    # Prepare data for writing
    output_rows = []
    team_number = 1  # Start numbering globally

    for tg, teams in final_team_assignments.items():
        for team in teams:
            # Calculate the mean CGPA for the current team
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
                    mean_cgpa  # Add mean CGPA for the team
                ]
                output_rows.append(output_row)
            team_number += 1  # Increment team number after each team

    # Write to CSV
    output_file_path = Path(__file__).parent / "balanced_teams.csv"
    with output_file_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(['Tutorial Group', 'Student ID', 'School', 'Name', 'Gender', 'CGPA', 'Team Assigned', 'Mean CGPA'])
        writer.writerows(output_rows)

# Function to visualize team diversity metrics
def visualize_team_diversity(teams):
    team_numbers = []
    school_diversity = []
    gender_diversity = []
    cgpa_averages = []

    for team_number, team in enumerate(teams, start=1):
        team_numbers.append(team_number)
        # School diversity
        schools = [member['school'] for member in team]
        school_counts = len(set(schools))
        school_diversity.append(school_counts)
        # Gender diversity
        genders = [member['gender'] for member in team]
        gender_counts = len(set(genders))
        gender_diversity.append(gender_counts)
        # CGPA average
        cgpas = [member['cgpa'] for member in team]
        avg_cgpa = sum(cgpas) / len(cgpas)
        cgpa_averages.append(avg_cgpa)

    # Plotting
    plt.figure(figsize=(12, 4))

    # School Diversity
    plt.subplot(1, 3, 1)
    plt.bar(team_numbers, school_diversity)
    plt.xlabel('Team Number')
    plt.ylabel('Number of Schools Represented')
    plt.title('School Diversity per Team')

    # Gender Diversity
    plt.subplot(1, 3, 2)
    plt.bar(team_numbers, gender_diversity)
    plt.xlabel('Team Number')
    plt.ylabel('Number of Genders Represented')
    plt.title('Gender Diversity per Team')

    # CGPA Averages
    plt.subplot(1, 3, 3)
    plt.bar(team_numbers, cgpa_averages)
    plt.xlabel('Team Number')
    plt.ylabel('Average CGPA')
    plt.title('Average CGPA per Team')

    plt.tight_layout()
    plt.show()

# Main execution flow
def main():
    # Step 1: Read student records
    students = read_student_records('records.csv')

    # Step 2: Calculate overall average CGPA
    overall_avg_cgpa = sum([s['cgpa'] for s in students]) / len(students)

    # Step 3: Group students by tutorial group
    tutorial_groups = group_students_by_tutorial(students)

    # Step 4: Form teams for each tutorial group
    final_team_assignments = {}
    for tg, students_in_group in tutorial_groups.items():
        teams = form_teams_greedy_stochastic(students_in_group, overall_avg_cgpa)
        final_team_assignments[tg] = teams

    # Step 5: Write team assignments to CSV with Mean CGPA
    write_team_assignments('team_assignments.csv', final_team_assignments)
    # print("Team assignments with mean CGPA have been written to 'team_assignments.csv'.")

    # # Step 6: Visualize diversity metrics for one tutorial group (optional)
    # for tg, teams in final_team_assignments.items():
    #     print(f'Visualization for Tutorial Group {tg}')
    #     visualize_team_diversity(teams)
    #     break  # Visualize only the first tutorial group

if __name__ == '__main__':
    main()
