from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QPushButton, QLabel, QSizePolicy, QStackedLayout, QFileDialog, QProgressBar, QTextEdit
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit, QHBoxLayout
import sys,os
import traceback
from datetime import datetime
from crypto import encrypt_file,decrypt_file,HashMismatchError
from metastore import EntryNotFoundError
from PyQt5.QtWidgets import QMessageBox


class FileUploadFrame(QFrame):
    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.vbox = QVBoxLayout(self)
        self.vbox.setAlignment(Qt.AlignCenter)
        self.label = QLabel(label_text)
        self.label.setFont(QFont("Helvetica", 13, QFont.Bold))
        self.label.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.label)
    
        # Create a container widget to center the upload button

        btn_container = QWidget()
        btn_container.setMinimumWidth(450)
        btn_container.setMaximumWidth(650)
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        self.upload_btn = QPushButton("Upload File   ")
        self.upload_btn.setStyleSheet("padding:1rem;font-weight:bold;color:red")
        self.upload_btn.setFont(QFont("Helvetica", 10))
        self.upload_btn.setIcon(QIcon("icon.svg"))
        self.upload_btn.setMinimumWidth(450)
        self.upload_btn.setMaximumWidth(650)

        btn_layout.addWidget(self.upload_btn)
        self.vbox.addWidget(btn_container, alignment=Qt.AlignCenter)

        self.upload_btn.setStyleSheet(self.upload_btn.styleSheet() + "QPushButton { qproperty-iconAlignment: AlignRight; }")
        self.upload_btn.clicked.connect(self.open_file_dialog)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)  # Hide initially
        self.vbox.addWidget(self.progress)

    def open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_name:
            self.on_file_selected(file_name)

    def on_file_selected(self, file_name):
        # To be overridden in subclasses
        pass

class OutputFolderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        hbox = QHBoxLayout(self)
        container = QWidget()
        container.setMaximumWidth(450)
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Select output folder...")
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setFont(QFont("Helvetica", 10))
        self.browse_btn.setIcon(QIcon("folder.png"))
        container_layout.addWidget(self.line_edit)
        container_layout.addWidget(self.browse_btn)
        hbox.addWidget(container)
        self.setLayout(hbox)
        self.browse_btn.clicked.connect(self.select_output_folder)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.line_edit.setText(folder)

    def output_folder(self):
        return self.line_edit.text()

class EncryptFrame(FileUploadFrame):
    def __init__(self, parent=None):
        super().__init__("Encrypt Content", parent)
        self.output_widget = OutputFolderWidget()
        self.vbox.addWidget(self.output_widget)

        # Add encryption key input
        # Create a container widget to group key_input and text
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter encryption key...")
        container_layout.addWidget(self.key_input)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setPlaceholderText("Encryption details will appear here...")

        container.setMinimumWidth(450)
        container.setMaximumWidth(650)
        container_layout.addWidget(self.text)

        # Add the container to the main layout and center it
        self.vbox.addWidget(container, alignment=Qt.AlignCenter)
        # Create a container widget to center the encrypt button
        btn_container = QWidget()
        btn_container.setMinimumWidth(450)
        btn_container.setMaximumWidth(650)
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        self.encrypt_btn = QPushButton("Encrypt Now")
        self.encrypt_btn.setFont(QFont("Helvetica", 11, QFont.Bold))
        # self.encrypt_btn.setMinimumWidth(450)
        self.encrypt_btn.setStyleSheet("""
            QPushButton {
            background-color: #c0392b;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            padding: 10px 20px;
            }
            QPushButton:hover {
            background-color: #a93226;
            }
        """)
        btn_layout.addWidget(self.encrypt_btn)
        self.vbox.addWidget(btn_container, alignment=Qt.AlignCenter,stretch=1)
        self.vbox.addStretch(1)

        self.selected_file = None
        self.encrypt_btn.clicked.connect(self.encrypt_file)

    def on_file_selected(self, file_name):
        self.selected_file = file_name
        self.text.setText(f"Selected for encryption:\n{file_name}\nOutput: {self.output_widget.output_folder()}")
        self.progress.setValue(50)  # Example progress

    def encrypt_file(self):
        print(self.selected_file)
        if not self.selected_file:
            self.text.setText("No file selected for encryption.")
            return
        output_folder = self.output_widget.output_folder()
        if not output_folder:
            self.text.setText("No output folder selected.")
            return
        key = self.key_input.text()
        if not key:
            self.text.setText("No encryption key entered.")
            return
        try:
            input_path = self.selected_file
            output_path = os.path.join(output_folder, os.path.basename(input_path) + ".enc")
            encrypt_file(key,input_path, output_path)
            self.text.setText(f"Encryption successful!\nOutput file: {output_path}")
            self.progress.setValue(100)
        except Exception as e:
            self.text.setText(f"Encryption failed:\n{str(e)}\n{traceback.format_exc()}")
            self.progress.setValue(0)

    def on_file_selected(self, file_name):
        self.selected_file = file_name
        self.text.setText(f"Selected for encryption:\n{file_name}\nOutput: {self.output_widget.output_folder()}")
        self.progress.setValue(50)  # Example progress

