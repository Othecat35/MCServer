from typing import NoReturn


def nothing_to_see_here_move_along() -> NoReturn:
    import getpass
    import random
    import sys

    messages: list[str] = [
        "The cake is a lie.",
        "Also try Minecraft!",
        "Is that a Geometry Dash reference?",
        "Did you even read the Mojang EULA?",
        "What are you doing here?",
        "Wow, someone actually found this?",
        "The sun is a deadly laser.",
        "Oh, hi {username}!",
        "404 Not Found",
        "I hid a creeper inside your server.",
        "It worked on my machine.",
        "Have you mooed today?",
        "Why did the chicken cross the road?",
        "What's the meaning of life?",
        "/warp this_is_a_very_long_phrase_that_hopefully_is_not_in_any_dictionary",
        "418 I'm a teapot",
        "Hold F3+C for 10 seconds for a surprise!",
        "Segmentation fault (core dumped)",
        "about:mozilla in Firefox?",
        "Do not press Ctrl+Alt+F3 if you are not prepared!",
        "Othecat35 was here!",
        "sudo make me a sandwich",
        "Notch left the game",
        "Do a barrel roll!",
        "Have you tried stopping the server and starting it again?",
        "One must continuously pet the watchdog.",
        "One does not simply enter the source code.",
        "Keyboard not found. Press F1 to continue.",
        "Press F to pay respect.",
        "FIX MOJANG BEDROCK!",
        "FIX BEDROCK MOJANG!",
        "This server is powered by hopes and prayers.",
        "Chrome ate all of your RAM before the Minecraft server does.",
        "You're communicating like it was in 1960s",
    ]

    message: str = random.choice(messages)
    new_message: str = message.replace("{username}", getpass.getuser())

    print(new_message)
    sys.exit(127)
