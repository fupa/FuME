#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os
import sys

from PyQt5 import QtCore


class ChromeDriverProcessor(QtCore.QThread):
    loggerSignal = QtCore.pyqtSignal(str)
    statusBarSignal = QtCore.pyqtSignal(str)

    def __init__(self, options):
        super(ChromeDriverProcessor, self).__init__(options['parent'])

    # def __del__(self):
    #     self.wait()

    def isFrozen(self):
        if getattr(sys, 'frozen', False):
            return True
        else:
            return False

    def subprocess_args(self, include_stdout=True):
        # adapted: https://github.com/pyinstaller/pyinstaller/wiki/Recipe-subprocess
        # Avoiding "[Error 6] the handle is invalid." in Windows
        #
        # Create a set of arguments which make a ``subprocess.Popen`` (and
        # variants) call work with or without Pyinstaller, ``--noconsole`` or
        # not, on Windows and Linux. Typical use::
        #
        #   subprocess.call(['program_to_run', 'arg_1'], **subprocess_args())
        #
        # When calling ``check_output``::
        #
        #   subprocess.check_output(['program_to_run', 'arg_1'],
        #                           **subprocess_args(False))
        #
        #
        shell = False

        # The following is true only on Windows.
        if hasattr(subprocess, 'STARTUPINFO'):
            # On Windows, subprocess calls will pop up a command window by default
            # when run from Pyinstaller with the ``--noconsole`` option. Avoid this
            # distraction.
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # Windows doesn't search the path by default. Pass it an environment so
            # it will.
            env = os.environ

            if not self.isFrozen():
                # TODO WinError 193
                # Running FuME on windows from bash, Python wants the shell=True arg
                # If it's set to False this warning appears
                # > [WinError 193] %1 is not a valid Win32 application <
                # There are some solutions online but simplest is set shell=True if
                # someone runs his FuME on Windows Bash. We cannot set this to True for every situation because
                # subprocess.Popen starts the chromedriver as a childprocess which is hard to kill/terminate.
                # This is not needed for macOS or .exe
                # Maybe this will be fixed later...
                shell = True
                print("shell is set to true, please kill chromedriver after closing FuME")
        else:
            si = None
            env = None

        # ``subprocess.check_output`` doesn't allow specifying ``stdout``::
        #
        #   Traceback (most recent call last):
        #     File "test_subprocess.py", line 58, in <module>
        #       **subprocess_args(stdout=None))
        #     File "C:\Python27\lib\subprocess.py", line 567, in check_output
        #       raise ValueError('stdout argument not allowed, it will be overridden.')
        #   ValueError: stdout argument not allowed, it will be overridden.
        #
        # So, add it only if it's needed.
        if include_stdout:
            ret = {'stdout': subprocess.PIPE}
        else:
            ret = {}

        # On Windows, running this from the binary produced by Pyinstaller
        # with the ``--noconsole`` option requires redirecting everything
        # (stdin, stdout, stderr) to avoid an OSError exception
        # "[Error 6] the handle is invalid."
        ret.update({'stdin': subprocess.PIPE,
                    'stderr': subprocess.PIPE,
                    'startupinfo': si,
                    'shell': shell,
                    'env': env})
        return ret

    def get_pathToTemp(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def quit(self):
        self.process.terminate()

    def run(self):
        cdpath = self.get_pathToTemp("chromedriver")

        try:
            self.process = subprocess.Popen([cdpath, '--port=9515', '--silent'], **self.subprocess_args(True))
            self.process.wait()
            # process does not wait if an error occured (e.g. port not available..)
        except Exception as e:
            self.loggerSignal.emit("Chrome Connection failed:\n" + str(e))

        self.loggerSignal.emit("ChromeDriver connection failed")
