# -*- coding: UTF-8 -*-
"""
    grail.plugins.console_viewer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    View python console output & execute commands

    :copyright: (c) 2018 by Grail Team.
    :license: GNU, see LICENSE for more details.
"""
import sys
import traceback

from grail.qt import *
from grail.core import Viewer


def create_format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)

    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)

    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': create_format('#cd7827'),
    'operator': create_format('#a8b6c6'),
    'brace': create_format('#a8b6c6'),
    'defclass': create_format('#b400b4', 'bold'),
    'string': create_format('#698857'),
    'string2': create_format('#698857'),
    'comment': create_format('#6a6a6a', 'italic'),
    'self': create_format('#764771', 'italic'),
    'numbers': create_format('#6697bd'),
}


class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language."""

    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword']) for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator']) for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace']) for b in PythonHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """

        # Do other syntax formatting
        for expression, nth, format_style in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))

                self.setFormat(index, length, format_style)

                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)

        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False


class ConsoleViewer(Viewer):
    """Python console"""

    id = 'console'
    name = 'Console'
    author = 'Grail Team'
    description = 'Python console'

    def __init__(self, *args):
        super(ConsoleViewer, self).__init__(*args)

        self._locals = {'self': self}
        self._follow = not self.get('follow', default=True)

        self.__ui__()
        self.follow_action()

        self.app.console.output.changed.connect(self._changed)

        print("Python %s" % sys.version)

    def __ui__(self):
        """Build UI"""

        self._ui_output = TextEdit()
        self._ui_output.setObjectName("ConsoleViewer_text")
        self._ui_output.setAcceptRichText(False)
        self._ui_output.setReadOnly(True)
        self._ui_output.setTextInteractionFlags(self._ui_output.textInteractionFlags() | Qt.TextSelectableByKeyboard)

        font = QFont()
        font.setFamily("Courier")
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(10)

        self._ui_input = TextEdit()
        self._ui_input.setPlaceholderText("Enter Python code")
        self._ui_input.setObjectName("ConsoleViewer_text")
        self._ui_input.setFont(font)
        self._ui_input.setAcceptRichText(False)
        self._ui_input.keyPressEvent = self._key_pressed
        self._ui_input.setTabStopWidth(4 * QFontMetrics(font).width(' '))

        self._ui_input_highlight = PythonHighlighter(self._ui_input.document())

        self._ui_splitter = Splitter(Qt.Vertical)
        self._ui_splitter.setHandleWidth(2)
        self._ui_splitter.addWidget(self._ui_output)
        self._ui_splitter.addWidget(self._ui_input)

        size = self._ui_splitter.height()
        self._ui_splitter.setSizes([size * 0.8, size * 0.2])
        self._ui_splitter.setCollapsible(0, False)

        self._ui_label = Label("Console")
        self._ui_label.setObjectName("ConsoleViewer_label")
        self._ui_label.setAlignment(Qt.AlignCenter)
        self._ui_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._ui_view_action = QToolButton()
        self._ui_view_action.setText("View")
        self._ui_view_action.setIcon(Icon(':/rc/menu.png'))
        self._ui_view_action.clicked.connect(self.view_action)

        self._ui_follow_action = QToolButton()
        self._ui_follow_action.setText("Enter")
        self._ui_follow_action.setIcon(Icon(':/rc/at.png'))
        self._ui_follow_action.clicked.connect(self.follow_action)

        self._ui_run_action = QToolButton()
        self._ui_run_action.setText("Run")
        self._ui_run_action.setIcon(Icon(':/rc/play.png'))
        self._ui_run_action.clicked.connect(self.run_action)

        self._ui_toolbar = Toolbar()
        self._ui_toolbar.setObjectName("ConsoleViewer_toolbar")
        self._ui_toolbar.addWidget(self._ui_view_action)
        self._ui_toolbar.addWidget(self._ui_label)
        self._ui_toolbar.addWidget(self._ui_follow_action)
        self._ui_toolbar.addWidget(self._ui_run_action)

        self._ui_layout = VLayout()
        self._ui_layout.addWidget(self._ui_splitter)
        self._ui_layout.addWidget(self._ui_toolbar)

        self.setLayout(self._ui_layout)

    def view_action(self):
        """Replace current view with something other"""

        self.show_menu(self._ui_view_action.pos(), self._ui_toolbar)

    def run_action(self):
        """Execute text as python code"""

        try:
            code = str(self._ui_input.toPlainText())
            print('>>', code)

            try:
                value = eval(code, globals(), self._locals)

                print('->', value)
            except:
                exec(code, globals(), self._locals)

            self._ui_input.setPlainText("")
        except Exception as e:
            stack = traceback.extract_stack()[:-3] + traceback.extract_tb(e.__traceback__)
            pretty = traceback.format_list(stack)

            print(''.join(pretty) + '\n  {} {}'.format(e.__class__, e))

    def follow_action(self):
        """Execute on enter press"""

        self._follow = not self._follow

        # store property
        self.set('follow', self._follow)

        if self._follow:
            self._ui_follow_action.setIcon(Icon.colored(':/rc/at.png', QColor('#aeca4b'), QColor('#e3e3e3')))
        else:
            self._ui_follow_action.setIcon(Icon(':/rc/at.png'))

    def _changed(self):
        """Console output changed"""

        self._ui_output.setPlainText(self.app.console.output.read())
        scrollbar = self._ui_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _key_pressed(self, event):
        """Process key event on  console input"""

        if (event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return) and self._follow:
            self.run_action()
        else:
            QTextEdit.keyPressEvent(self._ui_input, event)
