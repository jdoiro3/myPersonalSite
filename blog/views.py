from django.http import HttpResponse
from django.template import loader
import markdown
import bleach
from bs4 import BeautifulSoup

from .models import Post, UserProfile, PostCategory

def post_detail(request, slug):
	template = loader.get_template('blog/post.html')
	post = Post.objects.get(slug=slug)
	md = markdown.Markdown(extensions=['toc', 'markdown.extensions.fenced_code', 'markdown.extensions.tables', 'extra'])
	cleaned = bleach.clean(post.content)
	post.content = md.convert(cleaned)
	user_profile = post.author.userprofile
	if md.toc_tokens:
		context = {'post': post, 'toc': md.toc, 'user_profile': user_profile}
	else:
		context = {'post': post, 'user_profile': user_profile}
	return HttpResponse(template.render(context, request))

def index(request, category='All'):
	md = markdown.Markdown(extensions=['markdown.extensions.fenced_code', 'markdown.extensions.tables', 'extra'])
	if category == 'All':
		posts = Post.objects.filter(status=1)
	else:
		posts = Post.objects.filter(status=1, category__categories__contains=category)
	categories = PostCategory.objects.all()
	for post in posts:
		post.content_short = BeautifulSoup(md.convert(bleach.clean(post.content)), features="html.parser").find('p').text
	template = loader.get_template('blog/index.html')
	context = {'posts': posts, 'categories': categories, 'category': category}
	return HttpResponse(template.render(context, request))



