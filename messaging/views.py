# messaging/views.py

from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from . import models
from . import serializers
from userauth import models as userauth_models

@login_required
def load_inbox(request):
    """Load user inbox threads

     - Retrieve all of the threads that includes the user in the clients filed.
     - count number of unread messages using related ame receipts cpntaining user
     - returns {"threads":[thread]}
    """
    threads = models.MessageThread.objects.filter(clients=request.user).annotate(
        unread_count=Count('receipts',filter=Q(receipts__recipient=request.user))
    )
    thread_data = serializers.MessageThreadListSerializer(threads).data
    #user = userauth_models.User.objects.filter(username=request.user.username)
    #print(user.username)
    #print(get_channel_layer())
    #print(request.session['channel_name'])
    return JsonResponse({'threads':thread_data})

@login_required
def load_messages(request):
    """Load messages from thread

     - Load 30 messages by default
     - the 'before' parameter will load the last 30 messages relative to the date
     - returns json {messages:[message], end:bool}
    """
    thread = models.MessageThread.objects.get(hash_id=request.GET['id'])
    
    # check if user is a part of this chat
    if not request.user in thread.clients.all():
        return HttpResponse(status=403)

    # query for messages filter
    q = [Q(thread=thread)]
    if 'before' in request.GET:
        q.append(Q(date__lt=int(request.GET['before'])))

    # query messages matching filter
    messages = models.Message.objects.filter(*q).order_by('-id')
    messages_data = serializers.MessageListSerializer(messages[:30]).data

    # mark any unread messages in chat as read
    thread.mark_read(request.user)
    return JsonResponse({"messages":messages_data,"end":messages.count() <= 30})

@login_required
@csrf_exempt
def add_chatroom(request):
    """Add user to chatroom

     - create thread if existing one with title does not exist
     - user is added to the chat as well as the channel_layer group using the channel_name
       specified in the session
    """
    title = request.POST['title'].strip()
    psk = request.POST['psk']
    
    # If thread already exists
    if models.MessageThread.objects.filter(title=title).exists():
        thread = models.MessageThread.objects.get(title=title)
        if thread.psk != psk:
            # Invalid passkey
            thread = None
            return HttpResponse(status=403)
    # If the thread does not exist yet
    else:
        return HttpResponse(status=405)

    if not request.user in thread.clients.all():
        thread.clients.add(request.user)
        channel_layer = get_channel_layer()

        if 'channel_name' in request.session:
            async_to_sync(channel_layer.group_add)(thread.hash_id,request.session['channel_name'])

    return HttpResponse(status=200)

@login_required
@csrf_exempt
def create_chatroom(request):
    title = request.POST['title'].strip()
    psk = request.POST['psk']
    
    if models.MessageThread.objects.filter(title=title).exists():
        return HttpResponse(status=403)
    else:
        thread = models.MessageThread(title=title, psk=psk)
        thread.save()

    if not request.user in thread.clients.all():
        thread.clients.add(request.user)
        channel_layer = get_channel_layer()
        if 'channel_name' in request.session:
            async_to_sync(channel_layer.group_add)(thread.hash_id,request.session['channel_name'])

    return HttpResponse(status=200)

    
@login_required
@csrf_exempt
def add_direct(request):
    """Create a direct message with another user
     
     - search for friend 
     - create a thread for the direct message
     - add user and friend to direct message
    """
    friend = request.POST['friend'].strip()

    if userauth_models.User.objects.filter(username=friend).exists():
        friendUser = userauth_models.User.objects.get(username=friend)
    elif userauth_models.User.objects.filter(phone_number=friend):
        friendUser = userauth_models.User.objects.get(phone_number=friend)
    elif userauth_models.User.objects.filter(email=friend):
        friendUser = userauth_models.User.objects.get(email=friend)
    else:
        return HttpResponse(status=403) #no friend :(

    threadName =  request.user.username + friendUser.username

    if models.MessageThread.objects.filter(title=threadName).exists():
        thread = models.MessageThread.objects.get(title=threadName)
    elif models.MessageThread.objects.filter(title=(friendUser.username + \
    request.user.username)).exists():
        thread = models.MessageThread.objects.get(title=(friendUser.username \
        + request.user.username))
    else:
        thread = models.MessageThread(title=threadName, psk=threadName, \
        admin=request.user.username, friend1 = friendUser.username, is_direct=True)
        #thread = models.MessageThread(title=threadName, psk=threadName)
        thread.save()

    if not request.user in thread.clients.all():
        thread.clients.add(request.user)
        #thread.clients.add(friendUser)
        channel_layer = get_channel_layer()
        if 'channel_name' in request.session:
            async_to_sync(channel_layer.group_add)(thread.hash_id,request.session['channel_name'])
    
    #if not friendUser in thread.clients.all():
     #   thread.clients.add(friendUser)
      #  channel_layer = get_channel_layer()

       # if 'channel_name' in request.session:
        #    async_to_sync(channel_layer.group_add)(thread.hash_id,request.session['channel_name'])

    thread_data = serializers.MessageThreadSerializer(thread).data

    return HttpResponse(status=200)
