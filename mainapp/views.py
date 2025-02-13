from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .drivers.mongodb_driver import MongoDriver
from .drivers.postgres_driver import PostgresDriver
from .models import Room, Teacher, Subject, TeacherSubject, Student
from .serializers import (
    RoomSerializer,
    TeacherSerializer,
    SubjectSerializer,
    ExcelFileUploadSerializer,
)
import os
from GA.__init__ import run_timetable_generation
from Constants.section_allocation import StudentScorer
import pandas as pd
import json
from django.views.decorators.csrf import csrf_exempt
from .drivers.converter import csv_to_json
from Constants.is_conflict import IsConflict
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    Authenticate a teacher using email and return JWT tokens.
    """
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "").strip()

    if not email or not password:
        return Response({"error": "Email and password are required."}, status=400)

    user = User.objects.filter(email=email).first()

    if not user:
        return Response({"error": "Invalid email or password."}, status=401)

    # Authenticate using username
    user = authenticate(username=user.username, password=password)

    if not user:
        return Response({"error": "Invalid email or password."}, status=401)

    teacher = Teacher.objects.filter(user=user).first()
    if not teacher:
        return Response({"error": "Teacher account not found."}, status=404)

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "message": "Login successful",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "teacher": {
                "teacher_type": teacher.teacher_type,
            },
        },
        status=200,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getSpecificTeacher(request):
    """
    Retrieve the details of the authenticated teacher.
    """
    user = request.user
    teacher = Teacher.objects.filter(user=user).first()

    if not teacher:
        return Response({"error": "Teacher account not found."}, status=404)

    subject_codes = TeacherSubject.get_teacher_subjects(teacher.teacher_code)

    subject_names = list(
        Subject.objects.filter(subject_code__in=subject_codes).values_list(
            "subject_name", flat=True
        )
    )

    return Response(
        {
            "id": teacher.id,
            "name": user.get_full_name(),
            "email": user.email,
            "teacher_code": teacher.teacher_code,
            "phone": teacher.phone,
            "department": teacher.department,
            "designation": teacher.designation,
            "working_days": teacher.working_days,
            "preferred_subjects": subject_names,
        },
        status=200,
    )


def generateTimetable():
    output = run_timetable_generation()
    return output


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_timetable(request):
    """
    Generate a timetable using the provided data.
    """
    try:
        timetable = generateTimetable()
        print(timetable)
        return Response(timetable, status=200)
    except Exception as e:
        return Response(
            {"error": f"Failed to generate timetable: {str(e)}"}, status=500
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def mongo_status(request):
    """
    Check MongoDB connection status.
    """
    try:
        mongo_driver = MongoDriver()
        collections = mongo_driver.db.list_collection_names()
        return JsonResponse({"mongodb": "Connected", "collections": collections})
    except Exception as e:
        return JsonResponse({"mongodb": "Not Connected", "error": str(e)})


@api_view(["GET"])
@permission_classes([AllowAny])
def postgres_status(request):
    """
    Check PostgreSQL connection status.
    """
    try:
        postgres_driver = PostgresDriver(
            dbname=os.getenv("POSTGRES_NAME"),
            user=os.getenv("POSTGRES_USER"),
            host=os.getenv("POSTGRES_HOST"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port=os.getenv("POSTGRES_PORT"),
            options="-c search_path=public",
            logger=None,
        )
        query = "SELECT 1;"  # Simple query to validate the connection
        result = postgres_driver.execute_query(query)
        return JsonResponse({"postgresql": "Connected", "result": result})
    except Exception as e:
        return JsonResponse({"postgresql": "Not Connected", "error": str(e)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getRooms(request):
    """
    Retrieve a list of all rooms.
    """
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def addRoom(request):
    """
    Add one or multiple rooms.
    """
    data = request.data if isinstance(request.data, list) else [request.data]
    added_rooms = []
    errors = []

    for room_data in data:
        existing_room = Room.objects.filter(
            room_code=room_data.get("room_code")
        ).first()
        if existing_room:
            errors.append(
                {
                    "room_data": room_data,
                    "error": f"Room with code {room_data.get('room_code')} already exists",
                }
            )
            continue

        serializer = RoomSerializer(data=room_data)
        if serializer.is_valid():
            serializer.save()
            added_rooms.append(serializer.data)
        else:
            errors.append({"room_data": room_data, "errors": serializer.errors})

    if errors:
        return Response(
            {"added_rooms": added_rooms, "errors": errors},
            status=400 if not added_rooms else 207,
        )
    return Response(added_rooms, status=201)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateRoom(request, pk):
    """
    Update an existing room by ID.
    """
    try:
        room = Room.objects.get(id=pk)

        new_room_code = request.data.get("room_code")
        if (
            new_room_code
            and Room.objects.filter(room_code=new_room_code).exclude(id=pk).exists()
        ):
            return Response(
                {
                    "error": f"Room code '{new_room_code}' is already assigned to another room."
                },
                status=400,
            )

        serializer = RoomSerializer(instance=room, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)
    except Room.DoesNotExist:
        return Response({"error": "Room not found"}, status=404)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteRoom(request, pk):
    """
    Delete a room by ID.
    """
    try:
        room = Room.objects.get(id=pk)
        room.delete()
        return Response({"message": "Room deleted successfully"}, status=200)
    except Room.DoesNotExist:
        return Response({"error": "Room not found"}, status=404)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getTeachers(request):
    """
    Retrieve a list of all teachers along with their preferred subjects.
    """
    teachers = Teacher.objects.all()
    serializer = TeacherSerializer(teachers, many=True)
    return Response(serializer.data, status=200)


@api_view(["POST"])
@permission_classes([AllowAny])
def addTeacher(request):
    """
    Add a new teacher, generate a unique teacher_code & password,
    map preferred subjects in JSONField, and send credentials via email.
    """
    teacher_data = request.data

    email = teacher_data.get("email", "").strip().lower()
    full_name = teacher_data.get("name", "").strip()

    if not email or not full_name:
        return Response({"error": "Email and Name are required."}, status=400)

    existing_user = User.objects.filter(email=email).first()
    if existing_user:
        return Response({"error": "User with this email already exists."}, status=400)

    teacher_code = Teacher.generate_teacher_code(full_name)
    first_name = full_name.split()[0]
    raw_password = f"{first_name}{teacher_code}"

    # Create User and hash password automatically
    user = User.objects.create_user(
        username=teacher_code.lower(),
        email=email,
        first_name=full_name.split()[0],
        last_name=" ".join(full_name.split()[1:]),
        password=raw_password,
    )

    # Create the Teacher linked to User
    teacher = Teacher.objects.create(
        user=user,
        phone=teacher_data.get("phone", ""),
        department=teacher_data.get("department", ""),
        designation=teacher_data.get("designation", ""),
        working_days=teacher_data.get("working_days", ""),
        teacher_code=teacher_code,
        teacher_type=teacher_data.get("teacher_type", "faculty"),
    )

    subject_names = teacher_data.get("preferred_subjects", [])
    # Convert subject names to subject codes
    subject_codes = []
    for subject_name in subject_names:
        subject = Subject.objects.filter(subject_name=subject_name).first()
        if subject:
            subject_codes.append(subject.subject_code)
        else:
            return Response(
                {"error": f"Subject '{subject_name}' not found."}, status=404
            )

    # Map preferred subjects using subject codes
    for subject_code in subject_codes:
        TeacherSubject.add_teacher_to_subject(subject_code, teacher_code)

    # Send email with credentials
    email_subject = "Your Teacher Account Credentials"
    email_body = render_to_string(
        "emails/teacher_confirmation_email.html",
        {
            "teacher_name": full_name,
            "teacher_code": teacher_code,
            "preferred_subjects": subject_names,
            "email": email,
            "password": raw_password,
        },
    )

    try:
        send_mail(
            email_subject,
            email_body,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
            html_message=email_body,
        )
    except Exception as e:
        return Response({"error": f"Failed to send email: {str(e)}"}, status=500)

    return Response(
        {"message": "Teacher added successfully, credentials sent via email."},
        status=201,
    )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateTeacher(request, pk):
    """
    Update an existing teacher's detail by ID, including preferred subjects.
    """
    try:
        teacher = Teacher.objects.get(id=pk)
        serializer = TeacherSerializer(
            instance=teacher, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()

            if "preferred_subjects" in request.data:
                new_preferred_subjects = request.data["preferred_subjects"]
                teacher_code = teacher.teacher_code

                # Remove teacher from all subjects they were previously assigned to
                old_subjects = TeacherSubject.get_teacher_subjects(teacher_code)
                for subject in old_subjects:
                    TeacherSubject.remove_teacher_from_subject(subject, teacher_code)

                # Add teacher to new preferred subjects
                for subject_code in new_preferred_subjects:
                    TeacherSubject.add_teacher_to_subject(subject_code, teacher_code)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)

    except Teacher.DoesNotExist:
        return Response({"error": "Teacher not found"}, status=404)


@api_view(["DELETE"])
@permission_classes([AllowAny])
def deleteTeacher(request, pk):
    """
    Delete a teacher by ID.
    """
    try:
        teacher = Teacher.objects.get(id=pk)
        teacher.delete()
        return Response({"message": "Teacher deleted successfully"}, status=200)
    except Teacher.DoesNotExist:
        return Response({"error": "Teacher not found"}, status=404)


@api_view(["GET"])
@permission_classes([AllowAny])
def getAllSubjects(request):
    """
    Retrieve a list of all subjects.
    """
    subjects = Subject.objects.all()
    serializer = SubjectSerializer(subjects, many=True)
    return Response(serializer.data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getFilteredSubjects(request):
    """
    Retrieve subjects based on department, course, branch, and semester.
    """
    dept = request.GET.get("dept")
    course = request.GET.get("course")
    branch = request.GET.get("branch", "")
    semester = request.GET.get("semester")

    if not all([dept, course, semester]):
        return Response(
            {"error": "Please provide dept, course, and semester."},
            status=400,
        )

    filters = {
        "dept": dept,
        "course": course,
        "semester": semester,
    }
    if branch:
        filters["branch"] = branch

    subjects = Subject.objects.filter(**filters)
    serializer = SubjectSerializer(subjects, many=True)
    return Response(serializer.data, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def addSubject(request):
    """
    Add one or multiple subjects to a specific dept, course, branch, and semester.
    """
    data = request.data if isinstance(request.data, list) else [request.data]
    added_subjects = []
    errors = []

    for subject_data in data:
        dept = subject_data.get("dept")
        course = subject_data.get("course")
        branch = subject_data.get("branch", "")
        semester = subject_data.get("semester")

        if not all([dept, course, semester]):
            errors.append(
                {
                    "subject_data": subject_data,
                    "error": "Please provide dept, course, and semester for each subject.",
                }
            )
            continue

        subject_name = subject_data.get("subject_name")
        subject_code = subject_data.get("subject_code")
        credits = subject_data.get("credits")
        weekly_quota_limit = subject_data.get("weekly_quota_limit")
        is_special_subject = subject_data.get("is_special_subject", "No")

        if not all([subject_name, subject_code, credits, weekly_quota_limit]):
            errors.append(
                {
                    "subject_data": subject_data,
                    "error": "Please provide subject_name, subject_code, credits, and weekly quota limit for each subject.",
                }
            )
            continue

        existing_subject = Subject.objects.filter(subject_code=subject_code).first()
        if existing_subject:
            errors.append(
                {
                    "subject_data": subject_data,
                    "error": f"Subject with code {subject_code} already exists.",
                }
            )
            continue

        subject_dict = {
            "subject_name": subject_name,
            "subject_code": subject_code,
            "credits": credits,
            "weekly_quota_limit": weekly_quota_limit,
            "is_special_subject": is_special_subject,
            "dept": dept,
            "course": course,
            "branch": branch,
            "semester": semester,
        }

        serializer = SubjectSerializer(data=subject_dict)
        if serializer.is_valid():
            serializer.save()
            added_subjects.append(serializer.data)
        else:
            errors.append({"subject_data": subject_data, "errors": serializer.errors})

    if errors:
        return Response(
            {"added_subjects": added_subjects, "errors": errors},
            status=400 if not added_subjects else 207,
        )

    return Response(
        {"message": "Subjects added successfully.", "subjects": added_subjects},
        status=201,
    )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateSubject(request, pk):
    """
    Update an existing subject by ID.
    """
    try:
        subject = Subject.objects.get(id=pk)
    except Subject.DoesNotExist:
        return Response({"error": "Subject not found"}, status=404)

    new_subject_code = request.data.get("subject_code")
    if (
        new_subject_code
        and Subject.objects.filter(subject_code=new_subject_code)
        .exclude(id=pk)
        .exists()
    ):
        return Response(
            {
                "error": f"Subject code '{new_subject_code}' is already assigned to another subject."
            },
            status=400,
        )

    serializer = SubjectSerializer(instance=subject, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=200)
    else:
        return Response(serializer.errors, status=400)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteSubject(request, pk):
    """
    Delete a subject by ID.
    """
    try:
        subject = Subject.objects.get(id=pk)
        subject.delete()
        return Response({"message": "Subject deleted successfully"}, status=200)
    except Subject.DoesNotExist:
        return Response({"error": "Subject not found"}, status=404)


def addStudent(
    student_name,
    student_id,
    is_hosteller,
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
                "is_hosteller": is_hosteller,
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
def addStudentAPI(request):
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

                result = addStudent(**student_data)

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


@csrf_exempt
def detectConflicts(request):
    if request.method == "POST" and request.FILES.getlist("csv_files"):
        try:
            csv_files = request.FILES.getlist("csv_files")
            timetables = []
            file_names = []

            for csv_file in csv_files:
                timetable_json = csv_to_json(csv_file)
                timetables.append(json.loads(timetable_json))
                file_names.append(csv_file.name)

            conflict_checker = IsConflict()
            conflict_results = []
            has_conflicts = False

            for i in range(len(timetables)):
                for j in range(i + 1, len(timetables)):
                    timetable1 = timetables[i]
                    timetable2 = timetables[j]

                    conflicts = conflict_checker.process_schedules(
                        timetable1, timetable2
                    )

                    if conflicts:
                        has_conflicts = True
                        conflict_results.append(
                            {
                                "timetable_1": file_names[i],
                                "timetable_2": file_names[j],
                                "conflict_details": conflicts,
                            }
                        )

            if has_conflicts:
                return JsonResponse({"conflicts": conflict_results}, status=200)
            else:
                return JsonResponse(
                    {"message": "No conflicts found between any two timetables."},
                    status=200,
                )

        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=400)

    return JsonResponse(
        {"error": "Invalid request. Please provide CSV files."}, status=400
    )
