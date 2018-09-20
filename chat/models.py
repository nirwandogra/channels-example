from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

from django.db import models
import ast

class ListField(models.TextField):
    __metaclass__ = models.SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

class Room(models.Model):
    name = models.TextField()
    label = models.SlugField(unique=True)

    def __unicode__(self):
        return self.label

class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages')
    handle = models.TextField()
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    def __unicode__(self):
        return '[{timestamp}] {handle}: {message}'.format(**self.as_dict())

    @property
    def formatted_timestamp(self):
        return self.timestamp.strftime('%b %-d %-I:%M %p')
    
    def as_dict(self):
        return {'handle': self.handle, 'message': self.message, 'timestamp': self.formatted_timestamp}

class Call(models.Model):
    call_id = models.CharField(max_length=255)
    def __unicode__(self):
        return self.call_id

class File(models.Model):
    name = models.CharField(max_length=255)
    text = models.CharField(max_length=255)
    callId = models.ForeignKey(Call)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    peopleInvolved = ListField()

    def __unicode__(self):
        return self.name

    class Meta:
       ordering = ['-date']

    def get_json(self, flag=0):
        return {
            'callId':self.callId.call_id,
            'name':self.name,
            'text':self.text,
            'peopleInvolved': self.peopleInvolved
        }

