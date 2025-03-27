from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from mainapp.models import Teacher, Subject, TeacherSubject, SubjectPreference
from mainapp.serializers import (
    TeacherSerializer,
    SubjectSerializer,
    SubjectPreferenceSerializer,
)
from .emails import send_email_async

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_requests(request):
    """
    API to fetch pending subject-teacher requests for a department.
    """

    try:
        hod = Teacher.objects.get(user=request.user, teacher_type="hod")
        department = hod.department
    except Teacher.DoesNotExist:
        return Response({"error": "HOD access required"}, status=403)

    # Fetch all subjects in the department
    subjects = Subject.objects.filter(department=department).values(
        "subject_name", "subject_code"
    )

    # Fetch requested subject-teacher mappings
    pending_requests = SubjectPreference.get_subject_preferences(department)

    # Fetch all teachers in the department
    teachers = Teacher.objects.filter(department=department).values(
        "user__first_name", "user__last_name", "teacher_code"
    )

    # Format teachers data properly
    teacher_list = [
        {
            "teacher_name": f"{t['user__first_name']} {t['user__last_name']}",
            "teacher_code": t["teacher_code"],
        }
        for t in teachers
    ]

    return Response(
        {
            "subjects": list(subjects),
            "pending_requests": pending_requests,
            "teachers": teacher_list,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_subject_requests(request):
    """
    Approves the selected subject requests by the HOD and updates TeacherSubject mapping. Sends an email notification to teachers about approved and rejected subjects asynchronously.
    """
    try:
        approved_requests = request.data
        # Dictionary with subject_code -> list of teacher codes
        teacher_mapping = TeacherSubject.objects.get_or_create(id=1)[0]

        hod = Teacher.objects.get(user=request.user)
        hod_name = hod.user.get_full_name()
        department_name = hod.department

        subject_pref = SubjectPreference.objects.get_or_create(id=1)[0]
        department_preferences = subject_pref.preferences.get(department_name, {})

        approved_teachers = set()
        rejected_teachers = {}

        approved_subjects_per_teacher = {}

        # Approve subjects and track approved teachers
        for subject_code, teacher_codes in approved_requests.items():
            for teacher_code in teacher_codes:
                teacher = Teacher.objects.filter(teacher_code=teacher_code).first()
                if teacher:
                    teacher_mapping.add_teacher_to_subject(
                        subject_code, teacher.teacher_code
                    )
                    approved_teachers.add((teacher_code, subject_code))
                    approved_subjects_per_teacher.setdefault(teacher_code, []).append(
                        subject_code
                    )

        # Identify rejected subjects per teacher
        for subject_code, teacher_list in department_preferences.items():
            for teacher_entry in teacher_list:
                for teacher_code in teacher_entry.keys():
                    if (teacher_code, subject_code) not in approved_teachers:
                        rejected_teachers.setdefault(teacher_code, []).append(
                            subject_code
                        )

        # Remove all subject preferences for the department
        if department_name in subject_pref.preferences:
            del subject_pref.preferences[department_name]
            subject_pref.save()

        # Send emails asynchronously
        for teacher_code in set(
            list(approved_subjects_per_teacher.keys()) + list(rejected_teachers.keys())
        ):
            teacher = Teacher.objects.filter(teacher_code=teacher_code).first()
            if teacher and teacher.user.email:

                approved_subjects = [
                    Subject.objects.get(subject_code=sub).subject_name
                    for sub in approved_subjects_per_teacher.get(teacher_code, [])
                ]

                rejected_subjects = [
                    Subject.objects.get(subject_code=sub).subject_name
                    for sub in rejected_teachers.get(teacher_code, [])
                ]

                email_context = {
                    "teacher_name": teacher.user.get_full_name(),
                    "approved_subjects": approved_subjects,
                    "rejected_subjects": rejected_subjects,
                    "hod_name": hod_name,
                    "department_name": department_name,
                }

                send_email_async(
                    subject="Subject Preference Approval Status",
                    template_name="subject_approval_email.html",
                    context=email_context,
                    recipient_email=teacher.user.email,
                )

        return Response(
            {"message": "Subjects approved and emails sent successfully!"}, status=200
        )

    except Teacher.DoesNotExist:
        return Response({"error": "HOD not found or unauthorized"}, status=403)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


def get_teacher_name(teacher_code):
    """Helper function to get teacher's full name from teacher_code."""
    teacher = Teacher.objects.filter(teacher_code=teacher_code).first()
    return (
        f"{teacher.user.first_name} {teacher.user.last_name}" if teacher else "Unknown"
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_approved_subjects(request):
    """
    Fetches the approved subjects of the HOD's department along with the assigned teacher names.
    """
    try:
        hod = Teacher.objects.filter(user=request.user, teacher_type="hod").first()
        if not hod:
            return Response({"error": "Only HODs can access this data"}, status=403)

        teacher_subject_mapping = TeacherSubject.objects.get_or_create(id=1)[0]
        approved_subjects = []

        for (
            subject_code,
            teacher_codes,
        ) in teacher_subject_mapping.subject_teacher_map.items():
            # Fetch the subject and check if it belongs to the HOD's department
            subject = Subject.objects.filter(
                subject_code=subject_code, department=hod.department
            ).first()
            if subject:
                approved_subjects.append(
                    {
                        "subject_code": subject_code,
                        "subject_name": subject.subject_name,
                        "teachers": [
                            {code: get_teacher_name(code)} for code in teacher_codes
                        ],
                    }
                )

        return Response(approved_subjects, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
