from django.contrib import admin
from .models import Drawer, Word, WordsList, DrawingRoom

admin.site.register(Drawer)
admin.site.register(Word)
admin.site.register(WordsList)
admin.site.register(DrawingRoom)
