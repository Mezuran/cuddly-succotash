import sys
import os
from streamlit.web import cli as stcli

def run():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ui_path = os.path.join(current_dir, "ui.py")

    sys.argv = ["streamlit", "run", ui_path]
    sys.exit(stcli.main())

if __name__ == "__main__":
    run()