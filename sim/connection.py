import logging
import numpy as np


log = logging.getLogger(__name__)


class Connection(object):

    def __init__(self, env, tpattern):

        self._env = env
        self._tpattern = tpattern

        # Traffic volumne at each elapsed second
        self._tvolumne = np.append([0], tpattern.cumsum())

    def download(self, dlsize, delay):
        """
        Download a segment through the connection.

        :param dlsize: Segment size in Byte
        :param delay: Delay for download (TRDA)
        :return:
        """

        # Get theoretical maximum downloaded volumne until now
        nowdl = np.interp(self._env.now, range(len(self._tvolumne)), self._tvolumne)

        # Interpolate the time it takes for connection to download dlsize
        intptime = np.interp(nowdl + dlsize, self._tvolumne, range(len(self._tvolumne)))

        # Calculate download time for the segment
        dltime = intptime - self._env.now

        log.debug("%.3fs: Downloading %.3f Data starting from now will take %.3fs." % (self._env.now, dlsize, dltime))

        yield self._env.timeout(dltime+delay)

        log.debug("%.3fs: Downloading finished." % (self._env.now))

    def initialdelay(self, dlsize):
        """
        Schedules Playout after initial delay.

        :param dlsize: Segment size in Byte
        :return:
        """

        # Get theoretical maximum downloaded volumne until now
        nowdl = np.interp(0, range(len(self._tvolumne)), self._tvolumne)

        # Interpolate the time it takes for connection to download dlsize
        intptime = np.interp(nowdl + dlsize, self._tvolumne, range(len(self._tvolumne)))

        # Calculate download time for the segment
        #dltime = intptime - self._env.now
        dltime = 5
        yield self._env.timeout(dltime)


if __name__ == "__main__":

    RUN = '/home/sieber/Repositories/01_HASBRAIN/pydashsim/samples/00f69654-4087-4be9-b3ba-01d37a651139/'

    import os

    traffictrace = np.genfromtxt(os.path.join(RUN, 'traffictrace.csv'), skip_header=1)

    conn = Connection(None, traffictrace)

    conn.download(2)