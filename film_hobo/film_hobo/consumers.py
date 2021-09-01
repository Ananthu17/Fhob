
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        print("connect")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'user_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        print("Closed websocket with code: ", close_code)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        self.close()

    # Receive message from WebSocket
    def receive(self, text_data):
        print("receive")
        response = json.loads(text_data)
        print(response)
        event = response.get("event", None)
        message = response.get("message", None)
        if event == 'TRACK':
            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                          self.room_group_name,
                          {
                            'type': 'send.notification',
                            'message': message,
                            "event": "TRACK"
                          })
        if event == 'FRIEND_REQUEST':
            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                          self.room_group_name,
                          {
                            'type': 'send.friend_request_notification',
                            'message': message,
                            "event": "FRIEND_REQUEST"
                          })
        if event == 'FRIEND_REQUEST_ACCEPT':
            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                          self.room_group_name,
                          {
                            'type': 'send_friend_request_accept_notification',
                            'message': message,
                            "event": "FRIEND_REQUEST_ACCEPT"
                          })
        if event == 'USER_RATING':
            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                          self.room_group_name,
                          {
                            'type': 'send_profile_rating_notification',
                            'message': message,
                            "event": "USER_RATING"
                          })

    def receive_json(self, content, **kwargs):
        print("Received event: {}".format(content))
        self.send_json(content)

    # Receive message from room group
    def send_notification(self, event):
        message = event['message']
        id = event['track_by_user_id']
        self.send(text_data=json.dumps({
            'message': message,
            'user_id': id,
            'event': "TRACK"
        }))

    # Receive message from room group
    def send_friend_request_notification(self, event):
        message = event['message']
        id = event['friend_request_from']
        self.send(text_data=json.dumps({
            'message': message,
            'user_id': id,
            'event': "FRIEND_REQUEST"
        }))

    # Receive message from room group
    def send_friend_request_accept_notification(self, event):
        message = event['message']
        id = event['from']
        self.send(text_data=json.dumps({
            'message': message,
            'user_id': id,
            'event': "FRIEND_REQUEST_ACCEPT"
        }))

    def send_profile_rating_notification(self, event):
        message = event['message']
        id = event['from']
        self.send(text_data=json.dumps({
            'message': message,
            'user_id': id,
            'event': "USER_RATING"
        }))

    def send_membership_notification(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message,
            'event': "MEMBERSHIP_CHANGE"
        }))

    def send_project_tracking_notification(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message,
            'event': "PROJECT_TRACKING"
        }))

    def send_audition_status_notification(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message,
            'event': "AUDITION_STATUS"
        }))

    def send_video_rating_notification(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message,
            'event': "VIDEO_RATING"
        }))

    def send_project_rating_notification(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message,
            'event': "PROJECT_RATING"
        }))

    def send_comments_mention_notification(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message,
            'event': "COMMENTS_MENTION"
        }))

    def send_comments_reply_notification(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message,
            'event': "COMMENTS_REPLY"
        }))

    def send_comments_notification(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message,
            'event': "COMMENTS"
        }))

    def send_cast_attach_request_notification(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message,
            'event': "CAST_ATTACH_REQUEST",
        }))

    def send_cast_attach_response_notification(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message,
            'event': "CAST_ATTACH_RESPONSE",
        }))


