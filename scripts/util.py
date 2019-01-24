# -*- coding: UTF-8 -*-
"""
    scripts.util
    ~~~~~~~~~~~~

    Set of utility functions used in development and build build process.

    :copyright: (c) 2016-2019 by Alex Litvin.
    :license: GNU, see LICENSE for more details.
"""
import os

from PyQt5.QtCore import QFile, QIODevice, QTimer, QFileSystemWatcher
from PyQt5.QtGui import QPixmap

import grail
from scripts.css_preprocessor import CSSPreprocessor

THEME_FILE = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/../data/dist/theme.qss')


def print_step(title, *args):
    """Print build step to the console"""

    delimiter = '~~' * 30
    print("\n~%s\n~ Section: %s\n~%s" % (delimiter, title, delimiter))


def get_revision():
    """Returns version string with revision number (if possible)"""

    revision = grail.__version__

    try:
        # try to import hgapi, it may not be installed on build machine
        import hgapi

        repository = hgapi.Repo(os.path.abspath(os.curdir))
        revision = "%sb%d" % (grail.__version__, repository['tip'].rev)
    except ImportError:
        print("Failed to get revision number. Install 'hgapi' module.")
    except Exception as error:
        print("Unable to get revision number, following error occurred:")
        print(error)

    return revision


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


def create_version_file(path, revision):
    """Create .version file inside app directory"""

    directory = os.path.dirname(os.path.realpath(path))

    if not os.path.exists(directory):
        os.makedirs(directory)

    # add version file to build
    try:
        f = open(path, "w+")
        f.write(revision)
        f.close()

        print("\nVersion file created at %s" % path)
    except Exception as error:
        print("\nFailed to create a version file, following error occurred:")
        print(error)


def fix_png_profile(path, recursive=False, _main=True):
    """Fix annoying `libpng warning: iCCP: known incorrect sRGB profile`
    warning for files in given directory

    Args:
        path (str): path to directory
        recursive (bool): include sub-folders or not
        _main (bool): True if this is first non-recursive call
    """

    path = os.path.abspath(path)

    if not os.path.exists(path):
        return False

    if _main:
        print_step("Conforming PNG files")

    for name in os.listdir(path):
        link = os.path.join(path, name)

        if os.path.isfile(link) and link.endswith('.png'):
            try:
                pixmap = QPixmap()
                pixmap.load(link)

                file = QFile(link)
                file.open(QIODevice.WriteOnly)

                pixmap.save(link, "PNG")
                print('- %s' % link)
            except Exception as error:
                print(error)

        elif os.path.isdir(link):
            fix_png_profile(link, recursive, False)


def generate_stylesheet():
    """Compile theme.qss"""

    try:
        source = open('./data/dist/theme.qss', 'r')
        code = source.read()
        source.close()

        destination = open('./data/qt/theme.qss', 'w+')
        destination.write(CSSPreprocessor(code).compile())
        destination.close()

        print("Successfully generated theme")
    except Exception as error:
        print("Failed to generate theme.qss")
        print(error)


def update_stylesheet(watcher, app, path=""):
    """Read and compile stylesheet, then apply to application"""

    # Generate stylesheet
    print("Compiling theme.qss")

    try:
        source = open(THEME_FILE, 'r')
        code = source.read()
        source.close()
        stylesheet = CSSPreprocessor(code).compile(optimize=True)

        # setup stylesheet
        app.setStyleSheet(stylesheet)
    except Exception:
        print("Retry in 0.5 sec")
        QTimer.singleShot(500, lambda: update_stylesheet(watcher, app, path))

    watcher.addPath(THEME_FILE)


def apply_stylesheet_watcher(app):
    """Attach file watcher to application"""

    app.__file_watcher = QFileSystemWatcher()
    app.__file_watcher.addPath(THEME_FILE)
    app.__file_watcher.fileChanged.connect(lambda a: update_stylesheet(app.__file_watcher, app, a))

    # update stylesheet
    update_stylesheet(app.__file_watcher, app)
