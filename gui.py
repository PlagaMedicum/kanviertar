import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QDialog, QLabel
from text_processing import apply_all_rules

class ConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Пацвярджэнне замены")
        self.setFixedSize(600, 600)

        self.question_label = QLabel()
        self.old_text_label = QLabel()
        self.new_text_label = QLabel()
        self.confirm_button = QPushButton("Так")
        self.skip_button = QPushButton("Не")
        self.skip_all_button = QPushButton("«Не» для ўсіх наступных")

        layout = QVBoxLayout()
        layout.addWidget(self.question_label)
        layout.addWidget(self.old_text_label)
        layout.addWidget(self.new_text_label)
        layout.addWidget(self.confirm_button)
        layout.addWidget(self.skip_button)
        layout.addWidget(self.skip_all_button)
        self.setLayout(layout)

        self.confirm_button.clicked.connect(self.accept)
        self.skip_button.clicked.connect(self.reject)
        self.skip_all_button.clicked.connect(self.skip_all)

    def set_question_and_context(self, question, old_text, new_text):
        self.question_label.setText(question)
        self.old_text_label.setText(old_text)
        self.new_text_label.setText(new_text)

    def skip_all(self):
        self.parent().skip_all_flag = True
        self.reject()

class MainWindow(QMainWindow):
    def __init__(self, rules):
        super().__init__()

        self.rules = rules
        self.skip_all_flag = False  # Initialize the skip all flag
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Канвертар')
        self.setFixedSize(600, 400)

        self.text_edit = QTextEdit()

        # Set tab stop width to ensure proper rendering of tabs
        tab_stop_width = 30
        self.text_edit.setTabStopWidth(tab_stop_width)

        self.convert_button = QPushButton('Канвертаваць')
        self.convert_button.clicked.connect(self.convert_text)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.convert_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def convert_text(self):
        text = self.text_edit.toPlainText()
        new_text = apply_all_rules(text, self.rules, self)
        self.skip_all_flag = False

        # Wrap the text in a <pre> element with a CSS style for tabs
        new_text_display = f'<pre style="white-space: pre-wrap; tab-size: 4;">{new_text}</pre>'
        self.text_edit.setHtml(new_text_display)

    def show_confirmation_dialog(self, question, old_text, new_text):
        if self.skip_all_flag:
            print(f"Skipping confirmation window for '{old_text}'")
            return False
        dialog = ConfirmationDialog(self)
        dialog.set_question_and_context(question, old_text, new_text)
        result = dialog.exec_()
        print(f"Confirmation dialog result: {result}; returning {result == QDialog.Accepted}")
        return result == QDialog.Accepted

def run_gui(rules):
    app = QApplication(sys.argv)
    main_window = MainWindow(rules)
    main_window.show()
    sys.exit(app.exec_())

