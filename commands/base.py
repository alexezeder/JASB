class BaseCommand:
    command_name = ""
    command_keys = []

    def __init__(self, arguments, user_id, channel_id):
        self.arguments = arguments
        self.user_id = user_id
        self.channel_id = channel_id
        self.actions = []

    def execute(self):
        raise NotImplementedError

    def get_actions(self):
        return self.actions

    def _add_action(self, action):
        self.actions.append(action)
