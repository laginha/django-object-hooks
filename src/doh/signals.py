from django.conf import settings
from django.utils.module_loading import import_string
from django.db.models.signals import post_save, post_delete
from django.dispatch import Signal, receiver
from .models import Hook

COLLECTION_DELIVERER = import_string(getattr(settings, 
    "HOOK_COLLECTION_DELIVERER", "doh.deliverers.deliver_hooks"
))


hook_event = Signal(providing_args=['instance', 'action', 'payload'])


def handle_hook_event(sender, instance, action, payload=None):
    if Hook.queryset.fetch(model=instance, action=action).exists():
        return COLLECTION_DELIVERER(
            app_label=sender._meta.app_label, 
            object_name=sender._meta.object_name,
            instance_pk=instance.pk, 
            action=action,
            payload=payload,
        )
    

@receiver(hook_event, dispatch_uid="doh_hook_event_handler")
def on_hook_event(sender, instance, action=Hook.DEFAULT_ACTION, payload=None, **kwargs):
    return handle_hook_event(sender, instance, action, payload)


@receiver(post_save, dispatch_uid="doh_post_save_handler")
def on_post_save(sender, instance, created, **kwargs):
    if not created:
        model_name = "{app_label}.{object_name}".format(
            app_label=sender._meta.app_label, 
            object_name=sender._meta.object_name
        )
        if model_name in getattr(settings, "HOOK_ALLOWED_MODELS", []):
            return handle_hook_event(sender, instance, Hook.DEFAULT_ACTION)
