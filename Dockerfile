# Runs myapp under gunicorn.
# N.B. needs an external web server for the static files by sharing volume /var/www/html
FROM python:3

WORKDIR /usr/src/app

ENV DJANGO_DEBUG=false
ENV OAUTH2_SERVER=https://oauth-test.cc.columbia.edu
ENV RESOURCE_SERVER_ID=demo-django-jsonapi-training_validator
ENV RESOURCE_SERVER_SECRET=SaulGoodman

COPY requirements-django.txt .
COPY dist/*whl .
COPY myapp/fixtures/testcases.yaml .
COPY myapp/fixtures/adminuser.yaml .

# can manually login and create the superuser with:
# docker exec -it graviteeioapiplatform_demo_app_1 bash
# root@demoapp:/usr/src/app# django-admin createsuperuser --settings=training.settings
# or just pull one in with a fixture which is *not* in the git repo

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-django.txt && \
    pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir *whl && \
    django-admin migrate --settings=training.settings && \
    django-admin loaddata testcases.yaml --settings=training.settings && \
    django-admin loaddata adminuser.yaml --settings=training.settings && \
    mkdir -p /var/www/html && \
    django-admin collectstatic --no-input --clear --settings=training.settings

VOLUME /var/www/html
EXPOSE 9123

CMD ["sh","-c","gunicorn -b 0.0.0.0:9123 training.wsgi --workers 1"]
