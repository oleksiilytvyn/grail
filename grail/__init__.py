# -*- coding: UTF-8 -*-
"""
    grail.__init__
    ~~~~~~~~~~~~~~

    Bootstrap and run Grail
"""


import os
import sys

import grailkit
from grailkit import util
from grailkit.util import path_appdata

from grail.application import Grail

__version__ = '1.0.0'

APPLICATION_NAME = "Grail"
APPLICATION_WEB = "http://grailapp.com/"
ORGANISATION_NAME = "Grail"
ORGANISATION_DOMAIN = "grailapp.com"

LIBRARY_PATH = grailkit.PATH_LIBRARY
SETTINGS_PATH = os.path.join(path_appdata("grail"), "app.grail")


def main():
    os.chdir(util.path_app())

    app = Grail(sys.argv)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
