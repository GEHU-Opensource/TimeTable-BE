from django.urls import path
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import (
    login,
    getSpecificTeacher,
    mongo_status,
    postgres_status,
    getRooms,
    addRoom,
    updateRoom,
    deleteRoom,
    getTeachers,
    addTeacher,
    updateTeacher,
    deleteTeacher,
    getAllSubjects,
    getFilteredSubjects,
    addSubject,
    updateSubject,
    deleteSubject,
    generate_timetable,
    addStudentAPI,
    detectConflicts,
    downloadSections,
    listSections,
)

schema_view = get_schema_view(
    openapi.Info(
        title="GEHU Timetable API",
        default_version="v1",
        description="API for managing timetables and related data",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="vc.vibha23@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # login route
    path("login/", login, name="login"),
    # check database connection
    path("mongo-status/", mongo_status, name="mongo-status"),
    path("postgres-status/", postgres_status, name="postgres-status"),
    # JWT Authentication Routes
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # room's apis
    path("getRooms/", getRooms, name="get-rooms"),
    path("addRoom/", addRoom, name="add-room"),
    path("updateRoom/<int:pk>/", updateRoom, name="update-room"),
    path("deleteRoom/<int:pk>/", deleteRoom, name="delete-room"),
    # teacher's apis
    path("getSpecificTeacher/", getSpecificTeacher, name="get-Specific-Teacher"),
    path("getTeachers/", getTeachers, name="get-Teachers"),
    path("addTeacher/", addTeacher, name="add-Teacher"),
    path("updateTeacher/<int:pk>/", updateTeacher, name="update-Teacher"),
    path("deleteTeacher/<int:pk>/", deleteTeacher, name="delete-Teacher"),
    # subject's apis
    path("getAllSubjects/", getAllSubjects, name="get-all-subjects"),
    path(
        "getFilteredSubjects/filter", getFilteredSubjects, name="get-filtered-subjects"
    ),
    path("addSubject/", addSubject, name="add-subject"),
    path("updateSubject/<int:pk>/", updateSubject, name="update-subject"),
    path("deleteSubject/<int:pk>/", deleteSubject, name="delete-subject"),
    # generate timetable api
    path("generateTimetable/", generate_timetable, name="generate-timetable"),
    # detect conflicts
    path("detectConflicts/", detectConflicts, name="detect-conflicts"),
    # swagger
    path(
        "swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc-ui"),
    # csv to chromosome
    path("addStudentAPI/", addStudentAPI, name="addStudentAPI"),
    path('download/<str:mongo_id>/<str:section_label>/', downloadSections, name="download_sections"),
    path("listSections/",listSections,name="listSections"),
]
