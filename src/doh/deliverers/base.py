import datetime
import ujson
import requests
import celery
from requests.exceptions import MissingSchema, InvalidSchema, InvalidURL
from django.db.models import Q
from django.db.models.loading import get_model
from django.conf import settings
from django.utils.module_loading import import_string
from doh.models import Hook
from .mixins import DelivererMixin


class HooksDeliverer(celery.task.Task, DelivererMixin):
    DEFAULT_DUMP = "{}"

    def dump_payload(self, payload):
        if isinstance(payload, basestring):
            return payload
        return ujson.dumps(payload)
        
    def deliver_to_target(self, target, data):
        if not hasattr(self, '_deliverer'):
            self._deliverer = import_string(getattr(settings, 
                "HOOK_ELEMENT_DELIVERER", "doh.deliverers.deliver_hook"
            ))
        return self._deliverer(target, data)
    
    def delivering(self, hooks, payload=None):
        if payload != None:
            dump = self.dump_payload(payload)
        for each in hooks:
            if payload == None:
                instance = each.content_object
                if hasattr(instance, 'get_static_payload'):
                    payload = instance.get_static_payload(each)
                    dump = self.dump_payload( payload )
                elif hasattr(instance, 'get_dynamic_payload'):
                    dump = self.dump_payload( instance.get_dynamic_payload(each) )
                else:
                    dump = self.DEFAULT_DUMP
            yield self.deliver_to_target(each.target, dump)
    
    def deliver_hooks(self, hooks, payload=None): 
        for each in self.delivering(hooks, payload):
            continue
    
    def filter_hooks(self, app_label, object_name, instance_pk, action):
        model = get_model(app_label, object_name)
        return Hook.queryset.fetch(
            model=model, object_id=instance_pk, action=action
        )
    
    def after_deliver(self, hooks):
        return              

    def run(self, app_label, object_name, instance_pk, action, payload=None):
        hooks = self.filter_hooks(app_label, object_name, instance_pk, action)
        if payload != None:
            self.deliver_hooks(hooks, payload=payload)
        else:
            self.deliver_hooks(hooks)
        self.after_deliver(hooks)
    

class HookDeliverer(celery.task.Task, DelivererMixin): 
           
    def after_deliver(self, response):
        if response.status_code == 410:
            Hook.object.filter(target=response.url).delete()

    def run(self, target, payload):
        try:
            response = requests.post(target, data=payload)
        except (MissingSchema, InvalidSchema, InvalidURL) as e:
            Hook.objects.filter(target=target).delete()
        else:
            self.after_deliver(response)

