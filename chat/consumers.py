import json
import uuid

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from courses.models import Course, CourseBlock, Enrolment

from .models import ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        # =====================================================
        # USER / COURSE
        # =====================================================

        self.user = self.scope["user"]

        self.course_id = self.scope[
            "url_route"
        ]["kwargs"]["course_id"]

        self.room_group_name = (
            f"course_chat_{self.course_id}"
        )

        # Each browser tab / WebSocket gets its own ID.
        # This prevents one tab closing from incorrectly
        # marking a user offline when another tab is still open.
        self.connection_id = uuid.uuid4().hex

        self.joined_group = False


        # =====================================================
        # AUTHENTICATION
        # =====================================================

        if not self.user.is_authenticated:

            await self.close(
                code=4001
            )

            return


        # =====================================================
        # COURSE ACCESS
        # =====================================================

        has_access = (
            await self.user_can_access_course()
        )


        if not has_access:

            await self.close(
                code=4003
            )

            return


        # =====================================================
        # JOIN COURSE CHAT GROUP
        # =====================================================

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )


        self.joined_group = True


        await self.accept()


        # =====================================================
        # GET PRESENCE INFORMATION
        # =====================================================

        presence_data = (
            await self.get_presence_data()
        )


        # =====================================================
        # ANNOUNCE THAT THIS USER JOINED
        # =====================================================

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "presence_join",
                "connection_id": (
                    self.connection_id
                ),
                "username": (
                    presence_data["username"]
                ),
                "role": (
                    presence_data["role"]
                ),
                "profile_picture": (
                    presence_data[
                        "profile_picture"
                    ]
                ),
            },
        )


        # =====================================================
        # REQUEST CURRENT ONLINE USERS
        #
        # Existing WebSocket connections will reply directly
        # to this newly connected channel.
        # =====================================================

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "presence_request",
                "requester_channel_name": (
                    self.channel_name
                ),
            },
        )


    # =========================================================
    # DISCONNECT
    # =========================================================

    async def disconnect(
        self,
        close_code,
    ):

        if not getattr(
            self,
            "joined_group",
            False,
        ):

            return


        # Tell everyone which specific connection left.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "presence_leave",
                "connection_id": (
                    self.connection_id
                ),
                "username": (
                    self.user.username
                ),
            },
        )


        # Remove this WebSocket connection from the group.
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )


        self.joined_group = False


    # =========================================================
    # RECEIVE MESSAGE FROM BROWSER
    # =========================================================

    async def receive(
        self,
        text_data,
    ):

        try:

            data = json.loads(
                text_data
            )

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


        # Re-check permission before saving.
        has_access = (
            await self.user_can_access_course()
        )


        if not has_access:

            await self.close(
                code=4003
            )

            return


        # =====================================================
        # SAVE MESSAGE
        # =====================================================

        saved_message = (
            await self.save_message(
                message
            )
        )


        # =====================================================
        # BROADCAST MESSAGE
        # =====================================================

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "id": (
                    saved_message["id"]
                ),
                "message": (
                    saved_message["message"]
                ),
                "username": (
                    saved_message["username"]
                ),
                "role": (
                    saved_message["role"]
                ),
                "created_at": (
                    saved_message[
                        "created_at"
                    ]
                ),
            },
        )


    # =========================================================
    # CHAT MESSAGE EVENT
    # =========================================================

    async def chat_message(
        self,
        event,
    ):

        await self.send(
            text_data=json.dumps(
                {
                    "event": "chat_message",
                    "id": event["id"],
                    "message": (
                        event["message"]
                    ),
                    "username": (
                        event["username"]
                    ),
                    "role": (
                        event["role"]
                    ),
                    "created_at": (
                        event["created_at"]
                    ),
                }
            )
        )


    # =========================================================
    # PRESENCE - USER JOINED
    # =========================================================

    async def presence_join(
        self,
        event,
    ):

        await self.send(
            text_data=json.dumps(
                {
                    "event": "presence_join",
                    "connection_id": (
                        event[
                            "connection_id"
                        ]
                    ),
                    "username": (
                        event["username"]
                    ),
                    "role": (
                        event["role"]
                    ),
                    "profile_picture": (
                        event[
                            "profile_picture"
                        ]
                    ),
                }
            )
        )


    # =========================================================
    # PRESENCE - USER LEFT
    # =========================================================

    async def presence_leave(
        self,
        event,
    ):

        await self.send(
            text_data=json.dumps(
                {
                    "event": "presence_leave",
                    "connection_id": (
                        event[
                            "connection_id"
                        ]
                    ),
                    "username": (
                        event["username"]
                    ),
                }
            )
        )


    # =========================================================
    # PRESENCE REQUEST
    #
    # A newly connected user asks each existing consumer to
    # announce itself directly to that new connection.
    # =========================================================

    async def presence_request(
        self,
        event,
    ):

        requester_channel_name = (
            event[
                "requester_channel_name"
            ]
        )


        presence_data = (
            await self.get_presence_data()
        )


        await self.channel_layer.send(
            requester_channel_name,
            {
                "type": (
                    "presence_snapshot_member"
                ),
                "connection_id": (
                    self.connection_id
                ),
                "username": (
                    presence_data[
                        "username"
                    ]
                ),
                "role": (
                    presence_data["role"]
                ),
                "profile_picture": (
                    presence_data[
                        "profile_picture"
                    ]
                ),
            },
        )


    # =========================================================
    # SEND SNAPSHOT MEMBER TO NEW USER
    # =========================================================

    async def presence_snapshot_member(
        self,
        event,
    ):

        await self.send(
            text_data=json.dumps(
                {
                    "event": (
                        "presence_snapshot"
                    ),
                    "connection_id": (
                        event[
                            "connection_id"
                        ]
                    ),
                    "username": (
                        event["username"]
                    ),
                    "role": (
                        event["role"]
                    ),
                    "profile_picture": (
                        event[
                            "profile_picture"
                        ]
                    ),
                }
            )
        )


    # =========================================================
    # CHECK COURSE ACCESS
    # =========================================================

    @database_sync_to_async
    def user_can_access_course(self):

        try:

            course = Course.objects.get(
                id=self.course_id
            )

        except Course.DoesNotExist:

            return False


        # =====================================================
        # TEACHER
        #
        # Only the teacher who owns the course may access
        # this course discussion.
        # =====================================================

        if (
            self.user.role == "teacher"
            and
            course.teacher_id
            == self.user.id
        ):

            return True


        # =====================================================
        # STUDENT
        #
        # Student must:
        # 1. Be enrolled
        # 2. Not be blocked
        # =====================================================

        if self.user.role == "student":

            is_blocked = (
                CourseBlock.objects.filter(
                    course=course,
                    student=self.user,
                ).exists()
            )


            if is_blocked:

                return False


            return (
                Enrolment.objects.filter(
                    course=course,
                    student=self.user,
                ).exists()
            )


        return False


    # =========================================================
    # PRESENCE INFORMATION
    # =========================================================

    @database_sync_to_async
    def get_presence_data(self):

        profile_picture = None


        if self.user.profile_picture:

            try:

                profile_picture = (
                    self.user
                    .profile_picture
                    .url
                )

            except ValueError:

                profile_picture = None


        return {
            "username": (
                self.user.username
            ),
            "role": (
                self.user.role
            ),
            "profile_picture": (
                profile_picture
            ),
        }


    # =========================================================
    # SAVE MESSAGE
    # =========================================================

    @database_sync_to_async
    def save_message(
        self,
        message,
    ):

        course = Course.objects.get(
            id=self.course_id
        )


        chat_message = (
            ChatMessage.objects.create(
                course=course,
                sender=self.user,
                message=message,
            )
        )


        return {
            "id": (
                chat_message.id
            ),

            "message": (
                chat_message.message
            ),

            "username": (
                chat_message
                .sender
                .username
            ),

            "role": (
                chat_message
                .sender
                .role
            ),

            "created_at": (
                chat_message
                .created_at
                .isoformat()
            ),
        }