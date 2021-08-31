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
from myPersonalSite.settings import ALLOWED_HTML_TAGS, ALLOWED_HTML_ATTRS


from .models import Post, User, PostCategory, Image

def post_detail(request, slug):

	template = loader.get_template('blog/post.html')
	md = markdown.Markdown(extensions=['markdown.extensions.fenced_code', 'markdown.extensions.tables', 'extra'])

	if request.method == 'POST':
		header_image_id = request.POST.get('header-image-id')
		if header_image_id != "-1":
			image = Image.objects.get(id=header_image_id)
		else:
			image = None
		try:
			post = Post.objects.get(id=request.POST.get('post-id'))
			post.content = bleach.clean(request.POST.get('markdown'), tags=ALLOWED_HTML_TAGS, attributes=ALLOWED_HTML_ATTRS)
			post.first_paragraph = BeautifulSoup(md.convert(bleach.clean(post.content)), features="html.parser").find('p').text
			post.title = request.POST.get('title')
			post.author = User.objects.get(id=request.POST.get('user'))
			post.status = request.POST.get('status')
			post.category = PostCategory.objects.get(id=request.POST.get('category'))
			header_image_id = request.POST.get('header-image-id')
			post.title_image = image
		except Post.DoesNotExist:
			content = bleach.clean(request.POST.get('markdown'), tags=ALLOWED_HTML_TAGS, attributes=ALLOWED_HTML_ATTRS)
			post = Post(
				content = content, 
				first_paragraph = BeautifulSoup(md.convert(bleach.clean(content)), features="html.parser").find('p').text,
				title = request.POST.get('title', ''), 
				author = User.objects.get(id=request.POST.get('user')), 
				status = request.POST.get('status'),
				title_image = image,
				category = PostCategory.objects.get(id=request.POST.get('category'))
				)
		post.save()
		images = Image.objects.filter(post__isnull=True)
		for img in images:
			img.post = post
			img.save()
	
	post = get_object_or_404(Post, slug=slug)
	# convert markdown to html server-side
	post.content = md.convert(post.content)
	categories = PostCategory.objects.all()
	user_profile = post.author.userprofile
	context = {'post': post, 'user_profile': user_profile, 'categories': categories}
	return HttpResponse(template.render(context, request))

def index(request, category='All'):
	template = loader.get_template('blog/index.html')

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

	paginator = Paginator(posts, 6)
	page_number = request.GET.get('page', 1)
	page_posts = paginator.get_page(page_number)
	categories = PostCategory.objects.all()

	context = {'posts': page_posts, 'categories': categories, 'category': category}
	return HttpResponse(template.render(context, request))

def author_index(request, author_first_name, author_last_name):
	posts = Post.objects.filter(status=1, author__first_name__contains=author_first_name, author__last_name__contains=author_last_name)
	paginator = Paginator(posts, 8)
	page_number = request.GET.get('page', 1)
	page_posts = paginator.get_page(page_number)
	categories = PostCategory.objects.all()
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
	user = User.objects.get(id=request.POST.get('user', ''))
	post_image = Image(user=user, original_name=image.name, image=image)
	post_image.save()
	data = json.dumps({'image': {'url': post_image.image.url, 'id': post_image.id}})
	return HttpResponse(data, content_type='application/json')

def delete_post(request, Id):
	template = loader.get_template('blog/post-delete.html')
	post = get_object_or_404(Post, id=Id)
	post.delete()
	context = {'post': post}
	return HttpResponse(template.render(context, request))







