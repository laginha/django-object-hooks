class DelivererMixin(object):
    ignore_result = False
     
    @classmethod
    def deliver(cls, *args, **kwargs):
        return cls().run(*args, **kwargs)
