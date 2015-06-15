import requests
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from autofixture import AutoFixture
from .models import Hook, get_expiration_date
from .deliverers.base import HooksDeliverer
from .deliverers import deliver_hook, deliver_hooks
from .signals import hook_event


NUMBER = 10
CUSTOM_ACTION = 'died'


class HookTestCase(TestCase):

    def create_hook(self, user, instance, valid, action):
        if valid:
            path = instance.username.replace(' ', '_')
            target = 'http://localhost:8080/{path}'.format(path=path)
            Hook(
                user=user, 
                target=target, 
                action=action, 
                content_object=instance
            ).validate_and_save()
        else:
            Hook.objects.create(
                user=user, 
                target=instance.username, 
                action=action,
                content_object=instance
            )

    def create_users(self, number):
        return AutoFixture(User).create(number)
    
    def create_hooks(self, number, valid=False, action=Hook.DEFAULT_ACTION):
        users = self.create_users(number)
        for each in users:
            self.create_hook(users[0], each, valid=valid, action=action)

    def delete_all_hooks(self):
        Hook.objects.all().delete()

    def test_validate_and_save(self):
        user = self.create_users(1)[0]
        hook = Hook(user=user, target='http://example.com', content_object=user)
        try:
            hook.validate_and_save()
        except ValidationError:
            self.assertTrue(False)
        hook = Hook(user=user, target='example.com', content_object=user)
        try:
            hook.validate_and_save()
            self.assertTrue(False)
        except ValidationError:
            self.assertTrue(True)

    def test_default_expiration_date_delta(self):
        self.create_hooks(NUMBER)
        default_expiration_date = get_expiration_date().date()
        for each in Hook.objects.all():
            self.assertEqual(each.expiration_date.date(), default_expiration_date)
            self.assertEqual(each.expiration_date.year, each.creation_date.date().year +10)
            
    def test_custom_expiration_date_delta(self):
        with self.settings(HOOK_EXPIRATION_DATE_DELTA=1):
            self.create_hooks(NUMBER)
            default_expiration_date = get_expiration_date()
            for each in Hook.objects.all():
                self.assertEqual(each.expiration_date.year, each.creation_date.date().year +1)

    def test_HooksDeliverer(self):
        self.create_hooks(NUMBER)
        hooked_user = User.objects.latest('id')
        deliverer = HooksDeliverer()
        hooks = deliverer.filter_hooks(
            'auth', 'User', hooked_user.pk, Hook.DEFAULT_ACTION
        )
        self.assertEqual(hooks.count(), 1)
        self.assertEqual(hooks[0].user, User.objects.all()[0])
        self.assertEqual(hooks[0].content_object, hooked_user)
        deliverer.deliver_hooks(hooks, {'foo':'bar'})
        self.assertEqual(Hook.objects.count(), NUMBER-1)
        
    def test_deliver_all(self):
        self.test_deliver_all_with_custom_action(Hook.DEFAULT_ACTION)
        
    def test_deliver_all_with_valid_target(self):
        self.test_deliver_all_with_custom_action_and_valid_target(Hook.DEFAULT_ACTION)
        
    def test_deliver_all_with_custom_action(self, action=None):
        self.create_hooks(NUMBER)
        ACTION = action or CUSTOM_ACTION
        user = User.objects.latest('id')
        deliver_hooks('auth', 'User', user.pk, ACTION, payload={})
        if ACTION == Hook.DEFAULT_ACTION:
            self.assertEqual(Hook.objects.count(), NUMBER-1)
        else:
            self.assertEqual(Hook.objects.count(), NUMBER)
        self.create_hook(user, user, action=ACTION, valid=False)
        deliver_hooks('auth', 'User', user.pk, ACTION, payload={})
        self.assertEqual(Hook.objects.count(), NUMBER-1)
        
    def test_deliver_all_with_custom_action_and_valid_target(self, action=None):
        self.create_hooks(NUMBER)
        ACTION = action or CUSTOM_ACTION
        user = User.objects.latest('id')
        deliver_hooks('auth', 'User', user.pk, ACTION, payload={})
        self.create_hook(user, user, action=ACTION, valid=True)
        try:
            deliver_hooks('auth', 'User', user.pk, ACTION, payload={})
            self.assertTrue(False)
        except requests.exceptions.ConnectionError:
            if ACTION == Hook.DEFAULT_ACTION:
                self.assertEqual(Hook.objects.count(), NUMBER)
            else:
                self.assertEqual(Hook.objects.count(), NUMBER+1)
         
    def test_deliver_hook(self):
        self.create_hooks(NUMBER)
        hook = Hook.objects.latest('id')
        deliver_hook(hook.target, {})
        self.assertEqual(Hook.objects.count(), NUMBER-1)
    
    def test_deliver_hook_with_valid_target(self):
        self.create_hooks(NUMBER, valid=True)
        hook = Hook.objects.latest('id')
        try:
            deliver_hook(hook.target, {})
            self.assertTrue(False)
        except requests.exceptions.ConnectionError:
            self.assertEqual(Hook.objects.count(), NUMBER)

    def test_post_save_receiver(self):
        self.create_hooks(NUMBER, valid=True)
        instance = Hook.objects.latest('id').content_object
        instance.save()
        with self.settings(HOOK_ALLOWED_MODELS=['auth.User']):
            try:
                instance.save()
                self.assertTrue(False)
            except requests.exceptions.ConnectionError:
                self.assertTrue(True) 
    
    def test_hook_event_receiver(self):
        self.create_hooks(NUMBER, valid=True)
        instance = Hook.objects.latest('id').content_object
        try:
            hook_event.send(sender=User, instance=instance, payload={})
            self.assertTrue(False)
        except requests.exceptions.ConnectionError:
            self.assertTrue(True)
            
    def test_hook_event_receiver_when_hook_doesnt_exist(self):
        self.create_hooks(NUMBER, valid=True)
        instance = Hook.objects.latest('id').content_object
        try:
            hook_event.send(sender=User, instance=instance, action=CUSTOM_ACTION, payload={})
            self.assertEqual(Hook.objects.count(), NUMBER)
        except requests.exceptions.ConnectionError:
            self.assertTrue(False)
            
    def test_hook_event_receiver_with_custom_action(self):
        self.create_hooks(NUMBER, valid=True)
        user = User.objects.latest('id')
        self.create_hook(user, user, action=CUSTOM_ACTION, valid=False)
        try:
            hook_event.send(sender=User, instance=user, action=CUSTOM_ACTION, payload={})
            self.assertEqual(Hook.objects.count(), NUMBER)
        except requests.exceptions.ConnectionError:
            self.assertTrue(False)
    
    def test_hook_event_receiver_with_custom_action_and_valid_target(self):
        self.create_hooks(NUMBER, valid=True)
        user = User.objects.latest('id')
        self.create_hook(user, user, action=CUSTOM_ACTION, valid=True)
        try:
            hook_event.send(sender=User, instance=user, action=CUSTOM_ACTION, payload={})
            self.assertTrue(False)
        except requests.exceptions.ConnectionError:
            self.assertEqual(Hook.objects.count(), NUMBER+1)
        
        