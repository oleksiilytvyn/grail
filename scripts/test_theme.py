import re
import os
import sys
from distutils.core import run_setup

# using PyQt5 wrapper
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget
from PyQt5.QtCore import QTimer, Qt, QSettings, QByteArray, QPoint, QSize, QFile, QFileSystemWatcher

# import examples UI according to wrapper
from mw_menus_pyqt5_ui import Ui_MainWindow
from dw_buttons_pyqt5_ui import UI_ButtonWidget
from dw_displays_pyqt5_ui import UI_DisplaysWidget
from dw_inputs_fields_pyqt5_ui import UI_InputFieldsWidget
from dw_inputs_no_fields_pyqt5_ui import UI_InputsNoFiledsWidget
from dw_widgets_pyqt5_ui import UI_WidgetsWidget
from dw_views_pyqt5_ui import UI_ViewsWidget
from dw_containers_tabs_pyqt5_ui import UI_ContainersTabsWidget
from dw_containers_no_tabs_pyqt5_ui import UI_ContainersNoTabsWidget

from grailkit.util import application_location, OS_WIN, OS_LINUX, OS_MAC, OS_UNIX

from css_preprocessor import CSSPreprocessor


def print_step(title, *args):
    delimiter = '~~' * 30
    print("\n~%s\n~ Section: %s\n~%s" % (delimiter, title, delimiter))


def compile_resources(source=None, destination=None, exclude=None):
    """try to build resources file

    Args:
        source (str): path to folder with resources
        destination (str): path to python resource file
        exclude (list): list of excluded files and folders relative to given source
    """

    data_path = './data'
    source_file = os.path.join(source, 'resources.qrc')
    qrc_source = '''<!DOCTYPE RCC>\n<RCC version="1.0">\n\t<qresource>\n'''

    if not exclude:
        exclude = []

    for index, path in enumerate(exclude):
        exclude[index] = os.path.abspath(os.path.join(data_path, path))

    print("\nGenerating QRC file:")
    print(" - source: %s" % source)
    print(" - destination: %s" % destination)
    print(" - qrc file: %s" % source_file)

    for directory, directories, file_names in os.walk("./data"):

        # exclude directories
        if os.path.abspath(directory) in exclude:
            continue

        qrc_source += '\n\t\t<!-- ./%s/ -->\n' % directory[len(data_path) + 1:]

        for name in file_names:
            # skip system files
            if name.startswith('.'):
                continue

            file_path = os.path.join(directory, name)[len(data_path)+1:]
            qrc_source += '\t\t<file alias="%s">%s</file>\n' % (file_path, file_path)

    qrc_source += '\t</qresource>\n</RCC>'

    qrc_file = open(source_file, 'w')
    qrc_file.write(qrc_source)
    qrc_file.close()

    try:
        print("\nBuilding resource file")
        print("pyrcc5 -o %s %s" % (destination, source_file))
        os.system("pyrcc5 -o %s %s" % (destination, source_file))
    except Exception as error:
        print("Failed to build resource file, following error occurred:\n %s" % error)


def generate_stylesheet():

    try:
        source = open('./data/dist/theme.qss', 'r')
        code = source.read()
        source.close()

        destination = open('./data/rc/theme.qss', 'w+')
        destination.write(CSSPreprocessor(code).compile(optimize=True))
        destination.close()

        print("Successfully generated theme")
    except Exception as error:
        print("Failed to generate theme.qss")
        print(error)


def read_stylesheet(file_path):
    """Read and return stylesheet file contents

    Args:
        file_path (str): path to stylesheet file
    """

    if not file_path:
        return ""

    data = ""
    stream = QFile(file_path)

    if stream.open(QFile.ReadOnly):
        data = str(stream.readAll())
        stream.close()

    return re.sub(r'(\\n)|(\\r)|(\\t)', '', data)[2:-1]


def update_stylesheet(self, app, path=""):
    # Generate stylesheet
    print("Compiling theme.qss")

    try:
        source = open('./data/dist/theme.qss', 'r')
        code = source.read()
        source.close()
        stylesheet = CSSPreprocessor(code).compile(optimize=True)

        # setup stylesheet
        app.setStyleSheet(stylesheet)
    except PermissionError:
        print("Retry in 0.5 sec")
        QTimer.singleShot(500, lambda: update_stylesheet(self, app, path))

    self.addPath('./data/dist/theme.qss')


# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    # sys.exit(1)


# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


def main():

    os.chdir(os.path.abspath(application_location() + '/../'))

    # compile Qt resources
    # print_step("Compiling Qt resource")
    # compile_resources(source='./data', destination='./grail/resources.py', exclude=['./dist', '.'])

    from grail import resources

    # create the application
    app = QApplication(sys.argv)
    app.setOrganizationName('QDarkStyle')
    app.setApplicationName('QDarkStyle Example')

    watcher = QFileSystemWatcher()
    watcher.addPath('./data/dist/theme.qss')
    watcher.fileChanged.connect(lambda a: update_stylesheet(watcher, app, a))

    update_stylesheet(watcher, app)

    # create main window
    window = QMainWindow()
    window.setObjectName('mainwindow')
    ui = Ui_MainWindow()
    ui.setupUi(window)
    window.setWindowTitle("Dark theme test")

    # create docks for buttons
    dw_buttons = QDockWidget()
    dw_buttons.setObjectName('buttons')
    ui_buttons = UI_ButtonWidget()
    ui_buttons.setupUi(dw_buttons)
    window.addDockWidget(Qt.RightDockWidgetArea, dw_buttons)

    # create docks for buttons
    dw_displays = QDockWidget()
    dw_displays.setObjectName('displays')
    ui_displays = UI_DisplaysWidget()
    ui_displays.setupUi(dw_displays)
    window.addDockWidget(Qt.RightDockWidgetArea, dw_displays)

    # create docks for inputs - no fields
    dw_inputs_no_fields = QDockWidget()
    dw_inputs_no_fields.setObjectName('inputs_no_fields')
    ui_inputs_no_fields = UI_InputsNoFiledsWidget()
    ui_inputs_no_fields.setupUi(dw_inputs_no_fields)
    window.addDockWidget(Qt.RightDockWidgetArea, dw_inputs_no_fields)

    # create docks for inputs - fields
    dw_inputs_fields = QDockWidget()
    dw_inputs_fields.setObjectName('_fields')
    ui_inputs_fields = UI_InputFieldsWidget()
    ui_inputs_fields.setupUi(dw_inputs_fields)
    window.addDockWidget(Qt.RightDockWidgetArea, dw_inputs_fields)

    # create docks for widgets
    dw_widgets = QDockWidget()
    dw_widgets.setObjectName('widgets')
    ui_widgets = UI_WidgetsWidget()
    ui_widgets.setupUi(dw_widgets)
    window.addDockWidget(Qt.LeftDockWidgetArea, dw_widgets)

    # create docks for views
    dw_views = QDockWidget()
    dw_views.setObjectName('views')
    ui_views = UI_ViewsWidget()
    ui_views.setupUi(dw_views)
    window.addDockWidget(Qt.LeftDockWidgetArea, dw_views)

    # create docks for containers - no tabs
    dw_containers_no_tabs = QDockWidget()
    dw_containers_no_tabs.setObjectName('containers_no_tabs')
    ui_containers_no_tabs = UI_ContainersNoTabsWidget()
    ui_containers_no_tabs.setupUi(dw_containers_no_tabs)
    window.addDockWidget(Qt.LeftDockWidgetArea, dw_containers_no_tabs)

    # create docks for containers - tabs
    dw_containers_tabs = QDockWidget()
    dw_containers_tabs.setObjectName('containers')
    ui_containers_tabs = UI_ContainersTabsWidget()
    ui_containers_tabs.setupUi(dw_containers_tabs)
    window.addDockWidget(Qt.LeftDockWidgetArea, dw_containers_tabs)

    # tabify right docks
    window.tabifyDockWidget(dw_buttons, dw_displays)
    window.tabifyDockWidget(dw_displays, dw_inputs_fields)
    window.tabifyDockWidget(dw_inputs_fields, dw_inputs_no_fields)

    # tabify right docks
    window.tabifyDockWidget(dw_containers_no_tabs, dw_containers_tabs)
    window.tabifyDockWidget(dw_containers_tabs, dw_widgets)
    window.tabifyDockWidget(dw_widgets, dw_views)

    # run
    window.showMaximized()
    app.exec_()


if __name__ == "__main__":
    sys.exit(main())