import json, hashlib, re

from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http.response import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.html import escape

from .models import Post, Tag, Comment, AppUser

# Process the input query string to make sure only legitimate words are used.
def process_query_string(query_string):
    """Query sanitizer"""
    stopwords = set([u'i', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves', u'you', u'your', u'yours', u'yourself', u'yourselves', u'he', u'him', u'his', u'himself', u'she', u'her', u'hers', u'herself', u'it', u'its', u'itself', u'they', u'them', u'their', u'theirs', u'themselves', u'what', u'which', u'who', u'whom', u'this', u'that', u'these', u'those', u'am', u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have', u'has', u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the', u'and', u'but', u'if', u'or', u'because', u'as', u'until', u'while', u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between', u'into', u'through', u'during', u'before', u'after', u'above', u'below', u'to', u'from', u'up', u'down', u'in', u'out', u'on', u'off', u'over', u'under', u'again', u'further', u'then', u'once', u'here', u'there', u'when', u'where', u'why', u'how', u'all', u'any', u'both', u'each', u'few', u'more', u'most', u'other', u'some', u'such', u'no', u'nor', u'not', u'only', u'own', u'same', u'so', u'than', u'too', u'very', u's', u't', u'can', u'will', u'just', u'don', u'should', u'now'])
    query_string = re.sub(r"[^a-zA-Z0-9\s]",'',query_string.strip())
    tokens = [word for word in query_string.split() if word.lower() not in stopwords]
    # Use only the first 10 words to avoid using long string searches
    return tokens[:10]

# This function converts a give post obj queryset into a standard json response object used by postlistview, searchview and tagview
def post_objs_to_json(queryset):
    
    results = []
    for item in queryset:
        result_obj = {}
        result_obj['body'] = escape(item.body)[:100]
        result_obj['tags'] = []
        for tag in item.tags.all():
            result_obj['tags'].append(tag.name)
        results.append(result_obj)
        
    return JsonResponse({ 
                            'results': results
                        })


class PostListView(generic.ListView):
    
    model = Post
    
    def render_to_response(self, context, **response_kwargs):  
        
        queryset = Post.objects.all()[:10]  
        return post_objs_to_json(queryset)
    
class SearchView(generic.ListView):

    def get_queryset(self):
        if self.request.GET.has_key('q'):
            query_string = self.request.GET.get('q')
            # Sanitize the query string
            tokens = process_query_string(query_string)
            
            # Initialize the results
            results = Post.objects.none()
            # For each token, find objects that have the token in either the title or the body and append it to the existing results
            for token in tokens:
                results = results | Post.objects.filter(Q(body__icontains=token)) 

            # In case its an empty search or that filled with stopwords, return all objects
            if len(tokens) < 1:
                results = Post.objects.all()            
            
            # Number of results must be less than the value at which it is paginated
            return results[:10]    
        else:
            return Post.objects.all()[:10]
    
    # Render the results
    def render_to_response(self, context, **response_kwargs):  
        
        queryset = self.get_queryset()   
        return post_objs_to_json(queryset)

class AllTagsView(generic.ListView):
    
    model = Tag
    
    def render_to_response(self, context, **response_kwargs):    
        queryset = Tag.objects.all()
        results = []
        for item in queryset:
            result_obj = {}
            result_obj['tag'] = item.name
            result_obj['slug'] = item.slug
            result_obj['description'] = item.description
            results.append(result_obj)
            
        return JsonResponse({ 
                                'results': results
                            }, status=200)        
        
class TaggedPostListView(generic.ListView):
    
    # Updated query set to only show posts with the given tag name
    def get_queryset(self):
        # Extract the Slug from the url
        slug = self.kwargs['slug']
        # Try to retrieve the tag and all the posts it is linked to
        try:
            tag = Tag.objects.get(slug=slug)
            return tag.post_set.all()
        # Raise a 404 if the tag does not exist
        except Tag.DoesNotExist:
            raise Http404   
    
    # Render the results
    def render_to_response(self, context, **response_kwargs):  
        queryset = self.get_queryset()   
        return post_objs_to_json(queryset)

