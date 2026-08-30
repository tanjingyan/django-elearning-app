from asgiref.sync import async_to_sync

from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator

from django.test import TransactionTestCase, override_settings

from accounts.models import CustomUser
from courses.models import Course, CourseBlock, Enrolment

from chat.models import ChatMessage
from chat.routing import websocket_urlpatterns


class UserScopeMiddleware:
    """
    Adds a test user to the WebSocket scope.

    This allows ChatConsumer authentication and
    course-access rules to be tested without using
    a real browser session.
    """

    def __init__(self, app, user):
        self.app = app
        self.user = user

    async def __call__(
        self,
        scope,
        receive,
        send,
    ):
        scope = dict(scope)
        scope["user"] = self.user

        return await self.app(
            scope,
            receive,
            send,
        )


@override_settings(
    CHANNEL_LAYERS={
        "default": {
            "BACKEND": (
                "channels.layers."
                "InMemoryChannelLayer"
            ),
        },
    }
)
class ChatConsumerTests(TransactionTestCase):

    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            username="chat_teacher",
            password="testpass123",
            role="teacher",
        )

        self.student = CustomUser.objects.create_user(
            username="chat_student",
            password="testpass123",
            role="student",
        )

        self.other_student = (
            CustomUser.objects.create_user(
                username="other_student",
                password="testpass123",
                role="student",
            )
        )

        self.course = Course.objects.create(
            teacher=self.teacher,
            title="WebSocket Testing Course",
            description="Course used for chat tests.",
        )

        Enrolment.objects.create(
            student=self.student,
            course=self.course,
        )

    def create_communicator(self, user):
        application = UserScopeMiddleware(
            URLRouter(
                websocket_urlpatterns
            ),
            user,
        )

        return WebsocketCommunicator(
            application,
            (
                f"/ws/chat/course/"
                f"{self.course.id}/"
            ),
        )

    # -----------------------------------------
    # Enrolled student can connect and
    # send a message
    # -----------------------------------------

    def test_enrolled_student_can_send_chat_message(self):

        async def run_test():
            communicator = self.create_communicator(
                self.student
            )

            connected, _ = (
                await communicator.connect()
            )

            self.assertTrue(
                connected
            )

            await communicator.send_json_to(
                {
                    "message": "Hello from student!",
                }
            )

            response = (
                await communicator.receive_json_from()
            )

            self.assertEqual(
                response["message"],
                "Hello from student!",
            )

            self.assertEqual(
                response["username"],
                "chat_student",
            )

            self.assertEqual(
                response["role"],
                "student",
            )

            await communicator.disconnect()

        async_to_sync(run_test)()

        self.assertTrue(
            ChatMessage.objects.filter(
                course=self.course,
                sender=self.student,
                message="Hello from student!",
            ).exists()
        )

    # -----------------------------------------
    # Course teacher can connect
    # -----------------------------------------

    def test_course_teacher_can_connect_to_chat(self):

        async def run_test():
            communicator = self.create_communicator(
                self.teacher
            )

            connected, _ = (
                await communicator.connect()
            )

            self.assertTrue(
                connected
            )

            await communicator.disconnect()

        async_to_sync(run_test)()

    # -----------------------------------------
    # Non-enrolled student is rejected
    # -----------------------------------------

    def test_non_enrolled_student_cannot_connect(self):

        async def run_test():
            communicator = self.create_communicator(
                self.other_student
            )

            connected, close_code = (
                await communicator.connect()
            )

            self.assertFalse(
                connected
            )

            self.assertEqual(
                close_code,
                4003,
            )

        async_to_sync(run_test)()

    # -----------------------------------------
    # Blocked student is rejected
    # -----------------------------------------

    def test_blocked_student_cannot_connect(self):
        CourseBlock.objects.create(
            student=self.student,
            course=self.course,
        )

        async def run_test():
            communicator = self.create_communicator(
                self.student
            )

            connected, close_code = (
                await communicator.connect()
            )

            self.assertFalse(
                connected
            )

            self.assertEqual(
                close_code,
                4003,
            )

        async_to_sync(run_test)()

    # -----------------------------------------
    # Message above maximum length is ignored
    # -----------------------------------------

    def test_message_over_1000_characters_is_rejected(
        self
    ):

        async def run_test():
            communicator = self.create_communicator(
                self.student
            )

            connected, _ = (
                await communicator.connect()
            )

            self.assertTrue(
                connected
            )

            long_message = "A" * 1001

            await communicator.send_json_to(
                {
                    "message": long_message,
                }
            )

            # Consumer should not broadcast
            # anything for an invalid message.
            no_response = (
                await communicator.receive_nothing(
                    timeout=0.2
                )
            )

            self.assertTrue(
                no_response
            )

            await communicator.disconnect()

        async_to_sync(run_test)()

        self.assertFalse(
            ChatMessage.objects.filter(
                course=self.course,
                sender=self.student,
            ).exists()
        )