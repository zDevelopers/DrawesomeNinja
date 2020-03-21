from django.contrib import admin
from .models import DrawingRoom, Drawer, Draw, DrawingGame

admin.site.register(DrawingRoom)
admin.site.register(DrawingGame)
admin.site.register(Drawer)
admin.site.register(Draw)