class DecryptFrame(FileUploadFrame):
    def __init__(self, parent=None):
        super().__init__("Decrypt Content", parent)
        self.output_widget = OutputFolderWidget()
        self.vbox.addWidget(self.output_widget)

        # Add decryption key input
        # Create a container widget to group key_input and text
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter decryption key...")
        self.key_input.setMinimumWidth(450)
        container_layout.addWidget(self.key_input)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setMinimumWidth(450)

        container.setMinimumWidth(450)
        container.setMaximumWidth(650)
        self.text.setPlaceholderText("Decryption details will appear here...")
        container_layout.addWidget(self.text)
    

        # Add the container to the main layout and center it
        
        self.vbox.addWidget(container, alignment=Qt.AlignCenter)

        btn_container = QWidget()
        btn_container.setMinimumWidth(450)
        btn_container.setMaximumWidth(650)
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        self.decrypt_btn = QPushButton("Decrypt Now")
        self.decrypt_btn.setFont(QFont("Helvetica", 11, QFont.Bold))
        self.decrypt_btn.setStyleSheet("""
            QPushButton {
            background-color: #27ae60;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            padding: 10px 20px;
            }
            QPushButton:hover {
            background-color: #229954;
            }
        """)
        btn_layout.addWidget(self.decrypt_btn)
        self.vbox.addWidget(btn_container, alignment=Qt.AlignCenter,stretch=1)
        self.vbox.addStretch(1)

        self.selected_file = None
        self.decrypt_btn.clicked.connect(self.decrypt_file)

    def on_file_selected(self, file_name):
        self.selected_file = file_name
        self.text.setText(f"Selected for decryption:\n{file_name}\nOutput: {self.output_widget.output_folder()}")
        self.progress.setValue(50)  # Example progress

    def decrypt_file(self):
        if not self.selected_file:
            self.text.setText("No file selected for decryption.")
            return
        output_folder = self.output_widget.output_folder()
        if not output_folder:
            self.text.setText("No output folder selected.")
            return
        key = self.key_input.text()
        if not key:
            self.text.setText("No decryption key entered.")
            return
        try:
            input_path = self.selected_file
            # Remove .enc extension if present for output
            base_name = os.path.basename(input_path)
            if base_name.endswith(".enc"):
                base_name = base_name[:-4]
            output_path = os.path.join(output_folder, base_name)
            data = decrypt_file(key, input_path, output_path)
            self.text.setText(f"File hash verified\nFile name: {data.get("filename")}\nTimestamp: {datetime.fromtimestamp(data.get("timestamp"))}\nDecryption successful!\nOutput file: {output_path}")
            self.progress.setValue(100)
        except Exception as e:
            # Omit stacktrace
            # self.text.setText(f"Decryption failed:\n{str(e)}\n{traceback.format_exc()}")
            self.text.setText(f"Decryption failed:\n{str(e)}\n")
            msg = ""
            if isinstance(e,HashMismatchError):
                msg = "Hash couldn't be verified. File integrity breached."
            else:
                # Omit stacktrace
                msg = f"An error occurred during decryption:\n{str(e)}"
            QMessageBox.critical(self, "Decryption Failed", msg)
            self.progress.setValue(0)

class Pane1(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        vbox = QVBoxLayout(self)
        button_style = """
            QPushButton {
                background-color: #444851;
                color: white;
                font-family: Helvetica, Arial, sans-serif;
                font-weight: bold;
                font-size: 15px;
                border-radius: 8px;
                padding: 10px 20px 10px 16px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #5a5f6a;
            }
        """
        font = QFont("Helvetica", 11, QFont.Bold)

        def create_button(text, icon_path):
            btn = QPushButton(text)
            btn.setFont(font)
            btn.setStyleSheet(
                button_style +
                "QPushButton::menu-indicator { image: none; }"
                "QPushButton { qproperty-iconAlignment: AlignRight; }"
            )
            btn.setLayoutDirection(Qt.LeftToRight)
            btn.setIcon(QIcon(icon_path))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            return btn

        self.btn_encrypt = create_button("Encrypt", "lock.png")
        self.btn_decrypt = create_button("Decrypt", "unlock.png")

        vbox.addWidget(self.btn_encrypt)
        vbox.addWidget(self.btn_decrypt)
        vbox.addStretch(1)

class Pane2(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f5f6fa, stop:1 #d6dbe9
                );
                border-radius: 18px;
                border: 2px solid #b2bec3;
                box-shadow: 0px 8px 24px rgba(44, 62, 80, 0.08);
            }
        """)
        self.setStyleSheet("background-color: #ddd;")
        self.stacked_layout = QStackedLayout(self)

        self.encrypt_frame = EncryptFrame()
        self.decrypt_frame = DecryptFrame()

        self.stacked_layout.addWidget(self.encrypt_frame)  # index 0
        self.stacked_layout.addWidget(self.decrypt_frame)  # index 1

    def set_page(self, index):
        self.stacked_layout.setCurrentIndex(index)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cryptolocker")
        self.setWindowIcon(QtGui.QIcon('icon.svg'))
        self.setStyleSheet("background-color: #272727;")  # Set window background

        layout = QHBoxLayout(self)
        self.pane1 = Pane1(self)
        self.pane2 = Pane2(self)

        layout.addWidget(self.pane1, 1)
        layout.addWidget(self.pane2, 3)
        self.setLayout(layout)

        # Connect buttons to change content in pane2
        self.pane1.btn_encrypt.clicked.connect(lambda: self.pane2.set_page(0))
        self.pane1.btn_decrypt.clicked.connect(lambda: self.pane2.set_page(1))

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("QWidget { color: white; }")  # Set default text color to white
    window = MainWindow()
    window.setFixedSize(640, 480)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
