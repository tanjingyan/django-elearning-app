import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from courses.models import Course, Enrolment

from .models import ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.course_id = self.scope["url_route"]["kwargs"]["course_id"]
        self.room_group_name = f"course_chat_{self.course_id}"

        if not self.user.is_authenticated:
            await self.close()
            return

        has_access = await self.user_can_access_course()

        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message = data.get("message", "").strip()

        if not message:
            return

        if len(message) > 1000:
            return

        has_access = await self.user_can_access_course()

        if not has_access:
            await self.close()
            return

        chat_message = await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": chat_message["message"],
                "username": chat_message["username"],
                "role": chat_message["role"],
                "created_at": chat_message.created_at.strftime("%I:%M %p"),
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "username": event["username"],
                    "role": event["role"],
                    "created_at": event["created_at"],
                }
            )
        )

    @database_sync_to_async
    def user_can_access_course(self):
        try:
            course = Course.objects.get(
                id=self.course_id,
            )
        except Course.DoesNotExist:
            return False

        if (
            self.user.role == "teacher"
            and course.teacher_id == self.user.id
        ):
            return True

        if self.user.role == "student":
            return Enrolment.objects.filter(
                course=course,
                student=self.user,
            ).exists()

        return False

    @database_sync_to_async
    def save_message(self, message):
        course = Course.objects.get(
            id=self.course_id,
        )

        chat_message = ChatMessage.objects.create(
            course=course,
            sender=self.user,
            message=message,
        )

        return {
            "message": chat_message.message,
            "username": chat_message.sender.username,
            "role": chat_message.sender.role,
            "created_at": chat_message.created_at.strftime(
                "%I:%M %p"
            ),
        }