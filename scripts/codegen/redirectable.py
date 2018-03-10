# Copyright (c) 2018 Bobby Noelte.
#
# SPDX-License-Identifier: Apache-2.0


class RedirectableMixin(object):
    __slots__ = []

    def setOutput(self, stdout=None, stderr=None):
        """ Assign new files for standard out and/or standard error.
        """
        if stdout:
            self._stdout = stdout
        if stderr:
            self._stderr = stderr

    def prout(self, s, end="\n"):
        print(s, file=self._stdout, end=end)

    def prerr(self, s, end="\n"):
        print(s, file=self._stderr, end=end)
