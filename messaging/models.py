from django.db import models

from realtimechatserver import helper


class MessageThread(models.Model):
    """Thread for messages

     - Users join a chatroom when added to clients
     - last_message contains ForeignKey to last message sent
    """
    hash_id = models.CharField(max_length=32,default=helper.create_hash,unique=True)
    title = models.CharField(max_length=64)
    psk = models.CharField(max_length=32, default="lol")
    admin = models.CharField(max_length=32, default="admin")
    friend1 = models.CharField(max_length=32, default="friend1")
    is_direct = models.BooleanField(default=False)
    clients = models.ManyToManyField('userauth.User',blank=True)
    last_message = models.ForeignKey('messaging.Message', null=True,blank=True,on_delete=models.SET_NULL)

    
    def mark_read(self, user):
        """Marks all messages read for a particular user"""
        UnreadReceipt.objects.filter(recipient=user,thread=self).delete()

    def add_message_text(self, text, sender):
        """Adds a message sent by sender
         - User sends text to the chat
         - creates new message with foreign key to self
         - adds unread receipt for each user
         - returns instance of new message
        """
        new_message = Message(text=text,sender=sender,thread=self)
        new_message.save()
        self.last_message = new_message
        self.save()
        for c in self.clients.exclude(id=sender.id):
            UnreadReceipt.objects.create(recipient=c,thread=self,message=new_message)
        return new_message


class Message(models.Model):
    """Threas Message

     - An unread receipt is created for each recipent in the related thread
    """
    hash_id = models.CharField(max_length=32,default=helper.create_hash,unique=True)
    date = models.IntegerField(default=helper.time_stamp)
    text = models.CharField(max_length=1024)
    thread = models.ForeignKey('messaging.MessageThread',on_delete=models.CASCADE,related_name='messages')
    sender = models.ForeignKey('userauth.User',on_delete=models.SET_NULL,null=True)

class UnreadReceipt(models.Model):
    """Unread receipt for nread messages

     - Created for each recipient in a group chat when a message is sent
     - Deleted when a user loads related thread or when they respond with the 'read' flag over websocket connection
    """
    date = models.IntegerField(default=helper.time_stamp)
    message = models.ForeignKey('messaging.Message', on_delete=models.CASCADE,related_name='receipts')
    thread = models.ForeignKey('messaging.MessageThread',on_delete=models.CASCADE,related_name='receipts')
    recipient = models.ForeignKey('userauth.User',on_delete=models.CASCADE,related_name='receipts')

