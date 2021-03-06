import arrow
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q, Sum
from django.template.defaultfilters import pluralize
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from vishleva.models import CommentMixin, CommonInfo, NullableEmailField


class EventManager(models.Manager):
    """ Event model manager """

    def get_expenses(self, queryset=None):
        """
        :param queryset: EventManager queryset
        :type queryset: EventManager queryset
        :return: expenses sum
        :rtype: int
        """
        queryset = queryset if queryset is not None else self.get_queryset()
        result = queryset.extra().aggregate(Sum('expenses'))
        return result['expenses__sum'] if result['expenses__sum'] else 0

    def get_total(self, queryset=None, with_expenses=False):
        """
        :param queryset: EventManager queryset
        :type queryset: EventManager queryset
        :param with_expenses: with expenses?
        :type with_expenses: bool
        :return: total sum
        :rtype: int
        """
        queryset = queryset if queryset is not None else self.get_queryset()
        result = queryset.extra().aggregate(Sum('total'))
        total = result['total__sum'] if result['total__sum'] else 0
        return total - self.get_expenses(
            queryset=queryset) if with_expenses else total

    def get_paid(
            self,
            queryset=None, ):
        """
        :param queryset: EventManager queryset
        :type queryset: EventManager queryset
        :return: expenses sum
        :rtype: int
        """
        queryset = queryset if queryset is not None else self.get_queryset()
        result = queryset.extra().aggregate(Sum('paid'))
        return result['paid__sum'] if result['paid__sum'] else 0

    def get_by_dates(self, begin, end, grouped=False):
        """
        :param begin: datetime.datetime
        :type begin: datetime.datetime
        :param end: datetime.datetime
        :type end: datetime.datetime
        :return: Events
        :rtype: queryset
        """
        queryset = self.get_queryset().filter(
            Q(end__range=(begin, end)) | Q(end__range=(begin, end)) | Q(
                begin__lte=begin, end__gte=end))
        return queryset

    def get_for_notification(self, begin=None, end=None, hours=24):
        """
        :param begin: from datetime
        :type begin: datetime.datetime
        :param end: to datetime
        :type hours: timedelta hours
        :param hours: int
        :type end: datetime.datetime
        :return: Events
        :rtype: queryset
        """
        begin = begin if begin else timezone.datetime.now()
        end = end if end else begin + timezone.timedelta(hours=hours)
        queryset = self.get_queryset()
        return queryset.filter(
            notified_at__isnull=True,
            status='open',
            begin__gte=begin,
            begin__lte=end)

    def get_for_closing(self, date=None):
        """
        :param date: close from date
        :type date: datetime.datetime
        :return: Events
        :rtype: queryset
        """
        date = arrow.Arrow.strptime(
            date, '%Y-%m-%d', settings.TIME_ZONE) if date else arrow.now()
        date = date.floor('day').to('UTC').datetime
        queryset = self.get_queryset()

        return queryset.filter(
            end__lt=date, paid__gte=F('total')).exclude(status='closed')


class Event(CommonInfo, CommentMixin):
    """
    Event model
    """

    STATUSES = (('not_confirmed', 'not confirmed'), ('open', 'open'),
                ('closed', 'closed'), )
    objects = EventManager()
    begin = models.DateTimeField(db_index=True)
    end = models.DateTimeField(db_index=True)
    title = models.CharField(max_length=255, db_index=True)
    total = models.PositiveIntegerField(
        default=0, db_index=True, validators=[MinValueValidator(0)])
    expenses = models.PositiveIntegerField(
        default=0, db_index=True, validators=[MinValueValidator(0)])
    paid = models.PositiveIntegerField(
        default=0, db_index=True, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=15, choices=STATUSES, db_index=True)
    client = models.ForeignKey(
        'Client',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="events")
    google_calendar_id = models.CharField(
        max_length=255,
        db_index=True,
        null=True,
        blank=True,
        help_text='google calendar event id')
    notified_at = models.DateTimeField(null=True, blank=True)

    def is_paid(self):
        return self.total - self.paid <= 0

    is_paid.boolean = True

    def duration(self):
        duration = self.end - self.begin
        seconds = duration.total_seconds()
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return '{} day{} {} hour{} {} minute{}'.format(
            duration.days,
            pluralize(duration.days), hours,
            pluralize(hours), minutes, pluralize(minutes))

    def __str__(self):
        return '{} - {}. {}'.format(
            timezone.localtime(self.begin).strftime('%d %B %Y %H:%M'),
            self.duration(), self.title)

    def clean(self):
        if self.begin and self.end:
            if self.begin >= self.end:
                raise ValidationError(
                    'End ({}) must be greater than begin ({})'.format(
                        self.end.strftime('%d %B %Y %H:%M'),
                        self.begin.strftime('%d %B %Y %H:%M')))
            query = Event.objects.filter(
                begin__lt=self.end, end__gt=self.begin)
            if self.id:
                query = query.exclude(pk=self.id)
            if query.count():
                raise ValidationError('Events already exists: , {}'.format(
                    '; '.join([str(v) for v in query])))

    class Meta:
        ordering = ['begin']


class Client(CommonInfo, CommentMixin):
    """
    Client model
    """
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), )
    first_name = models.CharField(max_length=100, db_index=True)
    last_name = models.CharField(
        max_length=100, db_index=True, null=True, blank=True)
    patronymic = models.CharField(
        max_length=100, db_index=True, null=True, blank=True)
    phone = PhoneNumberField(max_length=30, db_index=True, unique=True)
    social_url = models.URLField(
        max_length=250,
        null=True,
        blank=True,
        help_text='social profile url (vk, facebook, ect)')
    email = NullableEmailField(
        max_length=200, db_index=True, unique=True, null=True, blank=True)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, db_index=True)

    def __str__(self):
        return '{0} {1} {2}'.format(self.last_name, self.first_name,
                                    self.patronymic)

    class Meta:
        ordering = ['last_name', 'first_name']
