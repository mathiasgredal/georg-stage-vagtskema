import logging
from georgstage.controller import Controller

logging.basicConfig(level=logging.INFO)


def main():
    app = Controller()
    app.main()


if __name__ == "__main__":
    main()
