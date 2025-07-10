from django.shortcuts import render , get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib import auth
from datetime import datetime
from freespeech.models import *
from django.shortcuts import render,redirect
from django.contrib import messages
from .models import News,Category,Comment
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.db.models import Count
from django.http import JsonResponse
from django.template.loader import render_to_string
import bleach
from django.utils.safestring import mark_safe
from django.utils.html import linebreaks
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from collections import defaultdict
from .recommender import get_recommendations
from django.core.paginator import Paginator
from django.contrib.auth import logout, login, authenticate
from .form import CustomUserCreationForm, CustomAuthenticationForm

# Allowed HTML tags and attributes
allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
allowed_attrs = {}  # No inline styles or JS


class HomeView(ListView):
    model = News
    template_name = 'home.html'
    context_object_name = 'news_list'
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['three_categories'] = Category.objects.all()
        context['podcasts'] = News.objects.filter(podcast=True).order_by('-id')
        context['voice'] = News.objects.filter(voice=True).order_by('-id')
        context['first_news'] = News.objects.filter(voice=False).order_by('-id').first()
        context['three_news'] = News.objects.filter(voice=False).filter(top_news=True).order_by('-id')[0:5]
        context['forth_news'] = News.objects.filter(voice=False).filter(top_news=True).order_by('-id')[5:9]
        context['popnews'] = News.objects.order_by('-views')[:10]
        context['opinion'] = News.objects.filter(opinion=True).order_by('-id')
        context['upcoming'] = News.objects.filter(release_date__gt=timezone.now()).order_by('-id')
        

        R_news = News.objects.order_by('-id')[:10]
        if R_news:
            context['recommend_blogs'] = get_recommendations(R_news[0].slug)  # Get recommendations based on the first article
        else:
            context['recommend_blogs'] = []
        return context

def search(request):
    count = 0
    x = 0
    if request.method == 'POST':
        search = request.POST['search']
        if search:
            news = News.objects.filter(title__icontains = search).order_by('-id')  # You can filter here
            paginator = Paginator(news, 9)  # Show 6 articles per page

            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)  # Handles invalid pages too

        else:
            news = News.objects.all( ).order_by('-id')
            paginator = Paginator(news, 9)  # Show 6 articles per page

            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
    else:
        search = ''
        news = News.objects.all().order_by('-id')

    count = news.count()
    return render(request, 'search.html', {
        'news': news,
        'search': search,
        'count': count,
        'x': x,
        'page_obj': page_obj,
    })

def all_news(request):
    three_categories=Category.objects.all()
    all_news=News.objects.order_by('-id')
    paginator = Paginator(all_news, 24)  # Show 24 articles per page
    page_number = request.GET.get('page')
    page_obje = paginator.get_page(page_number)
    return render(request, 'all_news.html',{
        'all_news':all_news,
        'three_categories':three_categories,
        'page_obje': page_obje,
    })

def all_category(request):
    three_categories=Category.objects.all()
    cats=Category.objects.all()
    return render(request,'all_category.html',{
        'cats':cats,
        'three_categories':three_categories,
    })

def savearticle(request, id): 
    article = get_object_or_404(News, pk=id)

    savearticle = request.session.get('savearticle', {})

    if str(id) not in savearticle:
        savearticle[str(id)] = {'quantity': 1}

    request.session['savearticle'] = savearticle
    messages.success(request, 'Article saved successfully!')
    return redirect('/')

