from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import HomeView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('all_news/', views.all_news, name='all_news'),
    path('home/', HomeView.as_view(), name='home'),
    path('singlearticle/<slug:slug>', views.singlearticle, name='singlearticle'),
    path('category/<int:id>', views.category, name='category'),
    path('all_category/', views.all_category, name='all_category'),

    path('logout_user/', views.logout_user, name='logout_user'),
    path('user_register/', views.user_register, name='user_register'),
    path('user_login/', views.user_login, name='user_login'),

    
    path('viewsarticle/', views.viewsarticle, name='viewsarticle'),
    path('savearticle/<int:id>', views.savearticle, name='savearticle'),
    path('removearticle/<int:id>/', views.remove_saved_article, name='removearticle'),
    path('search/', views.search, name='search'),
    path('react/', views.react_to_article, name='react_to_article'),
    path('react_comment/', views.react_to_comment, name='react_to_comment'),
    path('about/', views.about, name='about'),
    path('contactme/', views.contactme, name='contactme'),
    path('test/', views.test, name='test'),

    
]