from django.apps import AppConfig
from modules.index import InvertedIndex
from myPersonalSite.settings import DEBUG


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    # create and start the in-memory inverted index
    if not DEBUG:
        index = InvertedIndex(from_file=True, in_s3=True)
    else:
        index = InvertedIndex(from_file=True)
    index.save()

