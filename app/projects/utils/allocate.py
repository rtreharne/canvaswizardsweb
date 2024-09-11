import pandas as pd
import numpy as np
import pulp
import random
import itertools
import re
from scipy.optimize import linear_sum_assignment

def create_projects_list(sets):

    rows = []
    available = {}

    for set in sets:
        if set.active:
            row = []
            
            for i in range(set.available_for_ug):

                try:
                    prerequisite = set.prerequisite.name
                except:
                    prerequisite = None
                
                rows.append(
                    {
                        "username": set.supervisor.username,
                        "last_name": set.supervisor.last_name,
                        "first_name": set.supervisor.first_name,
                        "email": set.supervisor.email,
                        "department": set.supervisor.department,
                        "keywords": ",".join([x.name for x in set.keywords.all()]),
                        "types": set.type,
                        "prerequisites": prerequisite
                    }

                )

                available[set.supervisor.username] = set.supervisor.projects_UG


    df = pd.DataFrame(rows)

    subset = []

    print("Making sure no more projects than expected for each supervisor ...")
    for key, value in available.items():

        super_set = df[df["username"] == key]


        # randomly select projects from supervisor's available projects
        if len(super_set) > value:
            super_set = super_set.sample(n=value)
        
        subset.append(super_set)

    df = pd.concat(subset)

    # reset index
    df.reset_index(drop=True, inplace=True)

    print(f"Total projects: {len(df)}")

    # make index column
    df["id"] = df.index

    return df

def create_students_list(students):
    rows = []
    for student in students:
        rows.append(
            {
                "id": student.student_id,
                "last_name": student.last_name,
                "first_name": student.first_name,
                "programme": student.programme,
                "types": student.project_types,
                "keywords": student.project_keywords,
                "prerequisites": student.prerequisites,
                "mbiolsci": student.mbiolsci
            }
        )

    df = pd.DataFrame(rows)
    
    return df

def save_sets(sets):
    rows = []
    for set in sets:
        rows.append(
            {
                "username": set.supervisor.username,
                # format keywords as comma separated string (keywords is ManyToMany)
                "keywords": ",".join([x.name for x in set.keywords.all()]),
                "types": set.type,
                "prerequisite": set.prerequisite,
                "available": set.available_for_ug,
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv("sets.csv", index=False)

def save_students(students):
    rows = []
    for student in students:
        rows.append(
            {
                "student_id": student.student_id,
                "programme": student.programme,
                "types": student.project_types,
                "keywords": student.project_keywords,
                "prerequisites": student.prerequisites
            }
        )
    
    df = pd.DataFrame(rows)
    df.to_csv("students.csv", index=False)

def student_project_scores(label, projects, students):
    s_list = []

    for i, s in students.iterrows():
        p_list = []

        list1 = getattr(s, label).split(",")
        
        for j, p in projects.iterrows():
            
            try:
                list2 = getattr(p, label).split(",")
            except:
                list2 = [getattr(p, label)]

            score = score_preference(list1, list2)

            p_list.append(score)

        s_list.append(p_list)

    return np.array(s_list)

def score_preference(pref, lst):
    score = 0
    pref_reverse = pref[::-1]

    for i, item in enumerate(pref_reverse):
        if item in lst:
            score += i + 1

    return score 

def normalize_2d_array(arr):
    min_val = np.min(arr)
    max_val = np.max(arr)
    normalzed_array = (arr - min_val) / (max_val - min_val)
    return normalzed_array

def prerequisite_filter(scores, students, projects):

    new_scores = []

    for i, s in students.iterrows():

        try:
            student_modules = s.prerequisites.split(",")
        except:
            student_modules = []

        new_scores_row = []

        for j, p in projects.iterrows():
            

            prerequisite = p.prerequisites


            if prerequisite is not None:

                if any(prerequisite in word for word in student_modules):

                    new_scores_row.append(scores[i][j])
                else:

                    new_scores_row.append(0)
            else:

                new_scores_row.append(scores[i][j])
       

        new_scores.append(new_scores_row)

    return np.array(new_scores)

def rank_student_projects(combined_scores):
    student_project = []
    for item in combined_scores:
        student_project.append(item.argsort()[::-1].argsort()+1)
    return student_project

def create_problem_and_solve(A):
    A = np.array(A)  # Ensure A is a NumPy array
    # Use the Hungarian algorithm (Kuhn-Munkres algorithm) to find the optimal assignment
    row_ind, col_ind = linear_sum_assignment(A)
    
    # Create a matrix to represent the assignment
    allocation = np.zeros_like(A)
    allocation[row_ind, col_ind] = 1

    result = []

    for i, row in enumerate(allocation):
        # find the index of the 1 in the row
        idx = np.where(row == 1)[0][0]
        result.append([i, idx])

    return result

def get_allocation_coords(prob):

    allocation = []

    for v in prob.variables():
        if v.varValue == 1:
            stringy_coords = v.name.split(',')
            allocation.append([int(re.findall(r"[\d]+|\d+", x)[0]) for x in stringy_coords])


    return(allocation)

def prepare_output(allocation, student_project, projects, students):
    series = []
    score = []

    for [student, project] in allocation:
        
        s = students.iloc[student]
        p = projects.iloc[project]

        # rename s columns with _student suffix
        s = s.add_suffix("_student")

        # rename p columns with _project suffix
        p = p.add_suffix("_project")

        # combine p and s into one series
        series.append(pd.concat([p, s]))

        score.append(student_project[student][project])

    df = pd.DataFrame(series)
    df["score"] = score

    return df