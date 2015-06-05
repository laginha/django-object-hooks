import celery
from doh.deliverers.base import HooksDeliverer, HookDeliverer
from .eventlet import EventletDeliverer


class HooksDelivererTask(celery.task.Task, HooksDeliverer):
    ignore_result = False
    
    def run(self, app_label, model, instance_pk, action, payload=None):
        self.deliver(app_label, model, instance_pk, action, payload)

deliver_hooks_using_task = HooksDelivererTask.delay


class HookDelivererTask(celery.task.Task, HookDeliverer):
    ignore_result = False

    def run(self, target, payload):
        self.deliver(target, payload)

deliver_hook_using_task = HookDelivererTask.delay
