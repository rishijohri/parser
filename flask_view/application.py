# Python
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLabel, QPushButton, QScrollArea, QSizePolicy
from PyQt5.QtGui import QFont, QColor, QPalette
import os
import json
class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        # Set window title and size
        self.setWindowTitle('Data Dictionary')
        self.resize(800, 600)

        # Set color scheme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor('white'))
        palette.setColor(QPalette.WindowText, QColor('skyblue'))
        palette.setColor(QPalette.Button, QColor('skyblue'))
        palette.setColor(QPalette.ButtonText, QColor('black'))
        palette.setColor(QPalette.Base, QColor('white'))
        palette.setColor(QPalette.Text, QColor('skyblue'))

        self.setPalette(palette)

        #read all files in project folder
        self.projects = {}
        for filename in os.listdir('projects'):
            with open('projects/' + filename) as f:
                self.projects[filename] = json.load(f)

        # Placeholder data
        self.projects = {'Project1': {'Var1': 'Definition1', 'Var2': 'Definition2'},
                         'Project2': {'Var3': 'Definition3', 'Var4': 'Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4Definition4'}}

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Dropdown for project selection
        self.project_dropdown = QComboBox()
        self.project_dropdown.setFont(QFont('Arial', 18))
        self.project_dropdown.addItems(self.projects.keys())
        self.layout.addWidget(self.project_dropdown)

        # Dropdown for variable selection
        self.variable_dropdown = QComboBox()
        self.variable_dropdown.setFont(QFont('Arial', 18))
        self.layout.addWidget(self.variable_dropdown)

        # Button for creating definition
        self.create_button = QPushButton('Create Definition')
        self.create_button.setFont(QFont('Arial', 18))
        self.create_button.clicked.connect(self.create_definition)
        self.layout.addWidget(self.create_button)

        # Label for displaying variable definition
        self.definition_label = QLabel()
        self.definition_label.setWordWrap(True)
        self.definition_label.setFont(QFont('Arial', 18))

        # Scroll area for the definition label
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.definition_label)
        self.layout.addWidget(self.scroll_area)

        # Populate the variable dropdown with the variables of the first project
        self.project_selected(self.project_dropdown.itemText(0))

    def project_selected(self, project):
        self.variable_dropdown.clear()
        self.variable_dropdown.addItems(self.projects[project].keys())

    def create_definition(self):
        project = self.project_dropdown.currentText()
        variable = self.variable_dropdown.currentText()
        self.definition_label.setText(self.projects[project][variable])

if __name__ == '__main__':
    app = QApplication([])
    window = MyApp()
    window.show()
    app.exec_()