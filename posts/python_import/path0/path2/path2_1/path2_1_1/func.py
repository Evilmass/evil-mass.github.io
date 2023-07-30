from os.path import abspath, dirname


def echo():
    print(f"echo from: {abspath(dirname(__file__))}")


if __name__ == "__main__":
    echo()