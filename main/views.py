from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Blog, BlogCategory, BlogSeries
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import NewUserForm


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

        return render(request=request,
                      template_name='main/blog_detail.html',
                      context={"blog":this_blog,
                               "sidebar": blogs_from_series,
                               "this_tut_idx": this_blog_idx})

    #return HttpResponse(f"'{single_slug}' does not correspond to anything we know of!")
    if single_slug == "admin":
    	return redirect('/admin/')
    else:
    	return HttpResponse("PAGE NOT FOUND")


def homepage(request):
    return render(request=request,
                  template_name='main/categories.html',
                  context={"categories": BlogCategory.objects.all})

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
