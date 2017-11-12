from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
	'''
	An user profile (to add data to the standard contrib.auth User model)
	'''
	user = models.OneToOneField(User)
	ip_address = models.GenericIPAddressField(
		'Drawer IP',
		blank=True,
		null=True
	)


User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])
