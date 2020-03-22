from django.shortcuts import render


def index(request):
    return render(request, 'drawings/index.html')

def drawing_room(request, room_id):
    return render(request, 'drawings/drawing_room.html', {
        'room_id': room_id
    })
