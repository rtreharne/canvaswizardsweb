import io
from celery import shared_task
import pandas as pd
import numpy as np
from .models import Allocation, SupervisorSet, Student
from django.utils.datetime_safe import datetime
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from io import StringIO, BytesIO
import time
from .utils.allocate import *
import pickle



@shared_task
def allocate(allocation_id):
    "Running the allocation algorithm ..."
    allocation = Allocation.objects.get(id=allocation_id)
    sets = SupervisorSet.objects.filter(admin_dept=allocation.round.admin_dept, active=True, supervisor__active=True)

    # Create Projects List
    "Creating the projects list ..."
    projects = create_projects_list(sets)

    students = Student.objects.filter(allocation_round=allocation.round, active=True)
    students = students.order_by('student_id', '-submitted_at').distinct('student_id')
    students = create_students_list(students)

    print(f"Projects: {len(projects)}", f"Students: {len(students)}")

    if len(projects) < len(students):
        allocation.status = "Insufficient projects available."
        allocation.save()
        return "Insufficient projects available."

    # Update allocation status
    allocation.status = "Calculating scores ..."
    allocation.save()

    # Calculate keywords scores
    print("Calculating keywords scores ...")
    keyword_scores = student_project_scores("keywords", projects, students)

    # Calculate type scores
    print("Calculating type scores ...")
    type_scores = student_project_scores("types", projects, students)

    # Combine scores and normalize
    scores = normalize_2d_array(keyword_scores) + normalize_2d_array(type_scores)

    # Prerequisite filter
    print("Filtering prerequisites ...")
    scores = prerequisite_filter(scores, students, projects)

    # Rank scores
    print("Ranking projects ...")
    student_project = rank_student_projects(scores)

    print("Transposing array ...")
    project_student = transpose_array(student_project)

    average_ranking = [np.mean(x) for x in project_student]

    print("Re-reating projects list ...")
    projects = create_projects_list(sets, ranking=average_ranking)

    print(f"Projects: {len(projects)}", f"Students: {len(students)}")

    if len(projects) < len(students):
        allocation.status = "Insufficient projects available."
        allocation.save()
        return "Insufficient projects available."

     # Calculate keywords scores
    print("Calculating keywords scores ...")
    keyword_scores = student_project_scores("keywords", projects, students)

    # Calculate type scores
    print("Calculating type scores ...")
    type_scores = student_project_scores("types", projects, students)

    # Combine scores and normalize
    scores = normalize_2d_array(keyword_scores) + normalize_2d_array(type_scores)

    # Prerequisite filter
    print("Filtering prerequisites ...")
    scores = prerequisite_filter(scores, students, projects)

    # Rank scores (again)
    print("Ranking projects ...")
    student_project = rank_student_projects(scores)

    allocation.status = "Allocating projects ..."
    allocation.save()

    result = create_problem_and_solve(student_project)

    output = prepare_output(result, student_project, projects, students)

    # Get unallocated by cross-referencing id_project of output with id of projects
    unallocated = projects[~projects["id"].isin(output["id_project"])]

    # Save output on allocation object file field
    print("Saving output ...")
    output_file = BytesIO()

    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        # Write each DataFrame to a different worksheet
        output.to_excel(writer, sheet_name='allocation', index=False)
        unallocated.to_excel(writer, sheet_name='unallocated', index=False)

    output_file.seek(0)

    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"output_{timestamp}.xlsx"
    allocation.output.save(filename, output_file)

    allocation.status = "Completed."
    allocation.save()

    # Save allocation results

    # sets = save_sets(sets)
    # students = save_students(students)

    # pickle sets and save as "sets.pkl"
    #with open('sets.pkl', 'wb') as f:
        #pickle.dump(sets, f)

    # pickle students and save as "students.pkl"
    # with open('students.pkl', 'wb') as f:
    #     pickle.dump(students, f)


    return "Done."