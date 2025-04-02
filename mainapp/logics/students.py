import pandas as pd
from Constants.section_allocation import StudentScorer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from mainapp.models import Student
from mainapp.serializers import ExcelFileUploadSerializer
from ..drivers.mongo import MongoDriver
import string
from bson import ObjectId
import io
from django.http import HttpResponse



def addStudent(
    student_name,
    student_id,
    is_hosteller,
    location,
    department,
    course,
    branch,
    year,
    section,
    cgpa,
):
    try:
        student, created = Student.objects.get_or_create(
            student_id=student_id,
            defaults={
                "student_name": student_name,
                "is_hosteller": is_hosteller,
                "location": location,
                "department": department,
                "course": course,
                "branch": branch,
                "semester": semester,
                "section": section,
                "cgpa": cgpa,
            },
        )
        if created:
            return {
                "status": "success",
                "message": "Student added successfully",
                "student": student,
            }
        else:
            return {
                "status": "error",
                "message": f"Student ID {student_id} already exists.",
            }
    except Exception as e:
        print(f"Error adding student {student_id}: {str(e)}") 
        return {"status": "error", "message": str(e)}

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def addStudentAPI(request):
    mongo = MongoDriver()
    files = request.FILES.getlist("file")  
    dept = request.data.get("department")
    course = request.data.get("course")
    branch = request.data.get("branch")
    year = request.data.get("year")
    total_sections = request.data.get("total_sections")

    if not files:
        return Response({"error": "No files uploaded"}, status=400)

    try:
        total_sections = int(total_sections)
        if total_sections <= 0:
            raise ValueError("Total sections must be a positive integer.")
    except ValueError:
        return Response({"error": "Invalid total_sections value"}, status=400)

    all_students = []
    for file in files:
        try:
            data = pd.read_excel(file).fillna("")
            data.columns = data.columns.str.lower()
            if data.empty:
                continue
            students_list = data.to_dict(orient="records")
            all_students.extend(students_list)
        except Exception as e:
            return Response({"error": f"Error processing {file.name}: {str(e)}"}, status=400)

    total_students = len(all_students)
    if total_students == 0:
        return Response({"error": "No students found in uploaded files"}, status=400)

    class_strength = total_students // total_sections
    extra_students = total_students % total_sections  

    scorer = StudentScorer()
    students_with_scores = scorer.assign_scores_to_students(all_students)
    students_with_scores.sort(key=lambda x: x["score"], reverse=True)
    
    def get_section_label(index):
        letters = string.ascii_uppercase
        if index < 26:
            return letters[index]
        else:
            return letters[(index // 26) - 1] + letters[index % 26]
    
    section_labels = [get_section_label(i) for i in range(total_sections)]
    sections = {label: [] for label in section_labels}
    student_index = 0
    
    for section in section_labels:
        while len(sections[section]) < class_strength and student_index < total_students:
            sections[section].append(students_with_scores[student_index])
            student_index += 1
    
    for i in range(extra_students):
        sections[section_labels[i]].append(students_with_scores[student_index])
        student_index += 1

    if "student_distribution" not in mongo.list_collections():
        mongo.db.create_collection("student_distribution")
    mongo.delete_many("student_distribution", {"course": course, "department": dept, "branch": branch, "year": year})
    student_distribution = {
        "course": course,
        "department": dept,
        "branch": branch,
        "year": year,
        "sections": []
    }

    for section, students in sections.items():
        student_distribution["sections"].append({
            "section": section,
            "strength": len(students),
            "students": students
        })

    inserted = mongo.insert_one("student_distribution", student_distribution)
    
    if "section" not in mongo.list_collections():
        mongo.db.create_collection("section")
    mongo.delete_many("section", {"course": course, "department": dept, "branch": branch, "year": year})
    section_structure = {
        "course": course,
        "department": dept,
        "branch": branch,
        "year": year,
        "total_sections": total_sections,
        "sections": [{"section": sec["section"], "strength": sec["strength"]} for sec in student_distribution["sections"]]
    }
    
    mongo.insert_one("section", section_structure)

    return Response({
        "message": "Students processed successfully"
    }, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listSections(request):
    course = request.query_params.get("course")
    department = request.query_params.get("department")
    branch = request.query_params.get("branch")
    year = request.query_params.get("year")

    if not all([course, department, branch, year]):
        return Response({"error": "Missing required parameters (course, department, branch, year)"}, status=400)

    mongo = MongoDriver()

    # Fetch the student_distribution record
    student_distribution_record = mongo.find_one("student_distribution", {
        "course": course,
        "department": department,
        "branch": branch,
        "year": year
    })

    if not student_distribution_record:
        return Response({"error": "No sections found for the specified filters"}, status=404)

    # Extract sections from the record
    sections = [
        { 
            "section": sec["section"]
        }
        for sec in student_distribution_record["sections"]
    ]

    return Response({"mongo_id": str(student_distribution_record["_id"]), "sections": sections}, status=200)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def downloadSections(request, mongo_id):
    mongo = MongoDriver()

    try:
        object_id = ObjectId(mongo_id)
    except Exception:
        return Response({"error": "Invalid Mongo ID"}, status=400)

    section_cursor = mongo.find_one("student_distribution", {"_id": object_id})

    if not section_cursor:
        return Response({"error": "No record found for the given Mongo ID"}, status=404)

    excel_buffer = io.BytesIO()
    writer = pd.ExcelWriter(excel_buffer, engine="openpyxl")

    for section in section_cursor["sections"]:
        section_label = section["section"]
        students = section["students"]

        if not students:
            continue

        df = pd.DataFrame(students)
        sheet_name = f"Section {section_label}"[:31]  # Excel sheet names have a 31-character limit
        df.to_excel(writer, index=False, sheet_name=sheet_name)

    writer.close()
    excel_buffer.seek(0)

    filename = f"{section_cursor['course']}_{section_cursor['department']}_{section_cursor['branch']}_{section_cursor['year']}_Sections.xlsx"

    response = HttpResponse(excel_buffer.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response