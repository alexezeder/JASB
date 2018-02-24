from commands.base import BaseCommand
from utilities.locks import Lock
import datetime


class TestCommand(BaseCommand):
    command_name = "Test command"
    command_keys = ["test", "command"]

    def __init__(self, arguments, user_id, channel_id):
        super().__init__(arguments, user_id, channel_id)

    def execute(self):
        super()._add_action({
            "method": "chat.postMessage",
            "channel": self.channel_id,
            "text": "result of test command"
        })

        test_wait = datetime.timedelta(seconds=10)
        super()._add_pending_action({
            "method": "chat.postMessage",
            "channel": self.channel_id,
            "text": "pending result of test command"
        }, datetime.datetime.now() + test_wait)
