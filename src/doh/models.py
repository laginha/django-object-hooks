from django.db import models
from django.conf import settings
try:
    from django.contrib.contenttypes.fields import GenericForeignKey
except ImportError:
    from django.contrib.contenttypes.generic import GenericForeignKey    
from django.contrib.contenttypes.models import ContentType
from django.core.validators import URLValidator
from django.utils import timezone
from .managers import HookQuerySet


def get_expiration_date():
    now = timezone.now()
    return now.replace(
        year=now.year +getattr(settings, "HOOK_EXPIRATION_DATE_DELTA", 10)
    )


class Hook(models.Model):
    DEFAULT_ACTION = 'changed'
    expiration_date = models.DateTimeField(default=get_expiration_date, db_index=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    target = models.URLField(db_index=True)
    action = models.CharField(default=DEFAULT_ACTION, max_length=100, db_index=True)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    objects = models.Manager() 
    queryset = HookQuerySet.manager()
    
    def validate_and_save(self):
        models.URLField().run_validators(self.target)
        self.save()

    def __unicode__(self):
        return '%s %s %s' %(self.content_type, self.object_id, self.action)
