from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

from .logics.login import login
from .logics.rooms import get_rooms, add_room, update_room, delete_room
from .logics.students import addStudentAPI,listSections,downloadSections
from .logics.subjects import get_all_subjects, get_filtered_subjects, add_subject, update_subject, delete_subject
from .logics.teachers import get_specific_teacher, get_all_teachers, add_teacher, update_teacher, delete_teacher, update_password
from .logics.hod import get_pending_requests, approve_subject_requests, get_approved_subjects
from .logics.timetable import generate_timetable, detect_conflicts, manual_timetable_upload
from . import views


schema_view = get_schema_view(
    openapi.Info(
        title="GEHU Timetable API",
        default_version="v1",
        description="API for managing timetables and related data",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="timetablegehu@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Authentication and Database Status
    path("login/", login, name="login"),


    # JWT Authentication
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),


    # Room APIs
    path("getRooms/", get_rooms, name="get-rooms"),
    path("addRoom/", add_room, name="add-room"),
    path("updateRoom/<int:pk>/", update_room, name="update-room"),
    path("deleteRoom/<int:pk>/", delete_room, name="delete-room"),


    # Teacher APIs
    path("getSpecificTeacher/", get_specific_teacher, name="get-Specific-Teacher"),
    path("getAllTeachers/", get_all_teachers, name="get-Teachers"),
    path("addTeacher/", add_teacher, name="add-Teacher"),
    path("updateTeacher/<int:pk>/", update_teacher, name="update-Teacher"),
    path("deleteTeacher/<int:pk>/", delete_teacher, name="delete-Teacher"),
    path("updatePassword/", update_password, name="update-Password"),


    # HOD APIs
    path("getPendingRequests/", get_pending_requests, name="get-Pending-Requests"),
    path("approveSubjectRequests/", approve_subject_requests, name="approve-Subject-Requests"),
    path("getApprovedSubjects/", get_approved_subjects, name="get-Approved-Subjects"),


    # Subject APIs
    path("getAllSubjects/", get_all_subjects, name="get-all-subjects"),
    path("getFilteredSubjects/filter", get_filtered_subjects, name="get-filtered-subjects"),
    path("addSubject/", add_subject, name="add-subject"),
    path("updateSubject/<int:pk>/", update_subject, name="update-subject"),
    path("deleteSubject/<int:pk>/", delete_subject, name="delete-subject"),


    # Timetable and Conflict APIs
    path("timetable/generate/", generate_timetable, name="generate-timetable"),
    path("detectConflicts/", detect_conflicts, name="detect-conflicts"),
    # path("update-timetable/", views.updateTimeTable, name="update-timetable"),
    # path("current-timetable/<str:course_id>/<int:semester>/", views.getCurrentTimeTable, name="get-current-timetable"),
    # path("historical-timetables/<str:course_id>/<int:semester>/", views.getHistoricalTimeTable, name="get-historical-timetables"),


    # CSV and Student APIs
    path("timetable/manual/upload", manual_timetable_upload, name="manualTimeTableUpload"),
    path("addStudentAPI/", addStudentAPI, name="addStudentAPI"),



    # Documentation
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc-ui"),

    
    # Student APIs
    path("addStudentAPI/", addStudentAPI, name="addStudentAPI"),
    path("listSections/", listSections, name="listSections"),
    path("downloadSections/<str:mongo_id>/", downloadSections, name="downloadSections"),
]
