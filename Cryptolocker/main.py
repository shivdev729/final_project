import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from ui import MainWindow
import os
from metastore import setup

# Ensure metastore.py contains a function like:
# def setup(path):
#     with open(path, 'w') as f:
#         f.write('{}')

if __name__ == "__main__":
    
    metastore_path = os.path.join(os.path.dirname(__file__), "metastore.json")
    if not os.path.exists(metastore_path):
        setup()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())