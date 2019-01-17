
import re
import sys
from grailkit.util import OS_MAC, OS_LINUX, OS_WIN, default_key


class CSSPreprocessor:

    def __init__(self, text: str = ""):

        self.source = text
        self.code = text

        self.constants = {}

        self.define('MAC', OS_MAC)
        self.define('LINUX', OS_LINUX)
        self.define('WINDOWS', OS_WIN)

    def define(self, constant, value):
        """Define constant"""

        self.constants[constant] = value

    def reduce(self):
        """Remove comments and spaces"""

        code = self.code

        # remove comments
        code = re.sub(r'/\*[\s\S]*?\*/', "", code)

        # url() doesn't need quotes
        code = re.sub(r'url\((["\'])([^)]*)\1\)', r'url(\2)', code)

        # spaces may be safely collapsed as generated content will collapse them anyway
        code = re.sub(r'\s+', ' ', code)

        # shorten collapsible colors: #aabbcc to #abc
        code = re.sub(r'#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3(\s|;)', r'#\1\2\3\4', code)

        # fragment values can loose zeros
        code = re.sub(r':\s*0(\.\d+([cm]m|e[mx]|in|p[ctx]))\s*;', r':\1;', code)

        self.code = code

    def find_constants(self):
        """Collect all constants defined in source code"""

        regex = r'^@define\s+([a-zA-Z0-9_-]+)\s+(.*)$'
        pattern = re.compile(regex, re.MULTILINE | re.IGNORECASE)
        matches = pattern.findall(self.code)

        for match in matches:
            self.constants[match[0]] = match[1]

        self.code = re.sub(regex, '', self.code, flags=re.MULTILINE | re.IGNORECASE)

    def replace_constants(self):
        """Replace constants with values"""

        for key in sorted(self.constants, key=len, reverse=True):
            self.code = self.code.replace('$' + key, str(self.constants[key]))

    def fold_statements(self):
        """Find and fold @IF statements"""

        match = re.search(r'^@if ([\d\w_]+)', self.code, flags=re.MULTILINE | re.IGNORECASE)

        while match:
            key = match.group(1)
            value = default_key(self.constants, key, False)
            if_start = match.start(0)
            if_length = len(match.group(0))

            match_end = re.search(r'@end', self.code, flags=re.MULTILINE | re.IGNORECASE)
            end_start = match_end.start(0) if match_end else len(self.code)
            end_length = len(match_end.group(0)) if match_end else 0
            code = self.code

            if value:
                self.code = code[0:if_start] + code[if_start+if_length:end_start] + code[end_start+end_length:]
            else:
                self.code = code[0:if_start] + code[end_start+end_length:]

            match = re.search(r'^@if ([\d\w_]+)', self.code, flags=re.MULTILINE | re.IGNORECASE)

    def compile(self, optimize=False):
        """Compile code"""

        self.find_constants()
        self.replace_constants()
        self.fold_statements()

        if optimize:
            self.reduce()

        return self.code


CODE = """
/******************************************************************************
 *
 * Grail Style Sheet for Qt widgets and Plugins
 *
 *****************************************************************************/

@DEFINE TEXT_COLOR #f1f1f1
@if MAC
QWidget {mac-property: true;}
@end

@if WINDOWS
MainWindow {
    border: 1px solid red;
    }
@end

/** @section QWidget *********************************************************/

@define button-border 1px solid red

QWidget {
    background-color: #19232D;
    border: $button-border;
    padding: 0px;
    color: #F0F0F0;
    selection-background-color: #1464A0;
    selection-color: #F0F0F0;
    }

    QWidget:disabled {
        background-color: #19232D;
        color: #787878;
        selection-background-color: #14506E;
        selection-color: #787878;
        }

    QWidget:item:selected {
        background-color: $TEXT_COLOR;
        @if LINUX
        ~~~~~~~~~~~~~~~~~~~~~~~~~~
        @end
        }

    QWidget:item:hover {
        background-color: $TEXT_COLOR;
        color: #32414B;
        }
"""


def run():
    p = CSSPreprocessor(CODE)
    print(p.compile())
    print(p.constants)


if __name__ == '__main__':
    run()
