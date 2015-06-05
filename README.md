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
    user=user, 
    content_object=vehicle,
    target='http://www.example.com/vehicles',
)
```

and that's it! 
Whenever vehicle is saved, DOH handles the `post_save` signal and initiates the hook delivering process.


### Define payload

By default the payload in each request per hook is an empty json (`{}`). However you may define payloads per model as follows:

```python
class Vehicle(models.Model):
    ...
    
    def get_static_payload(self):
        # if this method exists, the payload will be fetched only once
        # and used for every hook within an event for this model
        return {
            'foo': 'bar'
        }
        
    def get_dynamic_payload(self, hook):
        # if this method exists, the payload will be fetched for each
        # hook in any event for this model
        return model_to_dict(hook.content_object)
```

### Send custom signals

```python
from django_object_hooks.signals import hook_event

hook_event.send(sender=Vehicle, instance=bus55, action='crashed', payload={})
```


## Delivering hooks

There are two configurable deliverers that play a part in notifying the targets:

- `HOOK_COLLECTION_DELIVERER` which is responsible for filtering the `Hook` model, dumping/serializing each payload and send it to the next deliverer
- `HOOK_DELIVERER` which is responsible to send an HTTP POST request to a target with a given payload


### Use celery

By default the deliveres are functions called within the `post_save` signal handling. However, you can override the settings to use Celery-Tasks driven deliverers

```python
# in settings.py
HOOK_COLLECTION_DELIVERER = "django_object_hooks.tasks.deliver_all_hooks"
HOOK_ELEMENT_DELIVERER = "django_object_hooks.tasks.deliver_hook"
```

There are 4 possible combinations of deliverers. Use the one you think it is best for you.


### Override base deliverers

Both the default and task-driven deliverers rely completely on two base deliveres: `AllHooksDeliverer` and `HookDeliverer`. From these you can create your own deliverers:

```python
from django_object_hooks.utils import AllHooksDeliverer
from django_object_hooks.utils import HookDeliverer

class MyCollectionDeliverer(AllHooksDeliverer):
    def dump_payload(self, payload):
        # you may override this method to use simplejson instead of ujson
        return simplejson.dumps(payload)

    def after_deliver(self, hooks):
        # you may use this method to do some logging
        logger.info('foobar')

deliver_all_hooks = MyCollectionDeliverer.deliver


class MyDeliverer(HookDeliverer):
    def after_deliver(self, response):
        # you may use this method to delete hooks
        if response.status_code in [404, 410]:
            Hook.object.filter(target=response.url).delete()            

deliver_hook = MyDeliverer.deliver
```

