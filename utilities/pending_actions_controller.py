class PendingActionsController:

    def __init__(self):
        self.pending_actions = []

    def add_actions(self, pending_actions):
        self.pending_actions.extend(pending_actions)

    def get_actions(self, command_name):
        return [x for x in self.pending_actions if x.command_name == command_name]

    def remove_action(self, pending_action):
        self.pending_actions.remove(pending_action)

    def is_empty(self):
        return not self.pending_actions
