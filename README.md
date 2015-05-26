# Django object hooks

![DOH](http://www.recreateweb.com.au/wp-content/uploads/2014/02/homer-computer-doh.jpg)

Object-level Web Hook application. 

This project was heavily influence by [django-rest-hooks](https://github.com/zapier/django-rest-hooks).


## Basic Usage

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


## Delivering Hooks

There are two configurable deliverers that play a part in notifying the targets:

- `HOOK_COLLECTION_DELIVERER` which is responsible for filtering the `Hook` model, dumping/serializing each payload and send it to the next deliverer
- `HOOK_DELIVERER` which is responsible to send an HTTP POST request to a target with a given payload


## Use celery

By default the deliveres are functions called within the `post_save` signal handling. However, you can override the settings to use Celery-Tasks driven deliverers

```python
# in settings.py
HOOK_COLLECTION_DELIVERER = "django_object_hooks.tasks.deliver_all_hooks"
HOOK_DELIVERER = "django_object_hooks.tasks.deliver_hook"
```

There are 4 possible combinations of deliverers. Use the one you think it is best for you.


## Override base deliverer

Both the default and task-driven deliverers rely completely on two base deliveres: `AllHooksDeliverer` and `HookDeliverer`. From these you can create your own deliverers:

```python
from django_object_hooks.utils import AllHooksDeliverer
from django_object_hooks.utils import HookDeliverer

class MyCollectionDeliverer(AllHooksDeliverer):
    def after_deliver(self):
        # does nothing by default
        
    def deliver(self, app_label, model, instance_pk, action, payload=None):
        ...

deliver_all_hooks = MyCollectionDeliverer.deliver

class MyDeliverer(HookDeliverer):
    def after_deliver(self, response):
        ...
        
    def deliver(self, target, payload):
        ...

deliver_hook = MyDeliverer.deliver
```

