import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from courses.models import Course, CourseBlock, Enrolment

from .models import ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        self.course_id = self.scope[
            "url_route"
        ]["kwargs"]["course_id"]

        self.room_group_name = (
            f"course_chat_{self.course_id}"
        )

        # Reject users who are not logged in.
        if not self.user.is_authenticated:
            await self.close(code=4001)
            return

        # Check that the user belongs to this course.
        has_access = await self.user_can_access_course()

        if not has_access:
            await self.close(code=4003)
            return

        # Add the current WebSocket connection to
        # the course discussion group.
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

        message = data.get(
            "message",
            "",
        ).strip()

        # Prevent empty messages.
        if not message:
            return

        # Maximum message length.
        if len(message) > 1000:
            return

        # Check permission again before saving.
        has_access = await self.user_can_access_course()

        if not has_access:
            await self.close(code=4003)
            return

        # save_message returns a dictionary.
        saved_message = await self.save_message(
            message
        )

        # Broadcast the message to everyone
        # connected to this course discussion.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "id": saved_message["id"],
                "message": saved_message["message"],
                "username": saved_message["username"],
                "role": saved_message["role"],
                "created_at": saved_message["created_at"],
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "id": event["id"],
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
                id=self.course_id
            )
        except Course.DoesNotExist:
            return False

        # Only the teacher who owns this course
        # can access its discussion.
        if (
            self.user.role == "teacher"
            and course.teacher_id == self.user.id
        ):
            return True

        # Students must be enrolled and not blocked.
        if self.user.role == "student":
            is_blocked = CourseBlock.objects.filter(
                course=course,
                student=self.user,
            ).exists()

            if is_blocked:
                return False

            return Enrolment.objects.filter(
                course=course,
                student=self.user,
            ).exists()

        return False

    @database_sync_to_async
    def save_message(self, message):
        course = Course.objects.get(
            id=self.course_id
        )

        chat_message = ChatMessage.objects.create(
            course=course,
            sender=self.user,
            message=message,
        )

        return {
            "id": chat_message.id,
            "message": chat_message.message,
            "username": chat_message.sender.username,
            "role": chat_message.sender.role,
            "created_at": (
                chat_message.created_at.strftime(
                    "%I:%M %p"
                )
            ),
        }