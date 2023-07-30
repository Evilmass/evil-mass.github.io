# import func
from func import echo as local_echo

# import text
from text.func import echo as text_echo


def echo_special():
    # func.echo()
    local_echo()

    # text.echo()
    text_echo()


if __name__ == "__main__":
    echo_special()