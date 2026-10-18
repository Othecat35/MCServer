from typing import NoReturn


def nothing_to_see_here_move_along() -> NoReturn:
    import getpass
    import random
    import sys

    messages: list[str] = [
        "The cake is a lie.",
        "Are these the world's most crispy fries? Lets find out!",
        "Also try Minecraft!",
        "Is that a Geometry Dash reference?",
        "Did you even read the Mojang EULA?",
        "What are you doing here?",
        "Wow, someone actually found this?",
        "The sun is a deadly laser.",
        "Oh, hi {username}!",
    ]

    message = random.choice(messages)
    new_message = message.replace("{username}", getpass.getuser())

    print(new_message)
    sys.exit(127)
