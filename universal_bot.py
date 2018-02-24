import os
import time
import re
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from slackclient import SlackClient
from utilities.locks import Lock
from utilities.pending_actions_controller import PendingActionsController

RTM_READ_DELAY = 1
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
universal_bot_id = None
commands = []
executor = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())
pa_controller = PendingActionsController()


def add_commands(command_classes):
    command_names = set()
    for item in command_classes:
        if item.command_name not in command_names:
            command_names.add(item.command_name)
        else:
            raise RuntimeError("Duplicate of \"{}\" command name found".format(item.command_name))
        commands.append((item.command_keys, item))
    print("Commands: {} were added".format(", ".join(command_names).join(("(", ")"))))


def process_events(slack_events, multithreaded):
    for event in slack_events:
        message_for_bot = None
        if event["type"] == "message" and "subtype" not in event:
            res = slack_client.api_call("conversations.info", channel=event["channel"])
            if res["ok"]:
                channel_info = res["channel"]
                if channel_info["is_im"]:
                    user_id, message = parse_direct_mention(event["text"])
                    if user_id == universal_bot_id:
                        message_for_bot = message
                    else:
                        message_for_bot = event["text"]
                else:
                    user_id, message = parse_direct_mention(event["text"])
                    if user_id == universal_bot_id:
                        message_for_bot = message
        if message_for_bot is None:
            continue
        res = [x for x in message_for_bot.split(" ") if x]
        if len(res) != 0:
            if multithreaded:
                executor.submit(handle_command, res, event["user"], event["channel"])
            else:
                handle_command(res, event["user"], event["channel"])


def process_pending():
    if pa_controller.is_empty():
        return
    for keys, command_class in commands:
        res = pa_controller.get_actions(command_class.command_name)
        if len(res) != 0:
            for pending_action in res:
                if pending_action.check():
                    slack_client.api_call(**pending_action.get_action())
                    pa_controller.remove_action(pending_action)
                    print("Pending action of \"{}\" was executed".format(command_class.command_name))


def parse_direct_mention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(arguments, user_id, channel_id):
    for keys, command_class in commands:
        if len(arguments) >= len(keys) and arguments[:len(keys)] == keys:
            command_instance = command_class(arguments[len(keys):], user_id, channel_id)
            command_instance.execute()
            actions = command_instance.get_actions()
            with Lock():
                for action in actions:
                    slack_client.api_call(**action)
            pending_actions = command_instance.get_pending_actions()
            print("Command \"{}\" processed by {} in {}".format(command_instance.command_name, user_id, channel_id))

            if len(pending_actions) != 0:
                pa_controller.add_actions(pending_actions)
                if len(pending_actions) == 1:
                    print("\tand 1 pending action was added")
                else:
                    print("\tand {} pending actions were added".format(len(pending_actions)))

            return


def connect():
    global universal_bot_id

    if not slack_client.rtm_connect(with_team_state=False):
        raise RuntimeError("Connection can not be established")
    print("Connection established")
    universal_bot_id = slack_client.api_call("auth.test")["user_id"]


def loop(multithreaded=False):
    Lock.multithreaded = multithreaded
    print("Loop started {} multi-threading".format("with" if multithreaded else "without"))
    while True:
        process_events(slack_client.rtm_read(), multithreaded)
        process_pending()
        time.sleep(RTM_READ_DELAY)
