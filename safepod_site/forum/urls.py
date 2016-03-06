from django.conf.urls import patterns, url

from .views import PostListView, SearchView, AllTagsView, TaggedPostListView, MyPostListView, forum_post, PostDetailView, forum_comment, CommentDetailView
 
urlpatterns = [
                       url(r'^$', PostListView.as_view(), name='posts_index'),
                       # if its a search
                       url(r'^search', SearchView.as_view(), name='search'),
                       # Tag views with home page and detailed views
                       url(r'^tag/?$', AllTagsView.as_view(), name='all_tags'),
                       url(r'^tag/(?P<slug>[a-zA-Z0-9-]+)/?$', TaggedPostListView.as_view(), name='tagged_posts'),
                       # url to handle new post
                       url(r'^post/new/?$', forum_post, name='new_post'),
                       url(r'^post/my/?$', MyPostListView.as_view(), name='my_post'),
                       # detailed view of a particular post
                       url(r'^post/(?P<pk>[0-9]+)/?$', PostDetailView.as_view(), name='post_detail'),
                       
                       # url to handle new comment
                       url(r'^comment/new/?$', forum_comment, name='new_comment'),
                       url(r'^comment/(?P<pk>[0-9]+)/?$', CommentDetailView.as_view(), name='comment_detail'),
                       
            ]