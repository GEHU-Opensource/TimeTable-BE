from django.template.loader import render_to_string
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from mainapp.models import Subject, Teacher, TeacherSubject, SubjectPreference
from mainapp.serializers import TeacherSerializer
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from .emails import send_email_async

class TimetableSerializer(serializers.Serializer):
    course_id = serializers.CharField(max_length=100)
    semester = serializers.IntegerField()
    timetable = serializers.DictField()
    chromosome = serializers.CharField(max_length=255)
    last_updated = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_specific_teacher(request):
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
            "teacher_type": teacher.teacher_type,
            "phone": teacher.phone,
            "department": teacher.department,
            "designation": teacher.designation,
            "working_days": teacher.working_days,
            "assigned_subjects": subject_names,
        },
        status=200,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_teachers(request):
    """
    Retrieve a list of all teachers along with their preferred subjects.
    """
    teachers = Teacher.objects.all()
    serializer = TeacherSerializer(teachers, many=True)
    return Response(serializer.data, status=200)


@api_view(["POST"])
@permission_classes([AllowAny])
def add_teacher(request):
    """
    Add a new teacher, generate a unique teacher_code & password,
    store preferred subjects in SubjectPreference, and send credentials via email.
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

    user = User.objects.create_user(
        username=teacher_code.lower(),
        email=email,
        first_name=first_name,
        last_name=" ".join(full_name.split()[1:]),
    )

    initials = "".join([part[0] for part in full_name.split()])
    teacher_id = str(user.id)
    raw_password = f"{first_name}@{initials}-{teacher_id}"

    user.set_password(raw_password)
    user.save()

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
    for subject_name in subject_names:
        subject = Subject.objects.filter(subject_name=subject_name).first()
        if subject:
            SubjectPreference.add_preference(
                subject.department, subject.subject_code, teacher_code, full_name
            )
        else:
            return Response(
                {"error": f"Subject '{subject_name}' not found."}, status=404
            )

    # Prepare email context
    email_context = {
        "teacher_name": full_name,
        "preferred_subjects": subject_names,
        "teacher_code": teacher_code,
        "email": email,
        "password": raw_password,
    }

    # Send email asynchronously using threading
    send_email_async(
        subject="Your Teacher Account Credentials",
        template_name="teacher_confirmation_email.html",
        context=email_context,
        recipient_email=email,
    )

    return Response(
        {"message": "Teacher added successfully, credentials sent via email."},
        status=201,
    )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_teacher(request, pk):
    """
    Update an existing teacher's details by ID.
    """
    try:
        teacher = Teacher.objects.get(id=pk)
        serializer = TeacherSerializer(
            instance=teacher, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()

            subject_codes = TeacherSubject.get_teacher_subjects(teacher.teacher_code)

            subject_names = list(
                Subject.objects.filter(subject_code__in=subject_codes).values_list(
                    "subject_name", flat=True
                )
            )

            return Response(
                {
                    "id": teacher.id,
                    "name": teacher.user.get_full_name(),
                    "email": teacher.user.email,
                    "teacher_code": teacher.teacher_code,
                    "phone": teacher.phone,
                    "department": teacher.department,
                    "designation": teacher.designation,
                    "working_days": teacher.working_days,
                    "assigned_subjects": subject_names,
                },
                status=200,
            )
        else:
            return Response(serializer.errors, status=400)

    except Teacher.DoesNotExist:
        return Response({"error": "Teacher not found"}, status=404)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_teacher(request, pk):
    """
    Delete a teacher by ID.
    """
    try:
        teacher = Teacher.objects.get(id=pk)
        teacher.delete()
        return Response({"message": "Teacher deleted successfully"}, status=200)
    except Teacher.DoesNotExist:
        return Response({"error": "Teacher not found"}, status=404)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_password(request):
    """
    Allows a teacher to update their login password.
    """
    user = request.user
    data = request.data

    old_password = data.get("old_password", "").strip()
    new_password = data.get("new_password", "").strip()
    confirm_password = data.get("confirm_password", "").strip()

    if not old_password or not new_password or not confirm_password:
        return Response({"error": "All fields are required."}, status=400)

    if not check_password(old_password, user.password):
        return Response({"error": "Old password is incorrect."}, status=400)

    if new_password != confirm_password:
        return Response(
            {"error": "New password and confirm password do not match."}, status=400
        )

    if len(new_password) < 8:
        return Response(
            {"error": "New password must be at least 8 characters long."}, status=400
        )

    user.set_password(new_password)
    user.save()

    return Response({"message": "Password updated successfully."}, status=200)
