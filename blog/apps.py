from django.apps import AppConfig
from modules.index import InvertedIndex


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    # create and start the in-memory inverted index
    index = InvertedIndex(from_file=True)
    index.save()

