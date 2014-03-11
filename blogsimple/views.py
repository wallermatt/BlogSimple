from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, UpdateView, CreateView, DeleteView, FormView, View
from models import Blog
from forms import BlogForm, BlogAuthenticationForm

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters

from utilities import ContextMixin, AuthMixin, BlogFormMixin
from utilities import select_blog, add_blog_to_memcache, delete_blog_from_cache, refill_memcache, select_all_blogs, cache_compare_and_reload

import logging

class BlogListView(ContextMixin, ListView):
    context_object_name='blog_list'
    template_name='blogsimple/index.html'
    paginate_by='5'

    def get_queryset(self):
        return select_all_blogs()


class BlogSingleView(ContextMixin, DetailView):
    context_object_name='blog'
    template_name='blogsimple/blog.html'

    def get_object(self):
        return select_blog(self.kwargs['pk']) 


class BlogCreateView(ContextMixin, AuthMixin, BlogFormMixin, CreateView):
    pass


class BlogEditView(ContextMixin, AuthMixin, BlogFormMixin, UpdateView):

    def get_object(self):
        return select_blog(self.kwargs['pk'])


class BlogDeleteView(ContextMixin, AuthMixin, DeleteView):
    template_name='blogsimple/delete.html'

    def get_object(self):
        return select_blog(self.kwargs['pk'])

    def get_success_url(self):
        delete_blog_from_cache(str(self.kwargs['pk']))
        return reverse_lazy('blogsimple:index')

"""
Test cookie needed for Django login.
If redirected from page that requires a login, NEXT is used to redirect back if login successful
"""
class LoginView(ContextMixin, FormView):
    template_name='blogsimple/generic_form.html'
    form_class=BlogAuthenticationForm
    success_url = '/blogsimple/'

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        if 'next' in self.request.GET:
            self.success_url=self.request.GET['next']
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    @method_decorator(sensitive_post_parameters('password'))
    def dispatch(self, request, *args, **kwargs):
        request.session.set_test_cookie()
        return super(LoginView, self).dispatch(request, *args, **kwargs)


class LogoutView(View):
    
    def get(self, request, *args, **kwargs):
        redirect_to = 'blogsimple:index'
        auth_logout(request)
        return HttpResponseRedirect(reverse(redirect_to))


"""
'Undocumented' feature to compare cache to db and reload if neccesary
"""
def cache(request):
    return cache_compare_and_reload(request)

