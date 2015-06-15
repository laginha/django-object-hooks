import erequests
from .base import HooksDeliverer

class EventletDeliverer(HooksDeliverer):
    
    def deliver_to_target(self, target, dump):
        return erequests.async.post(target, data=dump)
        
    def deliver_hooks(self, hooks, payload=None):
        posts = [req for req in self.delivering(hooks, payload)]
        return erequests.map(posts)
