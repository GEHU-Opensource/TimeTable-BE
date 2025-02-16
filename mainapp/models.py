from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class Teacher(models.Model):
    TEACHER_TYPES = [
        ("admin", "Admin"),
        ("hod", "HOD"),
        ("faculty", "Faculty"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Linked to User
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    working_days = models.CharField(max_length=100)
    teacher_code = models.CharField(max_length=10, unique=True, null=False)
    teacher_type = models.CharField(
        max_length=10, choices=TEACHER_TYPES, default="faculty"
    )

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.teacher_code}) - {self.department}"

    @staticmethod
    def generate_teacher_code(name):
        """Generate a unique teacher_code"""
        initials = "".join([part[0].upper() for part in name.split() if part])
        existing_codes = Teacher.objects.filter(
            teacher_code__startswith=f"{initials}-"
        ).values_list("teacher_code", flat=True)
        existing_numbers = sorted(
            [
                int(code.split("-")[1])
                for code in existing_codes
                if "-" in code and code.split("-")[1].isdigit()
            ]
        )

        next_number = (existing_numbers[-1] + 1) if existing_numbers else 1
        return f"{initials}-{next_number:02}"


class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=10)
    semester = models.IntegerField()
    credits = models.IntegerField()
    weekly_quota_limit = models.IntegerField(default=1)
    is_special_subject = models.CharField(max_length=10, default="No")
    department = models.CharField(max_length=50)
    course = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, default="")

    def __str__(self):
        return f"{self.subject_name} ({self.subject_code}) - {self.department} {self.semester} sem"


class SubjectPreference(models.Model):
    """
    Stores subject preference requests from teachers, waiting for HOD approval.
    """

    preferences = models.JSONField(default=dict)

    def __str__(self):
        return "Subject Preferences Mapping"

    @classmethod
    def add_preference(cls, department, subject_code, teacher_name):
        """
        Adds a teacher's subject preference request.
        """
        mapping, created = cls.objects.get_or_create(
            id=1
        )  # Ensuring a single-row model

        if department not in mapping.preferences:
            mapping.preferences[department] = {}

        if subject_code not in mapping.preferences[department]:
            mapping.preferences[department][subject_code] = []

        if teacher_name not in mapping.preferences[department][subject_code]:
            mapping.preferences[department][subject_code].append(teacher_name)

        mapping.save()

    @classmethod
    def remove_preference(cls, department, subject_code, teacher_name):
        """
        Removes a teacher's subject preference request.
        """
        try:
            mapping = cls.objects.get(id=1)
            if (
                department in mapping.preferences
                and subject_code in mapping.preferences[department]
                and teacher_name in mapping.preferences[department][subject_code]
            ):
                mapping.preferences[department][subject_code].remove(teacher_name)

                # Remove subject if empty
                if not mapping.preferences[department][subject_code]:
                    del mapping.preferences[department][subject_code]

                # Remove department if empty
                if not mapping.preferences[department]:
                    del mapping.preferences[department]

                mapping.save()
        except cls.DoesNotExist:
            pass

    @classmethod
    def get_subject_preferences(cls, department):
        """
        Retrieves all subject preferences for a department.
        """
        try:
            mapping = cls.objects.get(id=1)
            return mapping.preferences.get(department, {})
        except cls.DoesNotExist:
            return {}

    @classmethod
    def get_teacher_preferences(cls, teacher_name):
        """
        Retrieves all subject preferences of a specific teacher.
        """
        try:
            mapping = cls.objects.get(id=1)
            teacher_prefs = {}

            for department, subjects in mapping.preferences.items():
                for subject_code, teachers in subjects.items():
                    if teacher_name in teachers:
                        if department not in teacher_prefs:
                            teacher_prefs[department] = {}
                        teacher_prefs[department][subject_code] = teachers

            return teacher_prefs
        except cls.DoesNotExist:
            return {}


