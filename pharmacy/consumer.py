from django.core.mail import send_mail
from django.utils.timezone import now
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_user = self.scope['url_route']['kwargs']['username']
        self.user = self.scope['user']

        if self.user.is_authenticated:
            # Create a unique room for each user-to-user chat
            self.room_name = f'private_chat_{self.user.username}_{self.other_user}'
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        receiver = User.objects.get(username=self.other_user)

        # Save the message
        message_obj = PrivateMessage.objects.create(
            sender=self.user,
            receiver=receiver,
            message=message,
            is_read=False
        )

        # Check if the receiver is offline (not connected to WebSocket)
        is_online = await self.check_user_online(receiver.username)

        if not is_online:
            self.send_email_alert(receiver, message)

        # Send the message to the recipient
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
                'message_id': message_obj.id
            }
        )
        # Send a notification to the other user
        await self.send_notification(self.other_user, message)
    async def send_notification(self, username, message):
        # Find the channel layer
        channel_layer = get_channel_layer()

        # Send notification to the other user (broadcast)
        await channel_layer.group_send(
            f"user_notifications_{username}",
            {
                'type': 'user_notification',
                'message': f'New message from {self.user.username}: {message}',
            }
        )

    async def user_notification(self, event):
        # Send the notification to WebSocket
        await self.send(text_data=json.dumps({
            'notification': event['message']
        }))
    async def chat_message(self, event):
        message = event['message']
        user = event['user']

        # Send the message back to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user': user
        }))


    async def check_user_online(self, username):
        # Check if the user is connected to the WebSocket group
        online_users = await self.channel_layer.group_send(f"user_notifications_{username}")
        return len(online_users) > 0

    def send_email_alert(self, user, message):
        send_mail(
            subject=f'New message from {self.user.username}',
            message=f'You received a new message: "{message}"',
            from_email='your-email@example.com',
            recipient_list=[user.email]
        )



import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.user = self.scope['user']

        if self.user.is_authenticated:
            # Add user to group chat
            self.room_name = f'group_chat_{self.group_name}'
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Remove user from the group when they disconnect
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Save the message to the database
        message_obj = GroupMessage.objects.create(
            sender=self.user,
            group_name=self.group_name,
            message=message,
            is_read=False  # Mark as unread for the group
        )

        # Notify all group members
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
                'message_id': message_obj.id  # Include the message ID
            }
        )

        # Send notifications to all group members except the sender
        group_members = User.objects.filter(groups__name=self.group_name).exclude(username=self.user.username)
        for member in group_members:
            is_online = await self.check_user_online(member.username)

            if not is_online:
                self.send_email_alert(member, message)

            await self.send_notification(member.username, message)

    async def send_notification(self, username, message):
        # Broadcast notification to all group members
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"user_notifications_{username}",
            {
                'type': 'user_notification',
                'message': f'New group message from {self.user.username} in {self.group_name}: {message}',
            }
        )

    async def user_notification(self, event):
        # Send the notification to WebSocket
        await self.send(text_data=json.dumps({
            'notification': event['message']
        }))

    async def chat_message(self, event):
        message = event['message']
        user = event['user']

        # Send the message back to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user': user
        }))

    async def check_user_online(self, username):
        # Check if the user is part of the WebSocket group (online)
        online_users = await self.channel_layer.group_send(f"user_notifications_{username}")
        return len(online_users) > 0

    def send_email_alert(self, user, message):
        # Send an email notification to offline users
        send_mail(
            subject=f'New group message from {self.user.username} in {self.group_name}',
            message=f'You received a new message: "{message}"',
            from_email='your-email@example.com',
            recipient_list=[user.email]
        )
