from django import template
from django.http import HttpResponse
from django.template import loader
import markdown
import bleach
import json
from bs4 import BeautifulSoup
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.apps import apps

from .models import Post, User, PostCategory, Image

def post_detail(request, slug):

	template = loader.get_template('blog/post.html')

	if request.method == 'POST':
		try:
			post = Post.objects.get(id=request.POST.get('post-id', -1))
			post.content = request.POST.get('markdown', '')
			post.title = request.POST.get('title', '')
			post.author = User.objects.get(id=request.POST.get('user', ''))
			post.status = request.POST.get('status', '')
			post.category = PostCategory.objects.get(id=request.POST.get('category', ''))
		except Post.DoesNotExist:
			post = Post(content=request.POST.get('markdown', ''), title=request.POST.get('title', ''), author=User.objects.get(id=request.POST.get('user', '')), status=request.POST.get('status', ''))
		post.save()
	
	post = get_object_or_404(Post, slug=slug)


	md = markdown.Markdown(extensions=['toc', 'markdown.extensions.fenced_code', 'markdown.extensions.tables', 'extra'])
	cleaned = bleach.clean(post.content, tags=['blockquote', 'span', 'a'])
	post.content = md.convert(cleaned)
	user_profile = post.author.userprofile
	if md.toc_tokens:
		context = {'post': post, 'toc': md.toc, 'user_profile': user_profile}
	else:
		context = {'post': post, 'user_profile': user_profile}
	return HttpResponse(template.render(context, request))

def index(request, category='All'):
	md = markdown.Markdown(extensions=['markdown.extensions.fenced_code', 'markdown.extensions.tables', 'extra'])

	query = request.GET.get('q')
	if query:
		index = apps.get_app_config('blog').index
		results = index.search(query)
		posts = Post.objects.filter(status=1, id__in=tuple(results))
	elif category == 'All':
		posts = Post.objects.filter(status=1)
	elif category == 'Drafts':
		posts = Post.objects.filter(status=0)
	else:
		posts = Post.objects.filter(status=1, category__categories__contains=category)

	paginator = Paginator(posts, 8)
	page_number = request.GET.get('page', 1)
	page_posts = paginator.get_page(page_number)

	categories = PostCategory.objects.all()

	for post in page_posts:
		post.content_short = BeautifulSoup(md.convert(bleach.clean(post.content)), features="html.parser").find('p').text

	template = loader.get_template('blog/index.html')
	context = {'posts': page_posts, 'categories': categories, 'category': category}
	return HttpResponse(template.render(context, request))

def author_index(request, author_first_name, author_last_name):
	md = markdown.Markdown(extensions=['markdown.extensions.fenced_code', 'markdown.extensions.tables', 'extra'])
	posts = Post.objects.filter(status=1, author__first_name__contains=author_first_name, author__last_name__contains=author_last_name)

	paginator = Paginator(posts, 8)
	page_number = request.GET.get('page', 1)
	page_posts = paginator.get_page(page_number)

	categories = PostCategory.objects.all()

	for post in page_posts:
		post.content_short = BeautifulSoup(md.convert(bleach.clean(post.content)), features="html.parser").find('p').text

	template = loader.get_template('blog/index.html')
	context = {'posts': page_posts, 'categories': categories, 'category': 'All'}
	return HttpResponse(template.render(context, request))

def _get_edit_context(post):
	users = User.objects.all()
	categories = PostCategory.objects.all()
	user_profile = post.author.userprofile
	return {'post': post, 'user_profile': user_profile, 'users': users, 'categories': categories}


def post_editor(request, Id):
	template = loader.get_template('blog/post-editor.html')
	post = get_object_or_404(Post, id=Id)
	context = _get_edit_context(post)
	return HttpResponse(template.render(context, request))

def new_post(request):
	template = loader.get_template('blog/post-editor.html')
	post = Post(title="", author=request.user, content="", slug="new")
	context = _get_edit_context(post)
	return HttpResponse(template.render(context, request))

def post_image_upload(request):
	image = request.FILES.get('image')
	post_image = Image(user=User.objects.get(id=request.POST.get('user', '')), original_name=image.name, image=image)
	post_image.save()
	data = json.dumps({'image_url': post_image.image.url})
	return HttpResponse(data, content_type='application/json')

def delete_post(request, Id):
	template = loader.get_template('blog/post-delete.html')
	post = get_object_or_404(Post, id=Id)
	post.delete()
	context = {'post': post}
	return HttpResponse(template.render(context, request))










