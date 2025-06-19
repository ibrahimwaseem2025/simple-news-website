from django.shortcuts import render , get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib import auth
from datetime import datetime
from freespeech.models import *
x=datetime.now()
y=x.strftime('%Y-%m-%d')

def home(request):
    return render(request, 'home.html')


def news(request):
    return render(request, 'news.html')



# Create your views here.
