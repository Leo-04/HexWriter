from UI.app import App
from cli import command_line_interface
import sys
import os


def main():
    dir_path = os.path.dirname(os.path.abspath(sys.argv[0]))

    if len(sys.argv) > 1:
        command_line_interface()
    else:
        app = App(f"{dir_path}/style.style")
        app.run()


if __name__ == "__main__":
    main()
