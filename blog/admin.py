import requests
from django.contrib import admin

# Register your models here.
from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_permission_codename
from django.urls import reverse
from django.utils.html import format_html

from typeidea.base_admin import BaseOwnerAdmin
from typeidea.custom_site import custom_site
from .adminforms import PostAdminForm
from .models import Post, Category, Tag


# 配置为内部的SSO地址
# PERMISSION_API = "http://permission.sso.com/has_perm?user={}&perm_code={}"


class PostInline(admin.TabularInline):
    fields = ('title', 'desc')
    extra = 1
    model = Post


@admin.register(Category, site=custom_site)
@admin.register(Category)
class CategoryAdmin(BaseOwnerAdmin):
    inlines = [PostInline, ]
    list_display = ('name', 'status', 'is_nav', 'created_time', 'owner', 'post_count')
    fields = ('name', 'status', 'is_nav')

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = '文章数量'


@admin.register(Tag, site=custom_site)
@admin.register(Tag)
class TagAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'created_time', 'owner')
    fields = ('name', 'status')


class CategoryOwnerFilter(admin.SimpleListFilter):
    """ 自定义过滤器 只展示当前用户分类"""
    title = '分类过滤器'
    parameter_name = 'owner_category'

    def lookups(self, request, model_admin):
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    def queryset(self, request, queryset):
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=category_id)
        return queryset


# 双注册 保证在 admin 和 super_admin的个性化定制
@admin.register(Post, site=custom_site)
@admin.register(Post)
class PostAdmin(BaseOwnerAdmin):
    # 在编辑摘要时变为多行的Textarea
    form = PostAdminForm
    list_display = [
        'title', 'category', 'status', 'created_time', 'owner', 'operator'
    ]
    list_display_links = []

    list_filter = [CategoryOwnerFilter, ]
    search_fields = ['title', 'category__name']

    actions_on_top = True
    actions_on_bottom = True

    # 编辑页面
    save_on_top = True
    # fields = (
    #     ('category', 'title'),
    #     'desc',
    #     'status',
    #     'content',
    #     'tag',
    # )

    fieldsets = (
        ('基础配置', {
            'description': '基础配置描述',
            'fields': (
                ('title', 'category', 'status',)
            )
        }),
        ('内容', {
            'fields': (
                'desc',
                'content',
            )
        }),
        ('额外信息', {
            'classes': ('collapse',),
            'fields': ('tag',),
        }
         )
    )

    #   调用接口权限，判断登录用户是否有权限做改动
    # def has_add_permission(self, request):
    #     opts = self.opts
    #     codename = get_permission_codename('add', opts)
    #     perm_code = "%s.%s" % (opts.app_label, codename)
    #     resp = requests.get(PERMISSION_API.format(request.user.username, perm_code))
    #
    #     if resp.status_code == 200:
    #         return True
    #     else:
    #         return False

    def operator(self, obj):
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('cus_admin:blog_post_change', args=(obj.id,))
        )

    operator.short_description = '操作'

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(PostAdmin, self).save_model(request, obj, form, change)

    # 主要实现了对应用户显示对应的文章
    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        return qs.filter(owner=request.user)

    # # 对页面进行部分装饰
    # class Media:
    #     css = {
    #         'all': ('https://github.com/bootcdn/BootCDN/tree/1.0.1/ajax/libs/bootstrap/4.0.0-beta.x/css/bootstrap.min.css',),
    #     }
    #     js =  (' https://github.com/bootcdn/BootCDN/tree/1.0.1/ajax/libs/bootstrap/4.0.0-beta.x/js/bootstrap.bundle.js',)


@admin.register(LogEntry, site=custom_site)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['object_repr', 'object_id', 'action_flag', 'user', 'change_message']
