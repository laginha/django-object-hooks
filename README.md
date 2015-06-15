# Django object hooks

![DOH](http://www.recreateweb.com.au/wp-content/uploads/2014/02/homer-computer-doh.jpg)

Object-level Web Hook application. 

This project was heavily influence by [django-rest-hooks](https://github.com/zapier/django-rest-hooks).


## Basic usage

setup your settings:

```python
HOOK_ALLOWED_MODELS = [
    'app.Vehicle
]
```

create web hooks:

```python
vehicle = Vehicle.objects.get(type='bus', name='55')
Hook.objects.create(
    user=user, content_object=vehicle,
    target='http://www.example.com/vehicles',
)
```

and that's it! 

Whenever a `vehicle` is saved, DOH handles the `post_save` signal and initiates the hook delivering process.


### Define payload

```python
class Vehicle(models.Model):
    ...
    
    def get_static_payload(self):
        # if this method exists, the payload will be fetched only once
        # and used for every hook within an event for this model
        return model_to_dict(self)
        
    def get_dynamic_payload(self, hook):
        # if this method exists, the payload will be fetched for each
        # hook in any event for this model
        return {
            'resource_uri': 'http://foo.com/vehicles/{pk}'.format(pk=self.pk)
            'action': hook.action,
        }
```

By default the payload is an empty json (`{}`).


### Send custom signals

```python
from doh.signals import hook_event

hook_event.send(sender=Vehicle, instance=bus55, action='crashed', payload={})
```


## Deliverers

- `HOOK_COLLECTION_DELIVERER`: responsible for filtering the `Hook` model and dumping each payload.
- `HOOK_ELEMENT_DELIVERER`: responsible for sending a POST request to a target with a given payload.


### Use celery

```python
HOOK_COLLECTION_DELIVERER = "doh.deliveres.deliver_hooks_using_task"
HOOK_ELEMENT_DELIVERER = "doh.deliveres.deliver_hook_using_task"
```

You can just override one setting thus combining with the default deliverers.


### Use eventlet

```python
HOOK_COLLECTION_DELIVERER = "doh.deliveres.deliver_hooks_using_eventlet"
```

or

```python
HOOK_COLLECTION_DELIVERER = "doh.deliveres.deliver_hooks_using_eventlet_task"
```

> `HOOK_ELEMENT_DELIVERER` is not used in this case.


### Custom deliverers

Create your own custom deliverers from `HooksDeliverer` and `HookDeliverer`:

```python
from doh.deliverers.base import HooksDeliverer, HookDeliverer

class CustomHooksDeliverer(HooksDeliverer):
    def dump_payload(self, payload):
        # you may override this method to use simplejson instead of ujson
        return simplejson.dumps(payload)        

    def after_deliver(self, hooks):
        # you may use this method to do some logging
        logger.info('foobar')

deliver_hooks = CustomHooksDeliverer.deliver
deliver_hooks_using_task = CustomHooksDeliverer.delay


class CustomHookDeliverer(HookDeliverer):
    def after_deliver(self, response):
        # you may use this method to delete hooks
        if response.status_code in [404, 410]:
            Hook.object.filter(target=response.url).delete()            

deliver_hook = CustomHookDeliverer.deliver
deliver_hook_using_task = CustomHookDeliverer.delay
```