@receiver(post_delete, sender=Teacher)
def remove_teacher_from_preferences(sender, instance, **kwargs):
    """
    Removes the teacher from the SubjectPreference mapping when they are deleted.
    """
    teacher_name = instance.user.get_full_name()

    try:
        mapping = SubjectPreference.objects.get(id=1)
        updated = False

        for department in list(mapping.preferences.keys()):
            for subject_code in list(mapping.preferences[department].keys()):
                if teacher_name in mapping.preferences[department][subject_code]:
                    mapping.preferences[department][subject_code].remove(teacher_name)
                    updated = True

                    # Remove the subject if no more teachers have requested it
                    if not mapping.preferences[department][subject_code]:
                        del mapping.preferences[department][subject_code]

            # Remove the department if it has no more subjects
            if not mapping.preferences[department]:
                del mapping.preferences[department]

        if updated:
            mapping.save()

    except SubjectPreference.DoesNotExist:
        pass  # No mapping exists yet


class TeacherSubject(models.Model):
    subject_teacher_map = models.JSONField(default=dict)

    def __str__(self):
        return "Teacher-Subject Mapping"

    @classmethod
    def add_teacher_to_subject(cls, subject_code, teacher_code):
        """
        Adds a teacher to a subject in the mapping.
        """
        mapping, created = cls.objects.get_or_create(
            id=1
        )  # Ensuring a single-row model
        if subject_code in mapping.subject_teacher_map:
            if teacher_code not in mapping.subject_teacher_map[subject_code]:
                mapping.subject_teacher_map[subject_code].append(teacher_code)
        else:
            mapping.subject_teacher_map[subject_code] = [teacher_code]
        mapping.save()

    @classmethod
    def remove_teacher_from_subject(cls, subject_code, teacher_code):
        """
        Removes a teacher from a subject in the mapping.
        """
        try:
            mapping = cls.objects.get(id=1)
            if (
                subject_code in mapping.subject_teacher_map
                and teacher_code in mapping.subject_teacher_map[subject_code]
            ):
                mapping.subject_teacher_map[subject_code].remove(teacher_code)
                if not mapping.subject_teacher_map[subject_code]:  # Remove key if empty
                    del mapping.subject_teacher_map[subject_code]
                mapping.save()
        except cls.DoesNotExist:
            pass  # No mapping exists yet

    @classmethod
    def get_teacher_subjects(cls, teacher_code):
        """
        Retrieves all subjects a teacher is mapped to.
        """
        try:
            mapping = cls.objects.get(id=1)
            return [
                subj
                for subj, teachers in mapping.subject_teacher_map.items()
                if teacher_code in teachers
            ]
        except cls.DoesNotExist:
            return []

    @classmethod
    def get_subject_teachers(cls, subject_code):
        """
        Retrieves all teachers assigned to a specific subject.
        """
        try:
            mapping = cls.objects.get(id=1)
            return mapping.subject_teacher_map.get(subject_code, [])
        except cls.DoesNotExist:
            return []


@receiver(post_delete, sender=Teacher)
def delete_user_with_teacher(sender, instance, **kwargs):
    if instance.user:
        try:
            instance.user.delete()
        except Exception as e:
            print(f"Error deleting user: {e}")


@receiver(post_delete, sender=Teacher)
def remove_teacher_from_mapping(sender, instance, **kwargs):
    teacher_code = instance.teacher_code
    mapping = TeacherSubject.objects.filter(id=1).first()
    if mapping:
        updated = False
        for subject_code in list(mapping.subject_teacher_map.keys()):
            if teacher_code in mapping.subject_teacher_map[subject_code]:
                mapping.subject_teacher_map[subject_code].remove(teacher_code)
                updated = True
                if not mapping.subject_teacher_map[subject_code]:
                    del mapping.subject_teacher_map[subject_code]
        if updated:
            mapping.save()


@receiver(pre_delete, sender=User)
def delete_auth_token(sender, instance, **kwargs):
    """
    Deletes the authentication token when a user is deleted.
    """
    Token.objects.filter(user=instance).delete()


class Room(models.Model):
    room_code = models.CharField(max_length=10)
    capacity = models.IntegerField()
    room_type = models.CharField(
        max_length=20,
        choices=(
            ("Class Room", "Class Room"),
            ("Lecture Theatre", "Lecture Theatre"),
            ("Lab", "Lab"),
            ("Seminar Hall", "Seminar Hall"),
        ),
        default="Class Room",
    )

    def __str__(self):
        return f"{self.room_code} ({self.room_type})"


class Student(models.Model):
    student_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=15)
    is_hosteller = models.BooleanField(default=False)
    location = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    course = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, default="")
    semester = models.IntegerField()
    section = models.CharField(max_length=2)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"{self.student_name} ({self.student_id}) - Section {self.section}"
