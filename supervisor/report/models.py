from django.db import models
from django.conf import settings
from dateutil import parser


class Ticket(models.Model):
    tn = models.CharField(max_length=255, unique=True, verbose_name='Номер заявки')
    tid = models.IntegerField(primary_key=True)
    tcreatetime = models.DateField(blank=True, null=True, verbose_name='Дата и время регистрации обращения')
    service_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Сервис, подсервис')
    user_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Владелец')
    ticket_state_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Статус')
    queue_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='Очередь')
    artsubject = models.CharField(max_length=255, blank=True, null=True, verbose_name='Тема')
    artbody = models.CharField(max_length=255, blank=True, null=True, verbose_name='Текст обращения')
    note = models.CharField(max_length=255, blank=True, null=True, verbose_name='Заметка')
    auto_close = models.DateField(blank=True, null=True,
                                  verbose_name='Дата и время постановки обращения на автозакрытие')
    closed = models.DateField(blank=True, null=True, verbose_name='Дата и время закрытия заявки')
    moved_count = models.IntegerField(default=0, blank=True, null=True, verbose_name='Число смены очередей')
    first_line_emergence_time = models.DateField(blank=True, null=True,
                                                 verbose_name='Дата и время появления на первой линии')
    first_move_or_lock_time = models.DateField(blank=True, null=True,
                                               verbose_name='Время первого перемещения или блокировки первой линии')
    others_line_emergence_time = models.DateField(blank=True, null=True,
                                                  verbose_name='Время появления на второй линии')
    others_line_lock_time = models.DateField(blank=True, null=True,
                                             verbose_name='Время первого действия со стороны второй линии')
    others_line_message_time = models.FloatField(blank=True, null=True, verbose_name='Время ответа другой линии')
    auto_closed = models.FloatField(blank=True, null=True,
                                    verbose_name='Сколько прошло до постановки на автозакрытие заявки')
    forced_close = models.FloatField(blank=True, null=True,
                                     verbose_name='Сколько прошло до решения заявки')
    in_working_first = models.FloatField(blank=True, null=True, verbose_name='Время работы первой линии')
    in_working_others = models.FloatField(blank=True, null=True, verbose_name='Время первой реакции второй линии')

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return self.tn

    def save(self, *args, **kwargs):
        if self.tcreatetime:
            self.tcreatetime = parser.parse(self.tcreatetime)
        if self.auto_close:
            self.auto_close = parser.parse(self.auto_close)
        if self.closed:
            self.closed = parser.parse(self.closed)
        if self.first_line_emergence_time:
            self.first_line_emergence_time = parser.parse(self.first_line_emergence_time)
        if self.first_move_or_lock_time:
            self.first_move_or_lock_time = parser.parse(self.first_move_or_lock_time)
        if self.others_line_emergence_time:
            self.others_line_emergence_time = parser.parse(self.others_line_emergence_time)
        if self.others_line_lock_time:
            self.others_line_lock_time = parser.parse(self.others_line_lock_time)
        super(Ticket, self).save(*args, **kwargs)


class Review(models.Model):
    ticket_id = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    note = models.TextField()
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)
