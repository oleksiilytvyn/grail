import os
import sys

from PyQt5.QtCore import QFileSystemWatcher, QTimer

from grailkit.util import application_location
from css_preprocessor import CSSPreprocessor


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


def main():

    from grail.application import Grail

    os.chdir(os.path.abspath(application_location() + '/../'))

    app = Grail(sys.argv)

    watcher = QFileSystemWatcher()
    watcher.addPath('./data/dist/theme.qss')
    watcher.fileChanged.connect(lambda a: update_stylesheet(watcher, app, a))

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
