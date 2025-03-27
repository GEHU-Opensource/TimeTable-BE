from django.contrib import admin
from .models import Room, Teacher, Subject, TeacherSubject, Student, SubjectPreference

admin.site.register(Room)
admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(TeacherSubject)
admin.site.register(Student)
admin.site.register(SubjectPreference)
