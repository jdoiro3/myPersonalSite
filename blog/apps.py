from django.apps import AppConfig
from modules.index import InvertedIndex


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    index = InvertedIndex()

    def ready(self):
    	self.index.save()

