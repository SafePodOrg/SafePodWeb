from __future__ import unicode_literals
from django.core.urlresolvers import reverse

from django.db import models

# Model for Tags
# This models the many2many field Tag
# Each Tag can be associated with several Posts and each post can have several tags
class Tag(models.Model):
    # Name, optional description and a slug
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300, blank=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    # Order based on name
    class Meta:
        ordering = ["name"]

    def __unicode__(self):
        return self.name

    # Absolute URL made from the tag base url and the slug
    def get_absolute_url(self):
        return reverse('forum:tag', args=[unicode(self.slug)])

class AppUser(models.Model):
    
    id = models.CharField(max_length=50, primary_key=True)
    # If the user is banned for spamming
    banned = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.id

# Create a manager to override the default 'all' function to return only those models that are already published
class PostManager(models.Manager):
    def all(self):
        return super(PostManager,self).filter(published=True)

# Model for a Blog post
class Post(models.Model):
    
    # Meta information
    body = models.TextField()
    
    published = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)    
    
    likes = models.IntegerField(default=0)
    liked = models.ManyToManyField(AppUser, blank=True, related_name="post_liked_by")
    
    dislikes = models.IntegerField(default=0)
    disliked = models.ManyToManyField(AppUser, blank=True, related_name="post_disliked_by")
    
    tags = models.ManyToManyField(Tag, blank=True)
    
    app_user = models.ForeignKey(AppUser)
        
    objects = PostManager()
    
    # Helper functions
    class Meta:
        ordering = ["-created"]

    def get_absolute_url(self):
        return reverse('forum:post',args=[str(self.slug)])
    
    def __unicode__(self):
        return self.body[:25]
    
# Create a manager to override the default 'all' function to return only those models that are already published
class CommentManager(models.Manager):
    def all(self):
        return super(CommentManager,self).filter(published=True)
    
# Model for a Comment
class Comment(models.Model):
    
    # Meta information
    body = models.TextField()
    
    published = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)    
    
    likes = models.IntegerField(default=0)
    liked = models.ManyToManyField(AppUser, blank=True, related_name="comment_liked_by")
    
    dislikes = models.IntegerField(default=0)
    disliked = models.ManyToManyField(AppUser, blank=True, related_name="comment_disliked_by")
    
    app_user = models.ForeignKey(AppUser)
    
    post = models.ForeignKey(Post)
    
    objects = CommentManager()
     
    # Helper functions
    class Meta:
        ordering = ["-created"]

    def get_absolute_url(self):
        return reverse('forum:comment',args=[str(self.slug)])
    
    def __unicode__(self):
        return self.body[:25]