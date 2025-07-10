from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from embed_video.fields import EmbedVideoField
from django.urls import reverse
import datetime
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field





# category model
class Category(models.Model):
    title=models.CharField(max_length=200)
    category_image=models.ImageField(upload_to='img/')

    class Meta:
        verbose_name_plural ='Categories'

    def __str__(self):
        """Return the title of the category."""
        return self.title

class News(models.Model):
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    title=models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=300)
    image=models.ImageField(upload_to='img/', null=True, blank=True, default='img/noimage.png' )
    video = EmbedVideoField(blank=True, null=True, default=None)
    voice_file = models.FileField(upload_to='voice/', null=True, blank=True, default=None)
    image_description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True, default=None)
    detail=models.TextField()
    detail_rich_ckeditor =  CKEditor5Field('Content', config_name='rich', blank=True, null=True, default=None)
    key = models.TextField(max_length=100, blank=True, null=True, default=None)
    add_time=models.DateTimeField(auto_now_add=True)
    release_date = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    podcast=models.BooleanField(default=False)
    voice=models.BooleanField(default=False)
    opinion=models.BooleanField(default=False)
    featured=models.BooleanField(default=False)
    top_news=models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_articles', blank=True, default=None)

    def __str__(self):
        return self.title
    
    
    def upcomingg(self):
        if not self.release_date:
            return False
        now = timezone.now()
        release_date = self.release_date
        # Ensure both datetimes are timezone-aware
        if timezone.is_naive(release_date):
            release_date = timezone.make_aware(release_date, timezone.get_current_timezone())
        return release_date > now


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("singlearticle", kwargs={"slug": self.slug})
    
    def number_of_likes(self):
        return self.likes.count()

    class Meta:
        verbose_name_plural ='News'    
    
    def hours_ago(self):
        """Calculate the number of hours since the article was added."""
        now = timezone.now()
        diff = now - self.add_time
        hours = int(diff.total_seconds() / 3600)
        if hours >= 8760:
            years = int(hours // 8760)
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif hours >= 720:
            month = int(hours // 720)
            return f"{month} month{'s' if month > 1 else ''} ago"
        elif hours >= 168:
            weeks = int(hours // 168)
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif hours >= 24:
            days = int(hours // 24)
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif hours == 0:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    



# comments Model
class Reaction(models.Model):
    REACTION_CHOICES = [
        ('haha', 'Haha'),
        ('happy', 'Happy'),
        ('angry', 'Angry'),
        ('sad', 'Sad'),
    ]
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    article = models.ForeignKey(News, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'article'), ('session_key', 'article'))  

class Comment(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=200)
    comment = models.TextField()
    add_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.comment

class Commentreaction(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    type = models.CharField(max_length=10, choices= [
        ('like', 'like'),
        ('dislike', 'dislike'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'comment'), ('session_key', 'comment'))

# Create your models here.
