from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import Blog, BlogCategory, BlogSeries, Comment
from .forms import CommentForm, ContactForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import NewUserForm
from django.contrib.auth.models import User
import requests
import socket
from django.utils import timezone


def single_slug(request, single_slug):
    # first check to see if the url is in categories.
    categories = [c.category_slug for c in BlogCategory.objects.all()]
    if single_slug in categories:
        matching_series = BlogSeries.objects.filter(blog_category__category_slug=single_slug)
        series_urls = {}

        for m in matching_series.all():
            part_one = Blog.objects.filter(blog_series__blog_series=m.blog_series).earliest("blog_published")
            series_urls[m] = part_one.blog_slug

        return render(request=request,
                      template_name='main/category_detail.html',
                      context={"blog_series": matching_series, "part_ones": series_urls})

    blogs = [t.blog_slug for t in Blog.objects.all()]

    if single_slug in blogs:
        this_blog = Blog.objects.get(blog_slug=single_slug)
        blogs_from_series = Blog.objects.filter(blog_series__blog_series=this_blog.blog_series).order_by('blog_published')
        this_blog_idx = list(blogs_from_series).index(this_blog)

        comments = Comment.objects.filter(post=this_blog)#Comment.objects.all()
        new_comment = None
        # Comment posted
        if request.method == 'POST':
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                # Create Comment object but don't save to database yet
                new_comment = comment_form.save(commit=False)
                # Assign the current post to the comment
                new_comment.name = request.user.username
                new_comment.email = request.user.email
                new_comment.post = this_blog
                # Save the comment to the database
                new_comment.save()        
                messages.info(request,"Comment submitted successfully")
                return HttpResponseRedirect("/"+single_slug+"/")

        else:
            comment_form = CommentForm()

        return render(request=request,
                      template_name='main/blog_detail.html',
                      context={"blog":this_blog,
                               "sidebar": blogs_from_series,
                               "this_tut_idx": this_blog_idx,
                               "comments": comments,
                               "new_comment": new_comment,
                               "comment_form": comment_form})

    pages_check = ['login', 'register','admin','blog','cv','account','contact']
    if single_slug in pages_check:
        return redirect(f"main:{single_slug}")
    elif single_slug == "logout":
        logout_request(request)
        return redirect("main:homepage")
    else:
        return HttpResponse("PAGE NOT FOUND")






def homepage(request):
    truncate_to = 5
    blogs_list = (Blog.objects.order_by('-blog_published'))[:truncate_to]

    return render(request=request,
                  template_name='main/home.html',
                  context={"blogs": blogs_list})
def blog(request):
    return render(request=request,
                  template_name='main/categories.html',
                  context={"categories": BlogCategory.objects.all,
                           "posts": Blog.objects.order_by('-blog_published')})

def cv(request):
    return render(request=request,
                  template_name='main/portfolio.html')
def contact(request):
    name=''
    email=''
    comment=''

    form= ContactForm(request.POST or None)
    

    if request.user.is_authenticated:
        subject= str(request.user)
    else:
        subject= "Visitor"
    if request.method == 'POST':
        comment= "Message sent as "+subject
        messages.info(request,comment)
        return HttpResponseRedirect("/contact/")
    
    context= {'form': form}
    return render(request, 'main/contact.html', context)

    
    

def register(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, f"New Account Created: {username}")
			login(request, user)
			messages.info(request, f"You are now logged in as {username}")
			return redirect("main:homepage")
		else:
			for msg in form.error_messages:
				messages.error(request, f"{msg}: {form.error_messages[msg]}")
 

	form = NewUserForm
	return render(request,
				  "main/register.html",
				  context={"form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "Logged out successfully!")
	return redirect("main:homepage")


def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}")
				return redirect("main:homepage")
			else:
				messages.error(request, "Invalid username or password")

		else:
			messages.error(request, "Invalid username or password")

	form = AuthenticationForm()
	return render(request,
				  "main/login.html",
				  {"form":form})
