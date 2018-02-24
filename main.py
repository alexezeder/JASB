import universal_bot
from commands.example import ExampleCommand
from commands.test import TestCommand

if __name__ == "__main__":
    universal_bot.add_commands([
        ExampleCommand,
        TestCommand
    ])

    universal_bot.connect()
    universal_bot.loop()
