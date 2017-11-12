from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.models import User, AnonymousUser
from django.db import models
from ipware.ip import get_real_ip

from members.models import Profile


class Drawer(models.Model):
	'''
	Represents a drawer, associated with a site user (authenticated)
	or not (named anonymous). Any player in a drawing room gets a Drawer
	object in database, associated with its Profile model (for history
	and such things) if the user is authenticated.

	There is one Drawer record per user per room.
	'''
	profile = models.OneToOneField(
		Profile,
		blank=True,
		null=True,
		on_delete=models.SET_NULL
	)

	def is_registered_user(self):
		'''
		Checks if this drawer is a registered user
		'''
		return self.profile is not None


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
	owner = models.ForeignKey(Drawer, blank=True, null=True, on_delete=models.SET_NULL)
	public = models.BooleanField(default=False)
	order = models.IntegerField(default=0)
	words = models.ManyToManyField(Word)

	def __str__(self):
		return self.name


class DrawingRoom(models.Model):
	'''
	A drawing room, where a game is played. There is a slug for the URL.
	'''
	slug = models.CharField(max_length=16)
	words_list = models.ForeignKey(WordsList, on_delete=models.PROTECT)
	drawers = models.ManyToManyField(Drawer)

	# TODO add properties, room state, chronos, current word…

	def __str__(self):
		return (f'{self.slug} '
		        f'(drawers: {len(self.drawers)} -'
		        f' list: {self.words_list.name}#{self.words_list.id})')
