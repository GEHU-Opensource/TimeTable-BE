from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from mainapp.models import Subject
from mainapp.serializers import SubjectSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def get_all_subjects(request):
    """
    Retrieve a list of all subjects.
    """
    subjects = Subject.objects.all()
    serializer = SubjectSerializer(subjects, many=True)
    return Response(serializer.data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_filtered_subjects(request):
    """
    Retrieve subjects based on department, course, branch, and semester.
    """
    department = request.GET.get("department")
    course = request.GET.get("course")
    branch = request.GET.get("branch", "")
    semester = request.GET.get("semester")

    if not all([department, course, semester]):
        return Response(
            {"error": "Please provide department, course, and semester."},
            status=400,
        )

    filters = {
        "department": department,
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
def add_subject(request):
    """
    Add one or multiple subjects to a specific department, course, branch, and semester.
    """
    data = request.data if isinstance(request.data, list) else [request.data]
    added_subjects = []
    errors = []

    for subject_data in data:
        department = subject_data.get("department")
        course = subject_data.get("course")
        branch = subject_data.get("branch", "")
        semester = subject_data.get("semester")

        if not all([department, course, semester]):
            errors.append(
                {
                    "subject_data": subject_data,
                    "error": "Please provide department, course, and semester for each subject.",
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
            "department": department,
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
def update_subject(request, pk):
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
def delete_subject(request, pk):
    """
    Delete a subject by ID.
    """
    try:
        subject = Subject.objects.get(id=pk)
        subject.delete()
        return Response({"message": "Subject deleted successfully"}, status=200)
    except Subject.DoesNotExist:
        return Response({"error": "Subject not found"}, status=404)
