from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
from blogsimple.models import Blog
from blogsimple.views import BlogListView, BlogSingleView, BlogCreateView, BlogEditView, BlogDeleteView, LoginView, LogoutView


urlpatterns = patterns('blogsimple.views',
    url(r'^$', BlogListView.as_view(), name='index'),
    url(r'^create$', BlogCreateView.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/blog/$', BlogSingleView.as_view(), name='blog'),
    url(r'^(?P<pk>\d+)/edit/$', BlogEditView.as_view(), name='edit'),
    url(r'^(?P<pk>\d+)/delete/$', BlogDeleteView.as_view(), name='delete'),
    url(r'^login$', LoginView.as_view(), name='login'),
    url(r'^logout$', LogoutView.as_view(), name='logout'),
    url(r'^cache$', 'cache')
)
