from utilities.pending_action import PendingAction


class BaseCommand:
    command_name = ""
    command_keys = []

    def __init__(self, arguments, user_id, channel_id):
        self.arguments = arguments
        self.user_id = user_id
        self.channel_id = channel_id
        self.actions = []
        self.pending_actions = []

    def execute(self):
        raise NotImplementedError

    def get_actions(self):
        return self.actions

    def get_pending_actions(self):
        return self.pending_actions

    def _add_action(self, action):
        self.actions.append(action)

    def _add_pending_action(self, action, datetime):
        self.pending_actions.append(PendingAction(self.command_name, datetime, action))
