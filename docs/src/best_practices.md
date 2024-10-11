# Best Practices


!!! note "General best practices"

    - Always return any "readable" value (es. True)
    - Uses [Persistent revokes](https://docs.celeryq.dev/en/stable/userguide/workers.html#worker-persistent-revokes)        


## Display progress

Inform what is happening inside your task

    @celery.task(bind=True)
    def long_task(self)-> bool:
        record = 1

        for entry in Model.objects.all():
            self.update_state(state='PROGRESS', meta={'current': record, 'entry': str(entry)})
            record += 1
        return True


## Sentry Integration

In case you use [Sentry](https://sentry.io/), add some useful information
    
    from functools import wraps
    
    def sentry_tags(func: Callable) -> Callable: 
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with configure_scope() as scope:
                scope.set_tag("celery", True)
                scope.set_tag("celery_task", func.__name__)
                return func(*args, **kwargs)
    
        return wrapper

    @celery.task(bind=True)
    @sentry_tags
    def task(self) -> bool:
        ...
        return True
