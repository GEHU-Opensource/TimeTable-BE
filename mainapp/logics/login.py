from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from mainapp.models import Teacher


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
