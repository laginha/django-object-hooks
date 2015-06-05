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
        
deliver_all_hooks = EventletDeliverer().deliver
