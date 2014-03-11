<h1>BlogSimple</h1>

Simple Blog application to play with Django-Nonrel and Google App Engine.

It's based round the framework at http://github.com/GoogleCloudPlatform/appengine-django-skeleton (example at https://developers.google.com/appengine/#getstarted-framework-django). It sits in the appengine-django-skeleton directory.

settings.py was modified to add 'blogsimple' to INSTALLED_APPS and 'django.middleware.csrf.CsrfViewMiddleware' to MIDDLEWARE_CLASSES.

<h4>/blogsimple</h4>
BlogSimple main page. Displays all blogs in date created order, newest first, each page holding 5 entries. Blog title links to individual blog disply. 

<h4>/blogsimple/<blog_id>/</h4>
Individual blog display. If user is logged in, buttons linking to Edit and Delete will be displayed.

<h4>/blogsimple/create</h4>
Form for creating a blog entry. If user is not logged in they are redirected to login page, and returned once they have logged in successfully.

<h4>/blogsimple/<blog_id>/edit/</h4>
Form for editing an existing blog (called via the individual blog display screen). If user is not logged in they are redirected to login page, and returned once they have logged in successfully.

<h4>/blogsimple/<blog_id>/delete</h4>
If deleted selected, user is redirected to confirmation page. If they confirm, the blog is deleted and the user redirected to main page.

<h4>/blogsimple/login and /blogsimple/logout</h4>
Django user authorisation functionality is used. Users are created using admin. Once logged out successfully user is redirected to main page.

<h4>Note</h4>

Memcache used to hold all blog details. Three levels of keys:

'year_list': list of years blogs created on, e.g. 'year_list': [2013, 2014]

year: list of blogs created on that year, e.g. '2014': ['487657648', '459334565']

blog.id: actual blog object, e.g. '487657648': blog.object 

This approach assumes that each memcache entry won't go beyond 1mb limit. It also assumes that there won't be a number of users updating data on same blog concurrently.

If greater safety required, implement explicit size checking and cas/compare and set.

My next step is to experiment using .ndb with Django generic class based views. 