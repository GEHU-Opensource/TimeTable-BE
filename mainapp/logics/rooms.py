from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from mainapp.models import Room
from mainapp.serializers import RoomSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_rooms(request):
    """
    Retrieve a list of all rooms.
    """
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data, status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_room(request):
    """
    Add one or multiple rooms.
    """
    data = request.data if isinstance(request.data, list) else [request.data]
    added_rooms = []
    errors = []

    for room_data in data:
        existing_room = Room.objects.filter(
            room_code=room_data.get("room_code")
        ).first()
        if existing_room:
            errors.append(
                {
                    "room_data": room_data,
                    "error": f"Room with code {room_data.get('room_code')} already exists",
                }
            )
            continue

        serializer = RoomSerializer(data=room_data)
        if serializer.is_valid():
            serializer.save()
            added_rooms.append(serializer.data)
        else:
            errors.append({"room_data": room_data, "errors": serializer.errors})

    if errors:
        return Response(
            {"added_rooms": added_rooms, "errors": errors},
            status=400 if not added_rooms else 207,
        )
    return Response(added_rooms, status=201)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_room(request, pk):
    """
    Update an existing room by ID.
    """
    try:
        room = Room.objects.get(id=pk)

        new_room_code = request.data.get("room_code")
        if (
            new_room_code
            and Room.objects.filter(room_code=new_room_code).exclude(id=pk).exists()
        ):
            return Response(
                {
                    "error": f"Room code '{new_room_code}' is already assigned to another room."
                },
                status=400,
            )

        serializer = RoomSerializer(instance=room, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)
    except Room.DoesNotExist:
        return Response({"error": "Room not found"}, status=404)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_room(request, pk):
    """
    Delete a room by ID.
    """
    try:
        room = Room.objects.get(id=pk)
        room.delete()
        return Response({"message": "Room deleted successfully"}, status=200)
    except Room.DoesNotExist:
        return Response({"error": "Room not found"}, status=404)
