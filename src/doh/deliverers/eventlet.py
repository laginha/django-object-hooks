import celery
import erequests
from .base import HooksDeliverer


class EventletDeliverer(HooksDeliverer):
    def deliver_each(self, hooks, payload=None):
        posts = []
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
            posts.append(erequests.async.post(each.target, data=dump))
        return erequests.map(posts)
        
deliver_hooks_using_eventlet = EventletDeliverer().deliver


class EventletDelivererTask(celery.task.Task, EventletDeliverer):
    ignore_result = False

    def run(self, app_label, model, instance_pk, action, payload=None):
        self.deliver(app_label, model, instance_pk, action, payload)

deliver_hooks_using_eventlet_task = EventletDelivererTask.delay