@csrf_exempt
def forum_post(request):
    # If the request is a post, get the form contents and initialize an instance of the form object
    if request.method == "POST":
        post_obj = json.loads(request.body)
            
        try:
            new_post = Post()
            new_post.body = post_obj['body']
            new_post.app_user = AppUser.objects.get_or_create(id=post_obj['userid'])
            new_post.save() 
            for tag_name in post_obj['tags']:
                tag = Tag.objects.get(slug=tag_name)
                new_post.tags.add(tag)
            return JsonResponse({'success':True}, status=200)
        except:
            # Failed!
            return JsonResponse({'success':False}, status=200)
    else:
        return JsonResponse({'success':False, 'message': "Use POST request"}, status=200)


class PostDetailView(generic.DetailView):
    
    model = Post 
    
    def render_to_response(self, context, **response_kwargs):      
        postobj = self.get_object()
        
        results = {'body': postobj.body,
                   'created': postobj.created,
                   'likes': postobj.likes,
                   'dislikes':postobj.dislikes,   
                   'posted': False,  
                   'liked': False, 
                   'disliked': False,               
                   }

        if postobj.app_user.id==self.request.GET.get('userid',''):
            results['posted'] = True
        
        # If the user has liked the post, then notify
        if postobj.liked.filter(id=self.request.GET.get('userid','')).exists():
            results['liked'] = True
            
        # If the user has disliked the post, then notify
        if postobj.disliked.filter(id=self.request.GET.get('userid','')).exists():
            results['disliked'] = True
            
        # Get all the tags
        results['tags'] = []
        for tag in postobj.tags.all():
            results['tags'].append(tag.name)
        
        # Get all the comments
        results['comments'] = []
        for item in postobj.comment_set.all():
            result_obj = { 'body': item.body,
                           'created': item.created,
                           'likes': item.likes,
                           'dislikes':item.dislikes,   
                           'posted': False,  
                           'liked': False, 
                           'disliked': False,               
                           }
            if item.app_user.id==self.request.GET.get('userid',''):
                result_obj['posted'] = True
            
            # If the user has liked the post, then notify
            if item.liked.filter(id=self.request.GET.get('userid','')).exists():
                result_obj['liked'] = True
                
            # If the user has disliked the post, then notify
            if item.disliked.filter(id=self.request.GET.get('userid','')).exists():
                result_obj['disliked'] = True
            
            results['comments'].append(result_obj)
            
        return JsonResponse({ 
                                'results': results
                            }, status=200)        

   
    def post(self, request, *args, **kwargs):
        postobj = self.get_object()
        
        vote = json.loads(request.body)
        
        try:
            app_user = vote['userid']
            # Handle if post was liked
            if vote.has_key('liked'):
                # If the vote is true
                if vote['liked']:
                    # Two possibilies. a) This post was either already liked which means it will be ignored
                    if postobj.liked.filter(id=app_user).exists(): 
                        pass 
                    else: # otherwise, update the like and then check the dislike and remove it if it was disliked
                        postobj.liked.add(AppUser.objects.get(id=app_user))
                        postobj.likes+=1
                        # If it was disliked, then remove 
                        if postobj.disliked.filter(id=app_user).exists(): 
                            postobj.disliked.remove(AppUser.objects.get(id=app_user))
                            postobj.disliked-=1
                else:
                    # Else unlike the post if already liked
                    if postobj.liked.filter(id=app_user).exists(): 
                        postobj.liked.remove(AppUser.objects.get(id=app_user))
                        postobj.likes-=1 
                
                return JsonResponse({'success':True}, status=200) 
            
            # Handle if post was disliked
            if vote.has_key('disliked'):
                # If the vote is true
                if vote['disliked']:
                    # Two possibilies. a) This post was either already disliked which means it will be ignored
                    if postobj.disliked.filter(id=app_user).exists(): 
                        pass 
                    else: # otherwise, update the disliked and then check the like and remove it if it was liked
                        postobj.disliked.add(AppUser.objects.get(id=app_user))
                        postobj.dislikes+=1
                        # If it was liked, then remove 
                        if postobj.liked.filter(id=app_user).exists(): 
                            postobj.liked.remove(AppUser.objects.get(id=app_user))
                            postobj.liked-=1
                else:
                    # Else unlike the post if already liked
                    if postobj.disliked.filter(id=app_user).exists(): 
                        postobj.disliked.remove(AppUser.objects.get(id=app_user))
                        postobj.disliked-=1 
                
                return JsonResponse({'success':True}, status=200)
            
        except:
            # Do something based on the errors contained in e.message_dict.
            # Display them to a user, or handle them programmatically.
            return JsonResponse({'success':False})                                 
   
