from requests.exceptions import MissingSchema
from requests.exceptions import InvalidSchema
from requests.exceptions import InvalidURL
from doh.models import Hook
from .base import HooksDeliverer
import grequests


class GeventDeliverer(HooksDeliverer):
    
    def exception_handler(request, exception):
        if isinstance(exception, (MissingSchema, InvalidSchema, InvalidURL)):
            Hook.objects.filter(target=request.url).delete()
    
    def deliver_to_target(self, target, dump):
        return grequests.post(target, data=dump),
        
    def deliver_hooks(self, hooks, payload=None):
        posts = [req for req in self.delivering(hooks, payload)]
        return grequests.map(posts, exception_handler=exception_handler)
