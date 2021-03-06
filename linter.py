#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Alec Thomas
# Copyright (c) 2014 Alec Thomas
#
# License: MIT
#

"""This module exports the Gometalinter plugin class."""

import os
import shlex

from SublimeLinter.lint import Linter, highlight, util
from SublimeLinter.lint.persist import settings


class Gometalinter(Linter):
    """Provides an interface to gometalinter."""

    syntax = ('go', 'gosublime-go', 'gotools')
    cmd = 'gometalinter * .'
    regex = r'(?:[^:]+):(?P<line>\d+):(?P<col>\d+)?:(?:(?P<warning>warning)|(?P<error>error)):\s*(?P<message>.*)'
    error_stream = util.STREAM_BOTH
    default_type = highlight.ERROR

    def __init__(self, view, syntax):
        """Initialize and load GOPATH from settings if present."""
        Linter.__init__(self, view, syntax)

        gopath = self.get_view_settings().get('gopath')
        if gopath:
            if self.env:
                self.env['GOPATH'] = gopath
            else:
                self.env = {'GOPATH': gopath}
            print('sublimelinter: GOPATH={}'.format(self.env['GOPATH']))
        else:
            print('sublimelinter: using system GOPATH={}'.format(os.environ.get('GOPATH', '')))

    def run(self, cmd, code):
        if settings.get('lint_mode') == 'background':
            return self._live_lint(cmd, code)
        else:
            return self._in_place_lint(cmd)

    def _live_lint(self, cmd, code):
        print('gometalinter: linting {}'.format(self.filename))
        files = [f for f in os.listdir(os.path.dirname(self.filename)) if f.endswith('.go')]
        return self.tmpdir(cmd, files, code)

    def _in_place_lint(self, cmd):
        filename = os.path.basename(self.filename)
        cmd = cmd + ['-I', filename]
        print('gometalinter: linting {}: {}'.format(filename, ' '.join(map(shlex.quote, cmd))))
        out = util.communicate(cmd, output_stream=util.STREAM_STDOUT)
        return out or ''
