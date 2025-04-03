# from django.http import JsonResponse
# from rest_framework.response import Response
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated, AllowAny
#
# from .drivers.mongo import MongoDriver
# from .models import Room, Teacher, Subject, TeacherSubject, Student, SubjectPreference
# from .serializers import (
#     RoomSerializer,
#     TeacherSerializer,
#     SubjectSerializer,
#     SubjectPreferenceSerializer,
#     ExcelFileUploadSerializer,
# )
# import os
# from GA.__init__ import run_timetable_generation
# from Constants.section_allocation import StudentScorer
# import pandas as pd
# import json
# from django.views.decorators.csrf import csrf_exempt
# from .drivers.converter import csv_to_json
# from Constants.is_conflict import IsConflict
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
# from rest_framework_simplejwt.tokens import RefreshToken
# <<<<<<< HEAD
# from django.http import HttpResponse
# from gridfs import GridFS
# import string
# import io
# import zipfile
# from bson import ObjectId
# =======
# from django.contrib.auth.hashers import check_password
# import asyncio
# from django.conf import settings
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.core.mail import EmailMultiAlternatives
# from django.utils.html import strip_tags
# import threading
#
#
# def send_email_async(subject, template_name, context, recipient_email):
#     """
#     Sends an email asynchronously using a separate thread.
#     """
#
#     def send():
#         html_content = render_to_string(template_name, context)  # Render HTML template
#         text_content = strip_tags(html_content)  # Remove HTML tags for plain-text email
#
#         email = EmailMultiAlternatives(
#             subject,
#             text_content,
#             None,  # Uses default email sender from settings
#             [recipient_email],
#         )
#         email.attach_alternative(html_content, "text/html")
#         email.send()
#
#     thread = threading.Thread(target=send)
#     thread.start()
# >>>>>>> 6c3edb1851c0c1df6a778f73564eaf0a35ac8e5c
#
#
# @api_view(["POST"])
# @permission_classes([AllowAny])
# def login(request):
#     """
#     Authenticate a teacher using email and return JWT tokens.
#     """
#     email = request.data.get("email", "").strip().lower()
#     password = request.data.get("password", "").strip()
#
#     if not email or not password:
#         return Response({"error": "Email and password are required."}, status=400)
#
#     user = User.objects.filter(email=email).first()
#
#     if not user:
#         return Response({"error": "Invalid email or password."}, status=401)
#
#     user = authenticate(username=user.username, password=password)
#
#     if not user:
#         return Response({"error": "Invalid email or password."}, status=401)
#
#     teacher = Teacher.objects.filter(user=user).first()
#     if not teacher:
#         return Response({"error": "Teacher account not found."}, status=404)
#
#     # Generate JWT tokens
#     refresh = RefreshToken.for_user(user)
#
#     return Response(
#         {
#             "message": "Login successful",
#             "access_token": str(refresh.access_token),
#             "refresh_token": str(refresh),
#             "teacher": {
#                 "teacher_type": teacher.teacher_type,
#             },
#         },
#         status=200,
#     )
#
#
# def generateTimetable():
#     output = run_timetable_generation()
#     # chromosome_output, teacher_availability, classroom_availability = output
#     # mongo_driver = MongoDriver()
#     # mongo_driver.delete_many("teacher_availability", {})
#     # mongo_driver.delete_many("classroom_availability", {})
#     # mongo_driver.insert_one("teacher_availability", teacher_availability)
#     # mongo_driver.insert_one("classroom_availability", classroom_availability)
#     return chromosome_output
#
#
#
# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def generate_timetable(request):
#     """
#     Generate a timetable using the provided data.
#     """
#     try:
#         timetable = generateTimetable()
#         return Response(timetable, status=200)
#     except Exception as e:
#         return Response(
#             {"error": f"Failed to generate timetable: {str(e)}"}, status=500
#         )
#
#
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def getRooms(request):
#     """
#     Retrieve a list of all rooms.
#     """
#     rooms = Room.objects.all()
#     serializer = RoomSerializer(rooms, many=True)
#     return Response(serializer.data, status=200)
#
#
# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def addRoom(request):
#     """
#     Add one or multiple rooms.
#     """
#     data = request.data if isinstance(request.data, list) else [request.data]
#     added_rooms = []
#     errors = []
#
#     for room_data in data:
#         existing_room = Room.objects.filter(
#             room_code=room_data.get("room_code")
#         ).first()
#         if existing_room:
#             errors.append(
#                 {
#                     "room_data": room_data,
#                     "error": f"Room with code {room_data.get('room_code')} already exists",
#                 }
#             )
#             continue
#
#         serializer = RoomSerializer(data=room_data)
#         if serializer.is_valid():
#             serializer.save()
#             added_rooms.append(serializer.data)
#         else:
#             errors.append({"room_data": room_data, "errors": serializer.errors})
#
#     if errors:
#         return Response(
#             {"added_rooms": added_rooms, "errors": errors},
#             status=400 if not added_rooms else 207,
#         )
#     return Response(added_rooms, status=201)
#
#
# @api_view(["PUT"])
# @permission_classes([IsAuthenticated])
# def updateRoom(request, pk):
#     """
#     Update an existing room by ID.
#     """
#     try:
#         room = Room.objects.get(id=pk)
#
#         new_room_code = request.data.get("room_code")
#         if (
#             new_room_code
#             and Room.objects.filter(room_code=new_room_code).exclude(id=pk).exists()
#         ):
#             return Response(
#                 {
#                     "error": f"Room code '{new_room_code}' is already assigned to another room."
#                 },
#                 status=400,
#             )
#
#         serializer = RoomSerializer(instance=room, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=200)
#         else:
#             return Response(serializer.errors, status=400)
#     except Room.DoesNotExist:
#         return Response({"error": "Room not found"}, status=404)
#
#
# @api_view(["DELETE"])
# @permission_classes([IsAuthenticated])
# def deleteRoom(request, pk):
#     """
#     Delete a room by ID.
#     """
#     try:
#         room = Room.objects.get(id=pk)
#         room.delete()
#         return Response({"message": "Room deleted successfully"}, status=200)
#     except Room.DoesNotExist:
#         return Response({"error": "Room not found"}, status=404)
#
#
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def getTeachers(request):
#     """
#     Retrieve a list of all teachers along with their preferred subjects.
#     """
#     teachers = Teacher.objects.all()
#     serializer = TeacherSerializer(teachers, many=True)
#     return Response(serializer.data, status=200)
#
#
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def getSpecificTeacher(request):
#     """
#     Retrieve the details of the authenticated teacher.
#     """
#     user = request.user
#     teacher = Teacher.objects.filter(user=user).first()
#
#     if not teacher:
#         return Response({"error": "Teacher account not found."}, status=404)
#
#     subject_codes = TeacherSubject.get_teacher_subjects(teacher.teacher_code)
#
#     subject_names = list(
#         Subject.objects.filter(subject_code__in=subject_codes).values_list(
#             "subject_name", flat=True
#         )
#     )
#
#     return Response(
#         {
#             "id": teacher.id,
#             "name": user.get_full_name(),
#             "email": user.email,
#             "teacher_code": teacher.teacher_code,
#             "teacher_type": teacher.teacher_type,
#             "phone": teacher.phone,
#             "department": teacher.department,
#             "designation": teacher.designation,
#             "working_days": teacher.working_days,
#             "assigned_subjects": subject_names,
#         },
#         status=200,
#     )
#
#
# @api_view(["POST"])
# @permission_classes([AllowAny])
# def addTeacher(request):
#     """
#     Add a new teacher, generate a unique teacher_code & password,
#     store preferred subjects in SubjectPreference, and send credentials via email.
#     """
#     teacher_data = request.data
#
#     email = teacher_data.get("email", "").strip().lower()
#     full_name = teacher_data.get("name", "").strip()
#
#     if not email or not full_name:
#         return Response({"error": "Email and Name are required."}, status=400)
#
#     existing_user = User.objects.filter(email=email).first()
#     if existing_user:
#         return Response({"error": "User with this email already exists."}, status=400)
#
#     teacher_code = Teacher.generate_teacher_code(full_name)
#     first_name = full_name.split()[0]
#
#     user = User.objects.create_user(
#         username=teacher_code.lower(),
#         email=email,
#         first_name=first_name,
#         last_name=" ".join(full_name.split()[1:]),
#     )
#
#     initials = "".join([part[0] for part in full_name.split()])
#     teacher_id = str(user.id)
#     raw_password = f"{first_name}@{initials}-{teacher_id}"
#
#     user.set_password(raw_password)
#     user.save()
#
#     teacher = Teacher.objects.create(
#         user=user,
#         phone=teacher_data.get("phone", ""),
#         department=teacher_data.get("department", ""),
#         designation=teacher_data.get("designation", ""),
#         working_days=teacher_data.get("working_days", ""),
#         teacher_code=teacher_code,
#         teacher_type=teacher_data.get("teacher_type", "faculty"),
#     )
#
#     subject_names = teacher_data.get("preferred_subjects", [])
#     for subject_name in subject_names:
#         subject = Subject.objects.filter(subject_name=subject_name).first()
#         if subject:
#             SubjectPreference.add_preference(
#                 subject.department, subject.subject_code, teacher_code, full_name
#             )
#         else:
#             return Response(
#                 {"error": f"Subject '{subject_name}' not found."}, status=404
#             )
#
#     # Prepare email context
#     email_context = {
#         "teacher_name": full_name,
#         "preferred_subjects": subject_names,
#         "teacher_code": teacher_code,
#         "email": email,
#         "password": raw_password,
#     }
#
#     # Send email asynchronously using threading
#     send_email_async(
#         subject="Your Teacher Account Credentials",
#         template_name="teacher_confirmation_email.html",
#         context=email_context,
#         recipient_email=email,
#     )
#
#     return Response(
#         {"message": "Teacher added successfully, credentials sent via email."},
#         status=201,
#     )
#
#
# @api_view(["PUT"])
# @permission_classes([IsAuthenticated])
# def updateTeacher(request, pk):
#     """
#     Update an existing teacher's details by ID.
#     """
#     try:
#         teacher = Teacher.objects.get(id=pk)
#         serializer = TeacherSerializer(
#             instance=teacher, data=request.data, partial=True
#         )
#
#         if serializer.is_valid():
#             serializer.save()
#
#             subject_codes = TeacherSubject.get_teacher_subjects(teacher.teacher_code)
#
#             subject_names = list(
#                 Subject.objects.filter(subject_code__in=subject_codes).values_list(
#                     "subject_name", flat=True
#                 )
#             )
#
#             return Response(
#                 {
#                     "id": teacher.id,
#                     "name": teacher.user.get_full_name(),
#                     "email": teacher.user.email,
#                     "teacher_code": teacher.teacher_code,
#                     "phone": teacher.phone,
#                     "department": teacher.department,
#                     "designation": teacher.designation,
#                     "working_days": teacher.working_days,
#                     "assigned_subjects": subject_names,
#                 },
#                 status=200,
#             )
#         else:
#             return Response(serializer.errors, status=400)
#
#     except Teacher.DoesNotExist:
#         return Response({"error": "Teacher not found"}, status=404)
#
#
# @api_view(["DELETE"])
# @permission_classes([AllowAny])
# def deleteTeacher(request, pk):
#     """
#     Delete a teacher by ID.
#     """
#     try:
#         teacher = Teacher.objects.get(id=pk)
#         teacher.delete()
#         return Response({"message": "Teacher deleted successfully"}, status=200)
#     except Teacher.DoesNotExist:
#         return Response({"error": "Teacher not found"}, status=404)
#
#
# @api_view(["PUT"])
# @permission_classes([IsAuthenticated])
# def updatePassword(request):
#     """
#     Allows a teacher to update their login password.
#     """
#     user = request.user
#     data = request.data
#
#     old_password = data.get("old_password", "").strip()
#     new_password = data.get("new_password", "").strip()
#     confirm_password = data.get("confirm_password", "").strip()
#
#     if not old_password or not new_password or not confirm_password:
#         return Response({"error": "All fields are required."}, status=400)
#
#     if not check_password(old_password, user.password):
#         return Response({"error": "Old password is incorrect."}, status=400)
#
#     if new_password != confirm_password:
#         return Response(
#             {"error": "New password and confirm password do not match."}, status=400
#         )
#
#     if len(new_password) < 8:
#         return Response(
#             {"error": "New password must be at least 8 characters long."}, status=400
#         )
#
#     user.set_password(new_password)
#     user.save()
#
#     return Response({"message": "Password updated successfully."}, status=200)
#
#
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def getPendingRequests(request):
#     """
#     API to fetch pending subject-teacher requests for a department.
#     """
#
#     try:
#         hod = Teacher.objects.get(user=request.user, teacher_type="hod")
#         department = hod.department
#     except Teacher.DoesNotExist:
#         return Response({"error": "HOD access required"}, status=403)
#
#     # Fetch all subjects in the department
#     subjects = Subject.objects.filter(department=department).values(
#         "subject_name", "subject_code"
#     )
#
#     # Fetch requested subject-teacher mappings
#     pending_requests = SubjectPreference.get_subject_preferences(department)
#
#     # Fetch all teachers in the department
#     teachers = Teacher.objects.filter(department=department).values(
#         "user__first_name", "user__last_name", "teacher_code"
#     )
#
#     # Format teachers data properly
#     teacher_list = [
#         {
#             "teacher_name": f"{t['user__first_name']} {t['user__last_name']}",
#             "teacher_code": t["teacher_code"],
#         }
#         for t in teachers
#     ]
#
#     return Response(
#         {
#             "subjects": list(subjects),
#             "pending_requests": pending_requests,
#             "teachers": teacher_list,
#         }
#     )
#
#
# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def approveSubjectRequests(request):
#     """
#     Approves the selected subject requests by the HOD and updates TeacherSubject mapping. Sends an email notification to teachers about approved and rejected subjects asynchronously.
#     """
#     try:
#         approved_requests = request.data
#         # Dictionary with subject_code -> list of teacher codes
#         teacher_mapping = TeacherSubject.objects.get_or_create(id=1)[0]
#
#         hod = Teacher.objects.get(user=request.user)
#         hod_name = hod.user.get_full_name()
#         department_name = hod.department
#
#         subject_pref = SubjectPreference.objects.get_or_create(id=1)[0]
#         department_preferences = subject_pref.preferences.get(department_name, {})
#
#         approved_teachers = set()
#         rejected_teachers = {}
#
#         approved_subjects_per_teacher = {}
#
#         # Approve subjects and track approved teachers
#         for subject_code, teacher_codes in approved_requests.items():
#             for teacher_code in teacher_codes:
#                 teacher = Teacher.objects.filter(teacher_code=teacher_code).first()
#                 if teacher:
#                     teacher_mapping.add_teacher_to_subject(
#                         subject_code, teacher.teacher_code
#                     )
#                     approved_teachers.add((teacher_code, subject_code))
#                     approved_subjects_per_teacher.setdefault(teacher_code, []).append(
#                         subject_code
#                     )
#
#         # Identify rejected subjects per teacher
#         for subject_code, teacher_list in department_preferences.items():
#             for teacher_entry in teacher_list:
#                 for teacher_code in teacher_entry.keys():
#                     if (teacher_code, subject_code) not in approved_teachers:
#                         rejected_teachers.setdefault(teacher_code, []).append(
#                             subject_code
#                         )
#
#         # Remove all subject preferences for the department
#         if department_name in subject_pref.preferences:
#             del subject_pref.preferences[department_name]
#             subject_pref.save()
#
#         # Send emails asynchronously
#         for teacher_code in set(
#             list(approved_subjects_per_teacher.keys()) + list(rejected_teachers.keys())
#         ):
#             teacher = Teacher.objects.filter(teacher_code=teacher_code).first()
#             if teacher and teacher.user.email:
#
#                 approved_subjects = [
#                     Subject.objects.get(subject_code=sub).subject_name
#                     for sub in approved_subjects_per_teacher.get(teacher_code, [])
#                 ]
#
#                 rejected_subjects = [
#                     Subject.objects.get(subject_code=sub).subject_name
#                     for sub in rejected_teachers.get(teacher_code, [])
#                 ]
#
#                 email_context = {
#                     "teacher_name": teacher.user.get_full_name(),
#                     "approved_subjects": approved_subjects,
#                     "rejected_subjects": rejected_subjects,
#                     "hod_name": hod_name,
#                     "department_name": department_name,
#                 }
#
#                 send_email_async(
#                     subject="Subject Preference Approval Status",
#                     template_name="subject_approval_email.html",
#                     context=email_context,
#                     recipient_email=teacher.user.email,
#                 )
#
#         return Response(
#             {"message": "Subjects approved and emails sent successfully!"}, status=200
#         )
#
#     except Teacher.DoesNotExist:
#         return Response({"error": "HOD not found or unauthorized"}, status=403)
#     except Exception as e:
#         return Response({"error": str(e)}, status=400)
#
#
# def get_teacher_name(teacher_code):
#     """Helper function to get teacher's full name from teacher_code."""
#     teacher = Teacher.objects.filter(teacher_code=teacher_code).first()
#     return (
#         f"{teacher.user.first_name} {teacher.user.last_name}" if teacher else "Unknown"
#     )
#
#
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def getApprovedSubjects(request):
#     """
#     Fetches the approved subjects of the HOD's department along with the assigned teacher names.
#     """
#     try:
#         hod = Teacher.objects.filter(user=request.user, teacher_type="hod").first()
#         if not hod:
#             return Response({"error": "Only HODs can access this data"}, status=403)
#
#         teacher_subject_mapping = TeacherSubject.objects.get_or_create(id=1)[0]
#         approved_subjects = []
#
#         for (
#             subject_code,
#             teacher_codes,
#         ) in teacher_subject_mapping.subject_teacher_map.items():
#             # Fetch the subject and check if it belongs to the HOD's department
#             subject = Subject.objects.filter(
#                 subject_code=subject_code, department=hod.department
#             ).first()
#             if subject:
#                 approved_subjects.append(
#                     {
#                         "subject_code": subject_code,
#                         "subject_name": subject.subject_name,
#                         "teachers": [
#                             {code: get_teacher_name(code)} for code in teacher_codes
#                         ],
#                     }
#                 )
#
#         return Response(approved_subjects, status=200)
#     except Exception as e:
#         return Response({"error": str(e)}, status=400)
#
#
# @api_view(["GET"])
# @permission_classes([AllowAny])
# def getAllSubjects(request):
#     """
#     Retrieve a list of all subjects.
#     """
#     subjects = Subject.objects.all()
#     serializer = SubjectSerializer(subjects, many=True)
#     return Response(serializer.data, status=200)
#
#
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def getFilteredSubjects(request):
#     """
#     Retrieve subjects based on department, course, branch, and semester.
#     """
#     department = request.GET.get("department")
#     course = request.GET.get("course")
#     branch = request.GET.get("branch", "")
#     semester = request.GET.get("semester")
#
#     if not all([department, course, semester]):
#         return Response(
#             {"error": "Please provide department, course, and semester."},
#             status=400,
#         )
#
#     filters = {
#         "department": department,
#         "course": course,
#         "semester": semester,
#     }
#     if branch:
#         filters["branch"] = branch
#
#     subjects = Subject.objects.filter(**filters)
#     serializer = SubjectSerializer(subjects, many=True)
#     return Response(serializer.data, status=200)
#
#
# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def addSubject(request):
#     """
#     Add one or multiple subjects to a specific department, course, branch, and semester.
#     """
#     data = request.data if isinstance(request.data, list) else [request.data]
#     added_subjects = []
#     errors = []
#
#     for subject_data in data:
#         department = subject_data.get("department")
#         course = subject_data.get("course")
#         branch = subject_data.get("branch", "")
#         semester = subject_data.get("semester")
#
#         if not all([department, course, semester]):
#             errors.append(
#                 {
#                     "subject_data": subject_data,
#                     "error": "Please provide department, course, and semester for each subject.",
#                 }
#             )
#             continue
#
#         subject_name = subject_data.get("subject_name")
#         subject_code = subject_data.get("subject_code")
#         credits = subject_data.get("credits")
#         weekly_quota_limit = subject_data.get("weekly_quota_limit")
#         is_special_subject = subject_data.get("is_special_subject", "No")
#
#         if not all([subject_name, subject_code, credits, weekly_quota_limit]):
#             errors.append(
#                 {
#                     "subject_data": subject_data,
#                     "error": "Please provide subject_name, subject_code, credits, and weekly quota limit for each subject.",
#                 }
#             )
#             continue
#
#         existing_subject = Subject.objects.filter(subject_code=subject_code).first()
#         if existing_subject:
#             errors.append(
#                 {
#                     "subject_data": subject_data,
#                     "error": f"Subject with code {subject_code} already exists.",
#                 }
#             )
#             continue
#
#         subject_dict = {
#             "subject_name": subject_name,
#             "subject_code": subject_code,
#             "credits": credits,
#             "weekly_quota_limit": weekly_quota_limit,
#             "is_special_subject": is_special_subject,
#             "department": department,
#             "course": course,
#             "branch": branch,
#             "semester": semester,
#         }
#
#         serializer = SubjectSerializer(data=subject_dict)
#         if serializer.is_valid():
#             serializer.save()
#             added_subjects.append(serializer.data)
#         else:
#             errors.append({"subject_data": subject_data, "errors": serializer.errors})
#
#     if errors:
#         return Response(
#             {"added_subjects": added_subjects, "errors": errors},
#             status=400 if not added_subjects else 207,
#         )
#
#     return Response(
#         {"message": "Subjects added successfully.", "subjects": added_subjects},
#         status=201,
#     )
#
#
# @api_view(["PUT"])
# @permission_classes([IsAuthenticated])
# def updateSubject(request, pk):
#     """
#     Update an existing subject by ID.
#     """
#     try:
#         subject = Subject.objects.get(id=pk)
#     except Subject.DoesNotExist:
#         return Response({"error": "Subject not found"}, status=404)
#
#     new_subject_code = request.data.get("subject_code")
#     if (
#         new_subject_code
#         and Subject.objects.filter(subject_code=new_subject_code)
#         .exclude(id=pk)
#         .exists()
#     ):
#         return Response(
#             {
#                 "error": f"Subject code '{new_subject_code}' is already assigned to another subject."
#             },
#             status=400,
#         )
#
#     serializer = SubjectSerializer(instance=subject, data=request.data, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=200)
#     else:
#         return Response(serializer.errors, status=400)
#
#
# @api_view(["DELETE"])
# @permission_classes([IsAuthenticated])
# def deleteSubject(request, pk):
#     """
#     Delete a subject by ID.
#     """
#     try:
#         subject = Subject.objects.get(id=pk)
#         subject.delete()
#         return Response({"message": "Subject deleted successfully"}, status=200)
#     except Subject.DoesNotExist:
#         return Response({"error": "Subject not found"}, status=404)
#
# def addStudent(
#     student_name,
#     student_id,
#     is_hosteller,
#     location,
#     department,
#     course,
#     branch,
#     year,
#     section,
#     cgpa,
# ):
#     try:
#         student, created = Student.objects.get_or_create(
#             student_id=student_id,
#             defaults={
#                 "student_name": student_name,
#                 "is_hosteller": is_hosteller,
#                 "location": location,
#                 "department": department,
#                 "course": course,
#                 "branch": branch,
#                 "semester": year,
#                 "section": section,
#                 "cgpa": cgpa,
#             },
#         )
#         if created:
#             return {
#                 "status": "success",
#                 "message": "Student added successfully",
#                 "student": student,
#             }
#         else:
#             return {
#                 "status": "error",
#                 "message": f"Student ID {student_id} already exists.",
#             }
#     except Exception as e:
#         print(f"Error adding student {student_id}: {str(e)}")
#         return {"status": "error", "message": str(e)}
#
# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def addStudentAPI(request):
#     mongo = MongoDriver()
#     files = request.FILES.getlist("file")
#     dept = request.data.get("department")
#     course = request.data.get("course")
#     branch = request.data.get("branch")
#     year = request.data.get("year")
#     total_sections = request.data.get("total_sections")
#
#     if not files:
#         return Response({"error": "No files uploaded"}, status=400)
#
#     try:
#         total_sections = int(total_sections)
#         if total_sections <= 0:
#             raise ValueError("Total sections must be a positive integer.")
#     except ValueError:
#         return Response({"error": "Invalid total_sections value"}, status=400)
#
#     all_students = []
#     for file in files:
#         try:
#             data = pd.read_excel(file).fillna("")
#             data.columns = data.columns.str.lower()
#             if data.empty:
#                 continue
#             students_list = data.to_dict(orient="records")
#             all_students.extend(students_list)
#         except Exception as e:
#             return Response({"error": f"Error processing {file.name}: {str(e)}"}, status=400)
#
#     total_students = len(all_students)
#     if total_students == 0:
#         return Response({"error": "No students found in uploaded files"}, status=400)
#
#     class_strength = total_students // total_sections
#     extra_students = total_students % total_sections
#
#     scorer = StudentScorer()
#     students_with_scores = scorer.assign_scores_to_students(all_students)
#     students_with_scores.sort(key=lambda x: x["score"], reverse=True)
#
#     def get_section_label(index):
#         letters = string.ascii_uppercase
#         if index < 26:
#             return letters[index]
#         else:
#             return letters[(index // 26) - 1] + letters[index % 26]
#
#     section_labels = [get_section_label(i) for i in range(total_sections)]
#     sections = {label: [] for label in section_labels}
#     student_index = 0
#
#     for section in section_labels:
#         while len(sections[section]) < class_strength and student_index < total_students:
#             sections[section].append(students_with_scores[student_index])
#             student_index += 1
#
#     for i in range(extra_students):
#         sections[section_labels[i]].append(students_with_scores[student_index])
#         student_index += 1
#
#     if "student_distribution" not in mongo.list_collections():
#         mongo.db.create_collection("student_distribution")
#     mongo.delete_many("student_distribution", {"course": course, "department": dept, "branch": branch, "year": year})
#     student_distribution = {
#         "course": course,
#         "department": dept,
#         "branch": branch,
#         "year": year,
#         "sections": []
#     }
#
#     for section, students in sections.items():
#         student_distribution["sections"].append({
#             "section": section,
#             "strength": len(students),
#             "students": students
#         })
#
#     inserted = mongo.insert_one("student_distribution", student_distribution)
#
#     if "section" not in mongo.list_collections():
#         mongo.db.create_collection("section")
#     mongo.delete_many("section", {"course": course, "department": dept, "branch": branch, "year": year})
#     section_structure = {
#         "course": course,
#         "department": dept,
#         "branch": branch,
#         "year": year,
#         "total_sections": total_sections,
#         "sections": [{"section": sec["section"], "strength": sec["strength"]} for sec in student_distribution["sections"]]
#     }
#
#     mongo.insert_one("section", section_structure)
#
#     return Response({
#         "message": "Students processed successfully"
#     }, status=200)
#
#
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def listSections(request):
#     course = request.query_params.get("course")
#     department = request.query_params.get("department")
#     branch = request.query_params.get("branch")
#     year = request.query_params.get("year")
#
#     if not all([course, department, branch, year]):
#         return Response({"error": "Missing required parameters (course, department, branch, year)"}, status=400)
#
#     mongo = MongoDriver()
#
#     query = {
#         "course": course,
#         "department": department,
#         "branch": branch,
#         "year": year
#     }
#     sections_cursor = mongo.find("student_distribution", query)
#
#     sections = []
#
#
#     for record in sections_cursor:
#         for section in record["sections"]:
#             sections.append({
#                 "mongo_id": str(record["_id"]),
#                 "section": section["section"],
#             })
#
#     # Check if no sections were found
#     if not sections:
#         return Response({"error": "No sections found for the specified filters"}, status=404)
#
#     return Response({"sections": sections}, status=200)
#
#
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def downloadSections(request, mongo_id):
#     mongo = MongoDriver()
#
#     try:
#         object_id = ObjectId(mongo_id)
#     except Exception:
#         return Response({"error": "Invalid Mongo ID"}, status=400)
#
#     section_cursor = mongo.find("student_distribution", {"sections._id": object_id}).limit(1)
#     section_list = list(section_cursor)
#
#     if not section_list:
#         return Response({"error": "Section not found for the given Mongo ID"}, status=404)
#
#     section_data = section_list[0]
#     section_to_download = None
#
#     for section in section_data["sections"]:
#         if section["_id"] == object_id:
#             section_to_download = section
#             break
#
#     if not section_to_download:
#         return Response({"error": "Section not found in the specified record"}, status=404)
#
#     df = pd.DataFrame(section_to_download["students"])
#     csv_buffer = io.StringIO()
#     df.to_csv(csv_buffer, index=False)
#
#
#     filename = f"{section_data['course']}_{section_data['department']}_{section_data['branch']}_{section_data['year']}_Section{section_to_download['section']}.csv"
#     response = HttpResponse(csv_buffer.getvalue(), content_type="text/csv")
#     response["Content-Disposition"] = f'attachment; filename="{filename}"'
#
#     return response
#
#
#
# @csrf_exempt
# def detectConflicts(request):
#     if request.method == "POST" and request.FILES.getlist("csv_files"):
#         try:
#             csv_files = request.FILES.getlist("csv_files")
#             timetables = []
#             file_names = []
#
#             for csv_file in csv_files:
#                 timetable_json = csv_to_json(csv_file)
#                 timetables.append(json.loads(timetable_json))
#                 file_names.append(csv_file.name)
#
#             conflict_checker = IsConflict()
#             conflict_results = []
#             has_conflicts = False
#
#             for i in range(len(timetables)):
#                 for j in range(i + 1, len(timetables)):
#                     timetable1 = timetables[i]
#                     timetable2 = timetables[j]
#
#                     conflicts = conflict_checker.process_schedules(
#                         timetable1, timetable2
#                     )
#
#                     if conflicts:
#                         has_conflicts = True
#                         conflict_results.append(
#                             {
#                                 "timetable_1": file_names[i],
#                                 "timetable_2": file_names[j],
#                                 "conflict_details": conflicts,
#                             }
#                         )
#
#             if has_conflicts:
#                 return JsonResponse({"conflicts": conflict_results}, status=200)
#             else:
#                 return JsonResponse(
#                     {"message": "No conflicts found between any two timetables."},
#                     status=200,
#                 )
#
#         except Exception as e:
#             return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=400)
#
#     return JsonResponse(
#         {"error": "Invalid request. Please provide CSV files."}, status=400
#     )
