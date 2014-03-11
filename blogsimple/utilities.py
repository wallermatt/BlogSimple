from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import DetailView, ListView, UpdateView, CreateView, DeleteView, FormView, View
from models import Blog
from google.appengine.api import memcache
import logging
from forms import BlogForm 
from datetime import datetime
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

LOGIN_URL = reverse_lazy('blogsimple:login') # overrides settings.py 


"""
Add non-model data to generic views - mostly copied from Django documentation
Just used to pass user's logged in status - included in every view
"""
class ContextMixin(object):
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ContextMixin, self).get_context_data(**kwargs)
        # Add in a extra stuff here
        context['logged_in']=self.request.user.is_authenticated()
        return context

"""
Edit and Create views require user to be logged in. This checks and if user not logged in, it redirects
to log_in screen
"""
class AuthMixin(object):

    @method_decorator(login_required(login_url=LOGIN_URL))
    def dispatch(self, request, *args, **kwargs):        
        return super(AuthMixin, self).dispatch(request, *args, **kwargs)


"""
Used in edit and create views
"""
class BlogFormMixin(object):
    context_object_name='blog'
    template_name='blogsimple/generic_form.html'
    form_class=BlogForm    

    def form_valid(self, form):
        title=form.cleaned_data['title']
        body=form.cleaned_data['body']
        if 'pk' in self.kwargs:
            blog=select_blog(self.kwargs['pk'])
            blog.edited=datetime.now()
            blog.title=title
            blog.body=body
        else:
            blog=Blog(title=title, body=body)
        blog.save()
        add_blog_to_memcache(blog)
        return HttpResponseRedirect(reverse('blogsimple:blog', args=(blog.id,)))



"""
All DB and memcache operations controlled by these functions. 
All lookups check memcache first, then db if blog.id not found
All create and edit update db and memcache
"""

"""
Select blog from memcache with blog.id
If blog doesn't exist, it's selected from db and added to memcache
"""
def select_blog(blog_id):
    # select from memcache
    blog = memcache.get(str(blog_id))
    # if not found in mc select from db
    if not blog:
        blog = Blog.objects.get(pk=blog_id)
        if blog:
            add_blog_to_memcache(blog)
    return blog


"""
Adds blog to memcache
blogs stored in memcache via 3 keys:
year_list: breaks blogs up by year they were created, e.g. 'year_list': [2013, 2014]
year: lists all blog.ids that were created in that year, e.g. '2014': ['487657648', '459334565']
blog.id: blog.id as string, e.g. '487657648': <blog.object>
If these entries don't exist then they are created, otherwise they're updated
"""
def add_blog_to_memcache(blog):
        memcache.set(str(blog.id), blog)
        year = str(blog.posted.year)
        year_list = memcache.get('year_list')
        if not year_list:
            year_list = [year]
        elif year not in year_list:
            year_list.append(year)
        memcache.set('year_list', year_list)
        id_list = memcache.get(str(year))
        if not id_list:
            id_list = [str(blog.id)]
        elif str(blog.id) not in id_list:
            id_list.append(str(blog.id))
        memcache.set(str(year), id_list)

"""
Delete blog from cache - by id, year, and year_list
"""
def delete_blog_from_cache(blog_id):
    blog=memcache.get(blog_id)
    year = str(blog.posted.year)
    memcache.delete(blog_id)
    blogs_for_year=memcache.get(year)
    if blog_id in blogs_for_year:
        blogs_for_year.remove(blog_id)
        if len(blogs_for_year) == 0:
            memcache.delete(year)
            year_list=memcache.get('year_list')
            year_list.remove(year)
            if len(year_list) == 0:
                memcache.delete('year_list')
            else:
                memcache.set('year_list', year_list)
        else:
            memcache.set(year, blogs_for_year)


"""
Clears memcache then loads all blogs from db and reloads them into memcache
Also used to select all blogs if memcache empty
"""
def refill_memcache(blog_list=Blog.objects.all().order_by('-posted'), return_blogs=False):
    memcache.flush_all()
    for blog in blog_list:
         add_blog_to_memcache(blog)
    if return_blogs:
        return list(blog_list)


"""
Selects all blogs for index/front page
Gets data from memcache unless memcache is empty, then it selects from db and refills memcache
"""        
def select_all_blogs():
    year_list = memcache.get('year_list')
    blog_list = []
    if year_list:
        for year in year_list:
            id_list = memcache.get(year)
            if id_list:
                for id in id_list:
                    blog = select_blog(id)
                    if blog:
                        blog_list.append(blog)
    if blog_list == []:
        blog_list = refill_memcache(return_blogs=True)
    else:
        blog_list.sort(key=lambda x: x.posted, reverse=True)  # sorts newest first
    return blog_list


"""
Fear based function - compares memcache with db then refills memcache 
"""
def cache_compare_and_reload(request):
    db_blogs = Blog.objects.all().order_by('id')
    mc_blogs = select_all_blogs()
    mc_blogs.sort(key=lambda x: x.id)
    mismatch_details = []
    db_counter = 0
    mc_counter = 0
    while db_counter < len(db_blogs):
        if mc_counter < len(mc_blogs):
            if db_blogs[db_counter].id == mc_blogs[mc_counter].id:
                if db_blogs[db_counter].edited !=  mc_blogs[mc_counter].edited:
                    mismatch_details.append((mc_blogs[mc_counter].id, 
                                         ('Edited mismatch db:%s Vs mc:%s' %(db_blogs[db_counter].edited, mc_blogs[mc_counter].edited))))
                db_counter += 1
                mc_counter += 1
            elif db_blogs[db_counter].id >  mc_blogs[mc_counter].id:
                mismatch_details.append((mc_blogs[mc_counter].id, 'Cache Orphan'))
                mc_counter += 1
            else:
                mismatch_details.append((db_blogs[db_counter].id, 'Not in Cache'))
                db_counter += 1
        else:
            mismatch_details.append((db_blogs[db_counter].id, 'Not in Cache'))
            db_counter += 1
    
    # check for orphan mc entries at end
    while mc_counter < len(mc_blogs):
        mismatch_details.append((mc_blogs[mc_counter].id, 'Cache Orphan'))
        mc_counter += 1

    if db_blogs:
        refill_memcache(db_blogs)
    return HttpResponse(mismatch_details)
