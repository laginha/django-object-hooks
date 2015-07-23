from django.db import models
from django.contrib.contenttypes.models import ContentType
import datetime

        
class HookQuerySet(models.QuerySet):
    def with_content_type(self, model):
        ct = ContentType.objects.get_for_model(model)
        return self.filter(content_type__pk=ct.pk)
    
    def valid(self):
        return self.filter(expiration_date__gte=datetime.date.today())
        
    def fetch(self, model=None, **kwargs):
        queryset = self.valid()
        if model:
            queryset = queryset.with_content_type(model)
        return queryset.filter(**kwargs)#.distinct('target')
