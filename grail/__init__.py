# -*- coding: UTF-8 -*-
"""
    grail.__init__
    ~~~~~~~~~~~~~~

    Bootstrap and run Grail
"""


import os
import sys

from grailkit import util
from grail.application import Grail

__version__ = '1.0.0'

APPLICATION_NAME = "Grail"
APPLICATION_WEB = "http://grailapp.com/"
ORGANISATION_NAME = "Grail"
ORGANISATION_DOMAIN = "grailapp.com"


def main():
    os.chdir(util.path_app())

    app = Grail(sys.argv)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
