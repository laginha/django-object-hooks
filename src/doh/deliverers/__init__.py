from .base import HooksDeliverer, HookDeliverer
from .eventlet import EventletDeliverer

deliver_hooks = HooksDeliverer.deliver
deliver_hooks_using_task = HooksDeliverer.delay

deliver_hook = HookDeliverer.deliver
deliver_hook_using_task = HookDeliverer.delay

deliver_hooks_using_eventlet = EventletDeliverer.deliver
deliver_hooks_using_eventlet_task = EventletDeliverer.delay
