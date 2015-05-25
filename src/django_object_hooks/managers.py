import datetime
from django.db.models import query
from django.contrib.contenttypes.models import ContentType
from model_utils.managers import PassThroughManager


class QuerySetManager(query.QuerySet):
    @classmethod
    def manager(cls):
        return PassThroughManager.for_queryset_class(cls)()
        
        
class HookQuerySet(QuerySetManager):
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
