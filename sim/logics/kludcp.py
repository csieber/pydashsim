import numpy as np



class KLUDCPLogic(object):

    def __init__(self, maxBufferLevel):
        self._maxBufferLevel = maxBufferLevel
        self._timeMemory = 0
        self._decisionBandwidth = 0

        self._averageBitrateQ1 = 0
        self._averageBitrateQ2 = 0
        self._averageBitrateQ3 = 0
        self._averageBitrateQ4 = 0
        self._averageBitrateQ5 = 0


    def calculatefeature(self, segment, timeNow, bufferLevelSegments, bufferlevel, traffictrace, timeSinceLastSwitchList, segments, decisionSegment):

        bandwidth = 0
        if segment == 0:
            bandwidth = traffictrace[0]
            self._timeMemory = timeNow

            self._averageBitrateQ1 = np.mean(segments[:, 0])
            self._averageBitrateQ2 = np.mean(segments[:, 1])
            self._averageBitrateQ3 = np.mean(segments[:, 2])
            self._averageBitrateQ4 = np.mean(segments[:, 3])
            self._averageBitrateQ5 = np.mean(segments[:, 4])
        else:
            bandwidth = decisionSegment/(timeNow-self._timeMemory)
            self._timeMemory = timeNow


        bufferRatio = bufferlevel/self._maxBufferLevel

        if bufferRatio >= 0.5:
            self._decisionBandwidth = bandwidth*(1+0.5*bufferRatio)
        elif 0.35 <= bufferRatio < 0.5:
            self._decisionBandwidth = bandwidth
        elif 0.15 <= bufferRatio < 0.35:
            self._decisionBandwidth = bandwidth*0.5
        elif 0.0 <= bufferRatio < 0.15:
            self._decisionBandwidth = bandwidth * 0.3


    def decide(self, segment):
        bufferDelay = 0

        if self._decisionBandwidth < self._averageBitrateQ2:
            decision = 0
        elif self._averageBitrateQ2 <= self._decisionBandwidth < self._averageBitrateQ3:
            decision = 1
        elif self._averageBitrateQ3 <= self._decisionBandwidth < self._averageBitrateQ4:
            decision = 2
        elif self._averageBitrateQ4 <= self._decisionBandwidth < self._averageBitrateQ5:
            decision = 3
        elif self._averageBitrateQ5 <= self._decisionBandwidth:
            decision = 4

        return int(decision), 0
