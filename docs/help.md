# Help Wanted

There are still quite a few things I want to test and document. Contributions are welcome and encouraged!

- Complete the full suite of {json:api} tests to make sure all the various flavors of PATCH actually work.
- [`django-guardian`](https://django-guardian.readthedocs.io/en/stable/) model and object-level permissions.
- [`django-signals`](https://docs.djangoproject.com/en/stable/topics/signals/)
- Kafka-Avro-based SAGA stuff? Or AWS SQS, SNS, etc.
- Create a jsonapi.DefaultRouter that automates the added urlpatterns for relationships and related paths.
- Jenkins CI/CD setup for our private gitlab repo.
- Travis CI/CD setup for public github repo.
- Client app demos (with Jupyter notebook?)
    - conventional Python CLI client (in process; see `demo_jsonapi_cli`)
    - Single Page App (SPA) demo with [angular2-jsonapi](https://github.com/ghidoz/angular2-jsonapi)
