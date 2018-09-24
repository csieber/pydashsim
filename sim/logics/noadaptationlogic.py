
class NoAdaptationLogic:

    def __init__(self, constant_ql=0):
        self._decision = constant_ql

    def calculatefeature(self, segment, timeNow, bufferLevelSegments, buffer_level, traffictrace,
                             timeSinceLastSwitchList, segments, decisionSegment):
        self.decision = self._decision

    def decide(self, _):
        return self._decision, 0