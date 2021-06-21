from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.shortcuts import redirect
from .models import Post, UserProfile, PostImage, PostCategory


class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    readonly_fields = ('avatar_preview',)

    def avatar_preview(self, obj):
    	return obj.avatar_preview

class UserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)

class PostImageAdmin(admin.StackedInline):
	model = PostImage
	readonly_fields = ('image_preview',)

	def image_preview(self, obj):
		return obj.image_preview

	image_preview.short_description = 'Title Image Preview'
	image_preview.allow_tags = True

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	readonly_fields = ('title_image_preview',)
	inlines = [PostImageAdmin]
	save_on_top = True

	class Meta:
		model = Post

	def title_image_preview(self, obj):
		return obj.title_image_preview

	def response_change(self, request, obj):
		return redirect(f'/post/{obj.slug}')

	title_image_preview.short_description = 'Title Image Preview'
	title_image_preview.allow_tags = True

@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    pass

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(PostCategory)

