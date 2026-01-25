import sys
from pathlib import Path
from streamlit.web import cli as stcli

def run():
    current_dir = Path(__file__).parent
    ui_path = current_dir / "ui.py"

    sys.argv = ["streamlit", "run", str(ui_path)]
    sys.exit(stcli.main())

if __name__ == "__main__":
    run()