def viewsarticle(request):
    three_categories=Category.objects.all()
    news = News.objects.all()
    savearticle = request.session.get('savearticle', {})
    saved_articles = []
    paginator = Paginator(saved_articles, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total = 0

    for id_str, data in savearticle.items():
        try:
            article = News.objects.get(pk=int(id_str))
            quantity = data['quantity']
            saved_articles.append({'article': article, 'quantity': quantity})
            total += quantity
        except News.DoesNotExist:
            continue

    return render(request, 'savearticles.html', {'saved_articles': saved_articles, 'total': total, 'news': news, 'three_categories':three_categories, 'page_obj': page_obj})

def remove_saved_article(request, id):
    savearticle = request.session.get('savearticle', {})

    if str(id) in savearticle:
        del savearticle[str(id)]
        request.session['savearticle'] = savearticle
        messages.success(request, 'Article removed successfully!')

    return redirect('viewsarticle')

def singlearticle(request, slug):
    news = get_object_or_404(News, slug=slug)
    news.views += 1
    news.save(update_fields=['views'])
    # Increment the view count for the article
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'a']
    allowed_attrs = {
        'a': ['href', 'title'],  # Allow basic links
    }
    cleaned_detail = bleach.clean(news.detail, tags=allowed_tags, attributes=allowed_attrs)
    formatted_detail = linebreaks(cleaned_detail)
    news.detail = mark_safe(formatted_detail)  # Mark as safe for rendering in template
    search_query = SearchQuery(news.title)
    user = request.user
    show_all = request.GET.get('show_all', 'false') == 'true' #responsible to communicate with url and convert to boolean value: True and False. by default this is set to false so that only 3 comments are shown at first. this works like logic gate. where if false meet with true it will be false. else true.
    if request.method=='POST':
        if request.user.is_authenticated:
            comment=request.POST['message'] 
            Comment.objects.get_or_create(
                news=news,
                name=user.username,
                email=user.email,
                comment=comment
            )
            messages.success(request,'comment submitted but in moderation mode.')
        else:
            name=request.POST['name']
            email=request.POST['email']
            comment=request.POST['message'] 
            Comment.objects.create(
                news=news,
                name=name,
                email=email,
                comment=comment
            )
            messages.success(request,'comment submitted but in moderation mode.')
    if show_all:
        comments = Comment.objects.filter(news=news, status=False).order_by('-id')
        #cancel limit for comments if show all is true
    else:
        comments = Comment.objects.filter(news=news, status=False).order_by('-id')[:3]  #show only 3 comments by default
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('comment.html', {'comments': comments})
        return JsonResponse({'html': html})
    #This means if a JavaScript fetch() request is sent (with X-Requested-With: XMLHttpRequest), we only return the comments section's HTML as JSON — perfect for dynamic updates.
    
    category=Category.objects.get(id=news.category.id)
    rel_news=News.objects.filter(category=category).exclude(slug=slug).order_by('-id')
    location=News.objects.filter(location=news.location).exclude(slug=slug).order_by('-id')
    reaction_counts_query = Reaction.objects.filter(article=news).values('type').annotate(count=Count('id'))


    comment_reaction_counts = {}

    for comment in comments:
        reactions = Commentreaction.objects.filter(comment=comment).values('type').annotate(count=Count('id'))
        counts = {'like': 0, 'dislike': 0}
        for r in reactions:
            counts[r['type']] = r['count']
        comment_reaction_counts[comment.id] = counts

    reaction_counts = {
        'happy': 0,
        'haha': 0,
        'sad': 0,
        'angry': 0
    }

    for reaction in reaction_counts_query:
        reaction_counts[reaction['type']] = reaction['count']



    
    three_categories=Category.objects.all()
    similar = News.objects.annotate(search=SearchVector('title')).filter(search=search_query).exclude(slug=slug).order_by('-id')
    if not similar.exists():
        similar = News.objects.filter(category=news.category).exclude(slug=slug).order_by('-id')[:5]
    
    connect_news = News.objects.annotate(search=SearchVector('key')).filter(search=search_query).exclude(slug=slug).order_by('-id')
    if not connect_news.exists():
        connect_news = News.objects.filter(category=news.category).exclude(slug=slug).order_by('-id')[:5]

    recommend_blogs = get_recommendations(slug)  # Get recommendations based on the current article

    
    return render(request, 'singlearticle.html',{
        'news':news,
        'related_news':rel_news,
        'comments':comments,
        'hours_ago': news.hours_ago(),
        'reaction_counts': reaction_counts,
        'show_all': show_all,
        'three_categories':three_categories,
        'location':location,
        'similar':similar,
        'comment_reaction_counts': comment_reaction_counts,
        'connect_news': connect_news,
        'recommend_blogs': recommend_blogs,
    })

