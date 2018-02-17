import universal_bot
from commands.example import ExampleCommand

if __name__ == "__main__":
    universal_bot.add_commands([
        ExampleCommand
    ])

    universal_bot.connect()
    universal_bot.loop()