@csrf_exempt
def forum_comment(request):
    # If the request is a post, get the form contents and initialize an instance of the form object
    if request.method == "POST":
        comment_obj = json.loads(request.body)
            
        try:
            new_comment = Comment()
            new_comment.body = comment_obj['body']
            new_comment.app_user = AppUser.objects.get_or_create(id=comment_obj['userid'])
            new_comment.comment = Post.objects.get(comment_obj['post'])
            new_comment.save() 
            
            return JsonResponse({'success':True}, status=200)
        except:
            # Failed!
            return JsonResponse({'success':False}, status=200)
    else:
        return JsonResponse({'success':False, 'message': "Use POST request"}, status=200)

class CommentDetailView(generic.DetailView):
    
    model = Comment 
    
    def render_to_response(self, context, **response_kwargs):      
        commentobj = self.get_object()
        
        results = {'body': commentobj.body,
                   'created': commentobj.created,
                   'likes': commentobj.likes,
                   'dislikes':commentobj.dislikes,   
                   'posted': False,  
                   'liked': False, 
                   'disliked': False,               
                   }

        if commentobj.app_user.id==self.request.GET.get('userid',''):
            results['posted'] = True
        
        # If the user has liked the comment, then notify
        if commentobj.liked.filter(id=self.request.GET.get('userid','')).exists():
            results['liked'] = True
            
        # If the user has disliked the comment, then notify
        if commentobj.disliked.filter(id=self.request.GET.get('userid','')).exists():
            results['disliked'] = True
            
        return JsonResponse({ 
                                'results': results
                            }, status=200)        

   
    def post(self, request, *args, **kwargs):
        commentobj = self.get_object()
        
        vote = json.loads(request.body)
        
        try:
            app_user = vote['userid']
            # Handle if comment was liked
            if vote.has_key('liked'):
                # If the vote is true
                if vote['liked']:
                    # Two possibilies. a) This comment was either already liked which means it will be ignored
                    if commentobj.liked.filter(id=app_user).exists(): 
                        pass 
                    else: # otherwise, update the like and then check the dislike and remove it if it was disliked
                        commentobj.liked.add(AppUser.objects.get(id=app_user))
                        commentobj.likes+=1
                        # If it was disliked, then remove 
                        if commentobj.disliked.filter(id=app_user).exists(): 
                            commentobj.disliked.remove(AppUser.objects.get(id=app_user))
                            commentobj.disliked-=1
                else:
                    # Else unlike the comment if already liked
                    if commentobj.liked.filter(id=app_user).exists(): 
                        commentobj.liked.remove(AppUser.objects.get(id=app_user))
                        commentobj.likes-=1 
                
                return JsonResponse({'success':True}, status=200) 
            
            # Handle if comment was disliked
            if vote.has_key('disliked'):
                # If the vote is true
                if vote['disliked']:
                    # Two possibilies. a) This comment was either already disliked which means it will be ignored
                    if commentobj.disliked.filter(id=app_user).exists(): 
                        pass 
                    else: # otherwise, update the disliked and then check the like and remove it if it was liked
                        commentobj.disliked.add(AppUser.objects.get(id=app_user))
                        commentobj.dislikes+=1
                        # If it was liked, then remove 
                        if commentobj.liked.filter(id=app_user).exists(): 
                            commentobj.liked.remove(AppUser.objects.get(id=app_user))
                            commentobj.liked-=1
                else:
                    # Else unlike the comment if already liked
                    if commentobj.disliked.filter(id=app_user).exists(): 
                        commentobj.disliked.remove(AppUser.objects.get(id=app_user))
                        commentobj.disliked-=1 
                
                return JsonResponse({'success':True}, status=200)
            
        except:
            # Do something based on the errors contained in e.message_dict.
            # Display them to a user, or handle them programmatically.
            return JsonResponse({'success':False})   