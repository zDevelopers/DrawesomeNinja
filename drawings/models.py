from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from words_lists.models import Word, WordsList


DRAWING_GAMES_TYPES = (
    ('END_ON_SCORE', _('The game ends when a score is achieved by a player')),
    ('END_ON_TOUR', _('The game ends after a certain amount of tours')),
    ('END_ON_TIME', _('The game ends after a certain amount of time'))
)

DRAWING_GAMES_TYPES_DICT = dict(DRAWING_GAMES_TYPES)


class DrawingRoom(models.Model):
    '''
    A drawing room, where a game is played. There is a slug for the URL.
    '''
    STATES = (
        ('IDLE', _('Waiting to play')),
        ('IN_GAME', _('In game')),
        ('DEAD', _('Dead'))
    )

    # Properties of the room
    name = models.CharField(max_length=100, blank=True)
    slug = models.CharField(max_length=16)
    users = models.ManyToManyField(User)

    # State of the room
    state = models.CharField(
        choices=STATES,
        default=STATES[0][0],
        max_length=8
    )
    active_game = models.ForeignKey(
        'DrawingGame',
        blank=True,
        null=True,
        default=None,
        related_name='+'
    )

    # Default properties of the games in the room
    game_type = models.CharField(
        choices=DRAWING_GAMES_TYPES,
        default=DRAWING_GAMES_TYPES[0][0],
        max_length=16
    )
    words_list = models.ForeignKey(
        WordsList,
        on_delete=models.PROTECT,
        related_name='+'
    )
    tour_duration = models.IntegerField(
        _('Duration per tour, in minutes'),
        default=settings.DRAWESOME['GAMES_DEFAULTS']['TOUR_DURATION']
    )

    def __str__(self):
        return (f'{self.slug} '
                f'(drawers: {len(self.users)} -'
                f' list: {self.words_list.name}#{self.words_list.pk})')


class Drawer(models.Model):
    '''
    Represents a drawer, associated with a site user (authenticated)
    or not (named anonymous). Any player in a drawing room gets a Drawer
    object in database, associated with its Profile model (for history
    and such things) if the user is authenticated.

    If the user is authenticated, the username is always set to the value
    of user.username.

    There is one Drawer record per user per game.
    '''
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='drawers'
    )

    username = models.CharField(max_length=150, blank=True)
    score = models.IntegerField(verbose_name=_('The drawer\'s score in the game'))
    order = models.IntegerField(verbose_name=_('The drawer\'s order in the game'))

    def __str__(self):
        return f'{self.username} (authenticated: {self.is_registered_user()})'

    def is_registered_user(self):
        '''
        Checks if this drawer is a registered user
        '''
        return self.user is not None


@receiver(pre_save, sender=Drawer)
def set_username_to_user_name_if_authenticated(sender, instance, raw, **kwargs):
    '''
    Ensures the username stored here is always the associated user's username,
    if there is one. Else, does not alters anything.

    TODO unit test.
    '''
    if not raw and instance.is_registered_user():
        instance.username = instance.user.username


class Draw(models.Model):
    '''
    Represents a tour, a draw, in a drawing game.
    '''
    game = models.ForeignKey('DrawingGame', related_name='draws_history', on_delete=models.PROTECT)
    drawer = models.ForeignKey(Drawer, related_name='draws', on_delete=models.PROTECT)
    word = models.ForeignKey(Word, related_name='draws', on_delete=models.PROTECT)

    beginning = models.DateTimeField(
        verbose_name=_('Beginning of the draw'),
        auto_now_add=True
    )
    end = models.DateTimeField(
        verbose_name=_('End of the draw'),
        blank=True,
        null=True,
        default=None
    )

    skipped = models.BooleanField(default=False)
    skipped_because_AFK = models.BooleanField(default=False)

    guessed_by = models.ManyToManyField(
        Drawer,
        verbose_name=_('Word guessed by...'),
        related_name='guesses'
    )

    def __str__(self):
        return f'Draw by {self.drawer.username} of {self.word} in {self.game} (running: {self.is_running()})'

    def is_running(self):
        return self.end is None


class DrawingGame(models.Model):
    room = models.ForeignKey(DrawingRoom, on_delete=models.PROTECT)
    drawers = models.ManyToManyField(Drawer, related_name='games')

    # Game properties
    game_type = models.CharField(
        choices=DRAWING_GAMES_TYPES,
        default=DRAWING_GAMES_TYPES[0][0],
        max_length=16
    )
    words_list = models.ForeignKey(
        WordsList,
        on_delete=models.PROTECT,
        related_name='games'
    )
    tour_duration = models.IntegerField(
        _('Duration per tour, in minutes'),
        default=settings.DRAWESOME['GAMES_DEFAULTS']['TOUR_DURATION']
    )

    # Game state
    current_draw = models.ForeignKey(
        Draw,
        blank=True,
        null=True,
        default=None,
        on_delete=models.PROTECT,
        related_name='+'
    )

    # Game end
    winner = models.ForeignKey(
        Drawer,
        blank=True,
        null=True,
        default=None,
        on_delete=models.PROTECT,
        related_name='games_won'
    )

    # Others
    beginning = models.DateTimeField(
        verbose_name=_('Beginning of the draw'),
        auto_now_add=True
    )
    end = models.DateTimeField(
        verbose_name=_('End of the draw'),
        blank=True,
        null=True,
        default=None
    )

    def __str__(self):
        return f'Game in the {self.room.slug} room with {len(self.drawers)} players (running: {self.is_running()})'

    def is_running(self):
        return self.end is None

    def has_winner(self):
        '''
        Checks if this game has a winner. If not, and if the game
        is not running, the game was interrupted.
        '''
        return not self.is_running() and self.winner is None
