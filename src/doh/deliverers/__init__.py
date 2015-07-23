from .base import HooksDeliverer, HookDeliverer
from .gevent import GeventDeliverer

deliver_hooks = HooksDeliverer.deliver
deliver_hooks_using_task = HooksDeliverer.delay

deliver_hook = HookDeliverer.deliver
deliver_hook_using_task = HookDeliverer.delay

deliver_hooks_using_gevent = GeventDeliverer.deliver
deliver_hooks_using_gevent_task = GeventDeliverer.delay
