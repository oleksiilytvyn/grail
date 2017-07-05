# -*- coding: UTF-8 -*-
"""
    grail
    ~~~~~

    Bootstrap and run Grail

    :copyright: (c) 2017 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""


import os
import sys

import grailkit
from grailkit import util
from grailkit.util import data_location, application_location

from grail.application import Grail

__version__ = '1.0.0'

APPLICATION_NAME = "Grail"
APPLICATION_WEB = "http://grailapp.com/"
ORGANISATION_NAME = "Grail"
ORGANISATION_DOMAIN = "grailapp.com"

LIBRARY_PATH = grailkit.PATH_LIBRARY
SETTINGS_PATH = os.path.join(data_location("grail"), "app.grail")

DEBUG = False


def main():
    """Run Grail application from location of installation"""

    os.chdir(application_location())

    app = Grail(sys.argv)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
