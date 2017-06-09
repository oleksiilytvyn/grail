![grail.png](https://bitbucket.org/repo/xxy864/images/3941624082-grail.png)

# Grail #

Grail is an application for creating and executing cues that can send data over OSC (lyrics, display commands).
The goal of project to provide beautiful, simple and fast application for christian community.

## Dependencies ##

* Python 3.3 or higher
* PyQt 5 or higher
* grailkit (https://bitbucket.org/grailapp/grailkit or pip install grailkit)

If you want to build, you also need:

* cx_Freeze 5.0 or higher
* hgapi (https://bitbucket.org/haard/hgapi)
* pyrcc5 terminal utility (bundled with Qt)

## Running from sources ##

Change working directory to grail root and
execute following command in terminal:

    python grail.py

## How to build ##

Just run in terminal following command to build for your current platform

    python setup.py build
