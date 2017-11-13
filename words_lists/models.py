from django.contrib.auth.models import User
from django.db import models


class Word(models.Model):
    '''
    A word in a words list.
    '''
    word = models.CharField(max_length=256)

    def __str__(self):
        return self.word


class WordsList(models.Model):
    '''
    A list of words. The list is owned by a drawer, if it was created
    by one.
    Public lists are displayed as a choice for everyone in the server, while
    private ones are only for authenticated user who created their own lists.
    '''
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    public = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    words = models.ManyToManyField(Word)

    # Lists are never really deleted to avoid relationships with drawing rooms
    # and games to be broken.
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
