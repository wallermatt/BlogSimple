<h1>BlogSimple</h1>

Simple Blog application to play with Django-Nonrel and Google App Engine.

It's based round the framework at http://github.com/GoogleCloudPlatform/appengine-django-skeleton (example at https://developers.google.com/appengine/#getstarted-framework-django). It sits in the appengine-django-skeleton directory.

settings.py was modified to add 'blogsimple' to INSTALLED_APPS and 'django.middleware.csrf.CsrfViewMiddleware' to MIDDLEWARE_CLASSES.

<h3>/blogsimple</h3>
BlogSimple main page. Displays all blogs in date created order, newest first, each page holding 5 entries. Blog title links to individual blog disply. 

<h3>/blogsimple/<blog_id>/</h>
Individual blog display. If user is logged in, buttons linking to Edit and Delete will be displayed.

<h3>/blogsimple/create</h3>
Form for creating a blog entry. If user is not logged in they are redirected to login page, and returned once they have logged in successfully.

<h3>/blogsimple/<blog_id>/edit/</h3>
Form for editing an existing blog (called via the individual blog display screen). If user is not logged in they are redirected to login page, and returned once they have logged in successfully.

<h3>/blogsimple/<blog_id>/delete</h3>
If deleted selected, user is redirected to confirmation page. If they confirm, the blog is deleted and the user redirected to main page.

<h3>/blogsimple/login and /blogsimple/logout</h3>
Django user authorisation functionality is used. Users are created using admin. Once logged out successfully user is redirected to main page.


**Note:** 