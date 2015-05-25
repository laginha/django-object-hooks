import celery
from .utils import AllHooksDeliverer, HookDeliverer


class DeliverAllHooksTask(celery.task.Task, AllHooksDeliverer):
    ignore_result = False
    
    def run(self, app_label, model, instance_pk, action, payload=None):
        self.deliver(app_label, model, instance_pk, action, payload)

deliver_all_hooks = DeliverAllHooksTask.delay


class DeliverHookTask(celery.task.Task, HookDeliverer):
    ignore_result = False

    def run(self, target, payload):
        self.deliver(target, payload)

deliver_hook = DeliverHookTask.delay