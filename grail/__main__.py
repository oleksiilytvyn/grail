# -*- coding: UTF-8 -*-
"""
    Grail
    ~~~~~

    Run Grail as python package
"""

import os
import sys

from grailkit import util
from grail.application import Grail

if __name__ == "__main__":

    os.chdir(util.path_app())

    app = Grail(sys.argv)
    sys.exit(app.exec_())
