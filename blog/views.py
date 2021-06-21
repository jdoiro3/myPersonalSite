from django.http import HttpResponse
from django.template import loader
import markdown
import bleach
from bs4 import BeautifulSoup
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.apps import apps

from .models import Post, User, PostCategory

def post_detail(request, slug):

	template = loader.get_template('blog/post.html')
	post = get_object_or_404(Post, slug=slug)

	if request.method == 'POST':
		post.content = request.POST.get('markdown', '')
		post.title = request.POST.get('title', '')
		post.author = User.objects.get(id=request.POST.get('user', ''))
		post.save()

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

	paginator = Paginator(posts, 10)
	page_number = request.GET.get('page', 1)
	page_posts = paginator.get_page(page_number)

	categories = PostCategory.objects.all()

	for post in page_posts:
		post.content_short = BeautifulSoup(md.convert(bleach.clean(post.content)), features="html.parser").find('p').text

	template = loader.get_template('blog/index.html')
	context = {'posts': page_posts, 'categories': categories, 'category': 'All'}
	return HttpResponse(template.render(context, request))

def post_editor(request, Id):
	template = loader.get_template('blog/post-editor.html')
	post = get_object_or_404(Post, id=Id)
	users = User.objects.all()
	user_profile = post.author.userprofile
	context = {'post': post, 'user_profile': user_profile, 'users': users}
	return HttpResponse(template.render(context, request))

def new_post(request):
	template = loader.get_template('blog/post-editor.html')
	post = Post(title="", author=request.user, content="", slug="new")
	users = User.objects.all()
	user_profile = post.author.userprofile
	context = {'post': post, 'user_profile': user_profile, 'users': users}
	return HttpResponse(template.render(context, request))





