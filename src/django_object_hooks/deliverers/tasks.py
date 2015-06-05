import celery
from .base import HooksDeliverer, HookDeliverer
from .eventlet import EventletDeliverer


class HooksDelivererTask(celery.task.Task, HooksDeliverer):
    ignore_result = False
    
    def run(self, app_label, model, instance_pk, action, payload=None):
        self.deliver(app_label, model, instance_pk, action, payload)

deliver_all_hooks = HooksDelivererTask.delay


class EventletDelivererTask(celery.task.Task, EventletDeliverer):
    ignore_result = False

    def run(self, app_label, model, instance_pk, action, payload=None):
        self.deliver(app_label, model, instance_pk, action, payload)

deliver_all_hooks = EventletDelivererTask.delay


class HookDelivererTask(celery.task.Task, HookDeliverer):
    ignore_result = False

    def run(self, target, payload):
        self.deliver(target, payload)

deliver_hook = HookDeliverer.delay
