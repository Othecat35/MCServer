from typing import NoReturn


def nothing_to_see_here_move_along() -> NoReturn:
    import random
    import sys

    messages: list[str] = [
        "The cake is a lie.",
        "Are these the world's most crispy fries? Lets find out!",
        "Also try Minecraft!",
        "Is that a Geometry Dash reference?",
    ]

    print(random.choice(messages))
    sys.exit(127)
