from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import os
from hashlib import sha1
from django.utils.html import mark_safe
from django.apps import apps
from modules.index import Document

STATUS = (
	(0, "Draft"),
	(1, "Published")
	)

TITLE_COLORS = (
	(0, "white"),
	(1, "black")
	)

class ImageBase:

	def image_dir(self, filename):
		image = self.title_image.open()
		content = image.read()
		sha1_hash = sha1(content)
		return f'{sha1_hash.hexdigest()[0:2]}/{sha1_hash.hexdigest()[2:]}'

class PostCategory(models.Model):
	categories = models.CharField(max_length=20)

	def __str__(self):
		return self.categories

class Post(models.Model, ImageBase):

	title = models.CharField(max_length=200, unique=True)
	title_color = models.IntegerField(choices=TITLE_COLORS, default=0)
	category = models.ForeignKey(PostCategory, on_delete=models.CASCADE, related_name='posts', blank=True, null=True)
	slug = models.SlugField(default='', editable=False)
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
	created_on = models.DateField(auto_now_add=True)
	updated_on = models.DateField(auto_now=True)
	content = models.TextField()
	status = models.IntegerField(choices=STATUS, default=0)
	title_image = models.ImageField(upload_to=ImageBase.image_dir, blank=True, max_length=255)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		doc = Document(self.pk, self.content, self.title, self.author.first_name, self.author.last_name)
		index = apps.get_app_config('blog').index
		index.add(doc)
		index.save()
		super().save(*args, **kwargs)

	@property
	def title_image_preview(self):
		if self.title_image:
			return mark_safe('<img src="{0}" width="{1}" height="{2}" />'.format(self.title_image.url, min(500, self.title_image.width), min(500, self.title_image.height)))
		return ""

	def __str__(self):
		return self.title


class PostImage(models.Model, ImageBase):

	@property
	def image_preview(self):
		if self.image:
			return mark_safe('<img src="{0}" width="{1}" height="{2}" />'.format(self.image.url, min(500, self.image.width), min(500, self.image.height)))
		return ""

	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='blog_post')
	image = models.ImageField(upload_to=ImageBase.image_dir)



class UserProfile(models.Model, ImageBase):

	@property
	def avatar_preview(self):
		if self.avatar:
			return mark_safe('<img src="{0}" width="{1}" height="{2}" />'.format(self.avatar.url, min(500, self.avatar.width), min(500, self.avatar.height)))
		return ""

	user = models.OneToOneField(User, on_delete=models.CASCADE)
	avatar = models.ImageField(upload_to=ImageBase.image_dir, blank=True, max_length=255)