@csrf_exempt
def react_to_article(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            news_id = data.get('news_id')
            type = data.get('reaction')

            article = News.objects.get(id=news_id)

            if not request.session.session_key:
                request.session.create()  # make sure session exists

            if request.user.is_authenticated:
                reaction, created = Reaction.objects.update_or_create(
                    user=request.user,
                    article=article,
                    defaults={'type': type, 'session_key': None}
                )
            else:
                reaction, created = Reaction.objects.update_or_create(
                    session_key=request.session.session_key,
                    article=article,
                    defaults={'type': type, 'user': None}
                )

            return JsonResponse({'success': True})
        except News.DoesNotExist:
            return JsonResponse({'error': 'Article not found'}, status=404)
        except Exception as e:
            print(f"Error processing reaction: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def react_to_comment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            comment_id = data.get('comment_id')
            if comment_id:
                print(comment_id)
            else:
                print("Comment ID not found in request data.")
            type = data.get('reaction')
            if type:
                print(type)
            else:
                print("Reaction type not found in request data.")

            comment = Comment.objects.get(id=comment_id)
            if not comment:
                print("Comment not found.")
                return JsonResponse({'error': 'Comment not found'}, status=404)
            else:
                print("Comment found.")

            if not request.session.session_key:
                request.session.create()  # make sure session exists

            if request.user.is_authenticated:
                reaction, created = Commentreaction.objects.update_or_create(
                    user=request.user,
                    comment=comment,
                    defaults={'type': type, 'session_key': None}
                )
            else:
                reaction, created = Commentreaction.objects.update_or_create(
                    session_key=request.session.session_key,
                    comment=comment,
                    defaults={'type': type, 'user': None}
                )
            print("Reaction processed successfully.")
            print(reaction)
            print(created)
            return JsonResponse({'success': True})

        except News.DoesNotExist:
            return JsonResponse({'error': 'comment not found'}, status=404)
        except Exception as e:
            print(f"Error processing reaction: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def category(request,id):
    category=Category.objects.get(pk=id)
    three_categories=Category.objects.all()
    news=News.objects.filter(category=category).order_by('-id')
    all_news=News.objects.order_by('-id')[0:20]
    return render(request, 'category.html',{
        'news':news,
        'category':category,
        'all_news':all_news,
        'three_categories':three_categories,
    })



def about(request):
    three_categories=Category.objects.all()
    return render(request, 'about.html', {
        'three_categories':three_categories,
    })

def contactme(request):
    three_categories=Category.objects.all()
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']

        if not name or not email or not subject or not message:
            messages.error(request, 'Please fill in all fields.')
            return redirect('contactss')

        # Here you can handle the contact form submission, e.g., send an email or save to the database
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contactme')

    return render(request, 'contactme.html', {
        'three_categories':three_categories,
    })


''''This is for testing html elements'''



def test(request):
    articles = News.objects.all().order_by('-id')  # You can filter here
    paginator = Paginator(articles, 9)  # Show 6 articles per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  # Handles invalid pages too

    return render(request, 'test.html', {'page_obj': page_obj})
# Create your views here.


# user login view

def user_login(request):  # Changed from 'login' to 'user_login'
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
        # Use the built-in auth.authenticate method to verify credentials
            user = form.get_user()
            login(request, user)  # Use auth.login to call the built-in login function
            return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {
        'form': form
    })


def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {
        'form': form,
    })

def logout_user(request):
    auth.logout(request)
    return redirect('user_login')