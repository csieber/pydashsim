import numpy as np



class TRDALogic(object):

    def __init__(self, bmin, blow, bhigh, alpha1, alpha2, alpha3, alpha4, alpha5, faststart = False):

        self._BMin = bmin
        self._BLow = blow
        self._BHigh = bhigh
        self._BOpt = (blow+bhigh)/2
        self._runningFastStart = faststart

        self._alpha1 = alpha1
        self._alpha2 = alpha2
        self._alpha3 = alpha3
        self._alpha4 = alpha4
        self._alpha5 = alpha5

        self._timeMemory = 0
        self._bufferLevelSeconds = 0
        self._preceedingBufferLevelSeconds = 0
        self._preceedingNextHigherSegment = 0
        self._decisionBandwidth = 0
        self._preceedingSegment = 0
        self._preceedingDecision = 0
        self._preceedingBandwidth = np.zeros(10)
        self._preceedingSegmentBitrate = 0

    def calculatefeature(self, segment, timeNow, bufferLevelSegments, bufferlevel, traffictrace, timeSinceLastSwitchList, segments, decisionSegment):

        if segment == 0:
            self._preceedingBandwidth[9] = traffictrace[0]
            self._decisionBandwidth = np.sum(self._preceedingBandwidth)/(segment+1)
            self._preceedingSegmentBitrate = traffictrace[0]
            self._timeMemory = timeNow

            self._preceedingNextHigherSegment = segments[0, 1]

        else:
            self._preceedingBandwidth[0:9] = self._preceedingBandwidth[1:10]
            self._preceedingBandwidth[9] = decisionSegment/(timeNow-self._timeMemory)
            if segment < 10:
                self._decisionBandwidth = np.sum(self._preceedingBandwidth)/(segment+1)
            else:
                self._decisionBandwidth = np.mean(self._preceedingBandwidth)
            self._preceedingSegmentBitrate = (decisionSegment*1)/(timeNow-self._timeMemory)
            self._timeMemory = timeNow

            if self._preceedingDecision < 4:
                self._preceedingNextHigherSegment = np.mean(segments[:, self._preceedingDecision+1])
            else:
                self._preceedingNextHigherSegment = np.mean(segments[:, self._preceedingDecision])

        self._preceedingSegment = decisionSegment

        self._preceedingBufferLevelSeconds = self._bufferLevelSeconds
        self._bufferLevelSeconds = bufferlevel

    def decide(self, segment):

        decision = self._preceedingDecision

        bufferDelay = 0

        if self._runningFastStart and self._preceedingDecision != 4 and self._preceedingBufferLevelSeconds <= self._bufferLevelSeconds\
                and self._preceedingSegment <= self._alpha1*self._decisionBandwidth:
            if self._bufferLevelSeconds < self._BMin:
                if self._preceedingNextHigherSegment <= self._alpha2*self._decisionBandwidth:
                    decision = self._preceedingDecision + 1
            elif self._bufferLevelSeconds < self._BLow:
                if self._preceedingNextHigherSegment <= self._alpha3 * self._decisionBandwidth:
                    decision = self._preceedingDecision + 1
            else:
                if self._preceedingNextHigherSegment <= self._alpha4 * self._decisionBandwidth:
                    decision = self._preceedingDecision + 1
                if self._bufferLevelSeconds > self._BHigh:
                    bufferDelay = self._bufferLevelSeconds - (self._BHigh - 1)

        else:
            self._runningFastStart = False

            if self._bufferLevelSeconds < self._BMin:
                decision = 0
            elif self._BMin <= self._bufferLevelSeconds < self._BLow:
                if self._preceedingDecision != 0 and self._preceedingSegment > self._preceedingSegmentBitrate:
                    decision = self._preceedingDecision-1
            elif self._BLow <= self._bufferLevelSeconds < self._BHigh:
                if self._preceedingDecision == 4 or self._preceedingNextHigherSegment >= self._alpha5 * self._decisionBandwidth:
                    if self._bufferLevelSeconds-1 > self._BOpt:
                        bufferDelay = 1
                    elif self._bufferLevelSeconds > self._BOpt:
                        bufferDelay = self._bufferLevelSeconds - self._BOpt
                    else:
                        bufferDelay = 0

            else:
                if self._preceedingDecision == 4 or self._preceedingNextHigherSegment >= self._alpha5 * self._decisionBandwidth:
                    if self._bufferLevelSeconds-1 > self._BOpt:
                        bufferDelay = 1
                    elif self._bufferLevelSeconds > self._BOpt:
                        bufferDelay = self._bufferLevelSeconds - self._BOpt
                    else:
                        bufferDelay = 0
                else:
                    decision = self._preceedingDecision+1

        self._timeMemory = self._timeMemory + bufferDelay

        self._preceedingDecision = decision

        return int(decision), bufferDelay
