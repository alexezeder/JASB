import datetime


class PendingAction:

    def __init__(self, command_name, pending_datetime, action):
        self.command_name = command_name
        self.pending_datetime = pending_datetime
        self.action = action

    def check(self):
        return datetime.datetime.now() > self.pending_datetime

    def get_action(self):
        return self.action
