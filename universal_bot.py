import os
import time
import re
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from slackclient import SlackClient
from utilities.locks import Lock

RTM_READ_DELAY = 1
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
universal_bot_id = None
commands = []
executor = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())


def add_commands(command_classes):
    for item in command_classes:
        commands.append((item.command_keys, item))


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
            print("Command {} processed by {} in {}".format(command_instance.command_name, user_id, channel_id))
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
        time.sleep(RTM_READ_DELAY)
