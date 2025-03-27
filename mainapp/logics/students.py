import pandas as pd
from Constants.section_allocation import StudentScorer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mainapp.models import Student
from mainapp.serializers import ExcelFileUploadSerializer


def add_student(
    student_name,
    student_id,
    is_hosteler,
    location,
    dept,
    course,
    branch,
    semester,
    section,
    cgpa,
):
    try:
        student, created = Student.objects.get_or_create(
            student_id=student_id,
            defaults={
                "student_name": student_name,
                "is_hosteler": is_hosteler,
                "location": location,
                "dept": dept,
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
        print(f"Error adding student {student_id}: {str(e)}")  # Debugging
        return {"status": "error", "message": str(e)}


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_student_API(request):
    """
        Add multiple students from an Excel file.
    """
    serializer = ExcelFileUploadSerializer(data=request.data)
    if serializer.is_valid():
        excel_file = serializer.validated_data["file"]

        try:
            data = pd.read_excel(excel_file).fillna("")
            data.columns = data.columns.str.lower()

            if data.empty:
                return Response({"error": "Uploaded file is empty"}, status=400)

            students_list = data.to_dict(orient="records")

            processed_students = StudentScorer(
                students_list
            ).entry_point_for_section_divide()

            failed_rows = []
            required_fields = [
                "student_name",
                "student_id",
                "dept",
                "course",
                "branch",
                "semester",
            ]

            for index, row in enumerate(processed_students):
                missing_fields = [
                    field for field in required_fields if not row.get(field)
                ]
                if missing_fields:
                    failed_rows.append(
                        {
                            "row": index + 1,
                            "error": f"Missing fields: {', '.join(missing_fields)}",
                        }
                    )
                    continue

                student_data = {
                    "student_name": row.get("student_name"),
                    "student_id": row.get("student_id"),
                    "is_hosteller": row.get("is_hosteller"),
                    "location": row.get("location"),
                    "dept": row.get("dept"),
                    "course": row.get("course"),
                    "branch": row.get("branch"),
                    "semester": row.get("semester"),
                    "section": row.get("section"),
                    "cgpa": row.get("cgpa"),
                }

                result = add_student(**student_data)

                if result["status"] != "success":
                    failed_rows.append({"row": index + 1, "error": result["message"]})

            if failed_rows:
                print(f"Some students could not be added: {failed_rows}")
                return Response(
                    {
                        "message": "Some students could not be added",
                        "errors": failed_rows,
                    },
                    status=400,
                )

            return Response({"message": "All students added successfully"}, status=200)

        except Exception as e:
            print(f"Error processing Excel file: {str(e)}")
            return Response({"error": str(e)}, status=400)

    return Response(serializer.errors, status=400)
