from rest_framework import serializers
from .models import Room, Teacher, Subject, TeacherSubject, SubjectPreference


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class TeacherSerializer(serializers.ModelSerializer):
    preferred_subjects = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = "__all__"
        read_only_fields = ["password"]  # Only password should be read-only

    def get_preferred_subjects(self, obj):
        """
        Retrieve subjects assigned to this teacher from the JSONField.
        """
        return TeacherSubject.get_teacher_subjects(obj.teacher_code)

    def create(self, validated_data):
        """
        Ensure teacher_code is properly saved during creation.
        """
        if "teacher_code" not in validated_data:
            validated_data["teacher_code"] = Teacher.generate_teacher_code(
                validated_data["name"]
            )
        return super().create(validated_data)


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class SubjectPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectPreference
        fields = "__all__"


class ExcelFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        """
        Validate that the uploaded file is an Excel file.
        """
        if not value.name.endswith((".xls", ".xlsx")):
            raise serializers.ValidationError(
                "Invalid file format. Please upload an Excel file."
            )
        return value
