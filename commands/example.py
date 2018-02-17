from commands.base import BaseCommand
from utilities.locks import Lock


class ExampleCommand(BaseCommand):
    command_name = "Example command"
    command_keys = ["example", "command"]

    def __init__(self, arguments, user_id, channel_id):
        super().__init__(arguments, user_id, channel_id)

    def execute(self):
        with Lock():
            print("args: ", self.arguments)

        super()._add_action({
            "method": "chat.postMessage",
            "channel": self.channel_id,
            "text": "result of example command"
        })
