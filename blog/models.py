from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import os
import math
from hashlib import sha1
from django.utils.html import mark_safe
from django.apps import apps
from modules.index import Document, Parser

STATUS = (
	(0, "Draft"),
	(1, "Published")
	)

class PostCategory(models.Model):
	categories = models.CharField(max_length=20)

	def __str__(self):
		return self.categories

class Image(models.Model):

	def image_dir(self, filename):
		# process the file and return the path where it will be saved
		image = self.image.open()
		content = image.read()
		sha1_hash = sha1(content)
		ext = filename.split('.')[1]
		hash = sha1_hash.hexdigest()
		return f'{hash[0:2]}/{hash[2:]}.{ext}'

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_images')
	original_name = models.CharField(max_length=200)
	image = models.ImageField(upload_to=image_dir)
	post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='post_images', blank=True, null=True)

	@property
	def image_preview(self):
		if self.image:
			return mark_safe('<img src="{0}" width="{1}" height="{2}" />'.format(self.image.url, min(500, self.image.width), min(500, self.image.height)))
		return ""

	def __str__(self):
		return self.original_name

class Post(models.Model):

	class Meta:
		ordering = ['-created_on']

	def image_dir(self, filename):
		image = self.title_image.open()
		content = image.read()
		sha1_hash = sha1(content)
		ext = filename.split('.')[1]
		return f'{sha1_hash.hexdigest()[0:2]}/{sha1_hash.hexdigest()[2:]}.{ext}'

	title = models.CharField(max_length=200)
	category = models.ForeignKey(PostCategory, on_delete=models.SET_NULL, related_name='posts', blank=True, null=True)
	slug = models.SlugField(default='', editable=False)
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
	created_on = models.DateField(auto_now_add=True)
	updated_on = models.DateField(auto_now=True)
	content = models.TextField()
	first_paragraph = models.TextField()
	status = models.IntegerField(choices=STATUS, default=0)
	title_image = models.ForeignKey(Image, on_delete=models.SET_NULL, related_name='blogs', blank=True, null=True)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super().save(*args, **kwargs)
		# update index
		doc = Document(self.pk, self.content, self.title, self.author.first_name, self.author.last_name)
		index = apps.get_app_config('blog').index
		if self.pk is not None:
			index.remove(doc)
		index.add(doc)
		index.save()

	def delete(self, *args, **kwargs):
		# remove document from index
		doc = Document(self.pk, self.content, self.title, self.author.first_name, self.author.last_name)
		index = apps.get_app_config('blog').index
		index.remove(doc)
		index.save()
		# delete from database
		super().delete(*args, **kwargs)

	@property
	def title_image_preview(self):
		if self.title_image:
			return mark_safe('<img src="{0}" width="{1}" height="{2}" />'.format(self.title_image.url, min(500, self.title_image.width), min(500, self.title_image.height)))
		return ""

	def __str__(self):
		return self.title

	def get_relevance_score(self, search):
		score = 0
		parser = Parser()
		doc = Document(self.pk, self.content, self.title, self.author.first_name, self.author.last_name)
		search_tokens = parser.parse(search, stem=False)
		for search_token in search_tokens:
			for field in doc.fields:
				field = field.lower()
				if search_token in field:
					term_freq = math.sqrt(field.count(search_token))
					norm = 1 / math.sqrt(len(parser.parse(field)))
					score += term_freq * norm
		return score

	
class UserProfile(models.Model):

	def image_dir(self, filename):
		image = self.avatar.open()
		content = image.read()
		sha1_hash = sha1(content)
		ext = filename.split('.')[1]
		return f'{sha1_hash.hexdigest()[0:2]}/{sha1_hash.hexdigest()[2:]}.{ext}'

	@property
	def avatar_preview(self):
		if self.avatar:
			return mark_safe('<img src="{0}" width="{1}" height="{2}" />'.format(self.avatar.url, min(500, self.avatar.width), min(500, self.avatar.height)))
		return ""

	user = models.OneToOneField(User, on_delete=models.CASCADE)
	avatar = models.ImageField(upload_to=image_dir, blank=True, max_length=255)
