from django.apps import apps

index = apps.get_app_config('blog').index
index.clean_up()