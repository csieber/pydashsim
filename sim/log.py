# -*- coding: utf-8 -*-

import os
import csv


class LogWriter(object):
    def __init__(self, parent, writer):

        self._parent = parent
        self._writer = writer

    def write(self, row):

        ret = None

        try:
            ret = self._writer.writerow(row)
        except ValueError:
            print("Couldn't write row: %s" % row)

        return ret


class LogDir(object):
    def __init__(self, folder):
        self._folder = folder
        self._files = {}
        self._writer = {}

        os.makedirs(folder, exist_ok=True)

    def new(self, name, header):
        assert (not name in self._writer)

        self._files[name] = open(os.path.join(self._folder, '%s.csv' % name),
                                 mode='wt',
                                 encoding='utf-8',
                                 newline='')
        self._writer[name] = csv.DictWriter(self._files[name],
                                            fieldnames=header,
                                            extrasaction='ignore')

        self._writer[name].writeheader()

        return LogWriter(self, self._writer[name])

    def writer(self, name):
        assert (name in self._writer)

        return LogWriter(self, self._writer[name])

    def close(self):
        for n, f in self._files.items():
            f.close()

        self._writer = {}
        self._files = {}