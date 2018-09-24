import os

import numpy as np
from keras.models import Sequential
from keras.models import load_model


class NeuralNetworkLogic(object):

    def __init__(self, path_to_model):
        self._neural_network_model = load_model(path_to_model)

        self._featuresForDecision = np.zeros(242)
        self.trafficMemory = np.zeros(30)
        self.representationsMemory = np.zeros(30)
        self.lastDecision = 0
        self.decisionMemory = np.zeros(30)
        self.timeMemory = 0
        self._featureLength = 0

    def calculatefeature(self, segment, timeNow, bufferLevelSegments, buffer_level, traffictrace, timeSinceLastSwitchList, segments, decisionSegment):

        # 1-30: Observed Throughput !
        self._featuresForDecision[1:30] = self.trafficMemory[1:30]  # 1-29

        if segment == 0:
            self._featuresForDecision[30] = traffictrace[0]
            decisionSegment = 0
            self.timeMemory = timeNow
            self._featureLength = segments.shape[0]-30
        else:
            self._featuresForDecision[30] = decisionSegment/(timeNow-self.timeMemory)
            self.timeMemory = timeNow

        #Shift traffic memory
        self.trafficMemory[0:30] = self._featuresForDecision[1:31]

        # 0: Average Throughput !
        self._featuresForDecision[0] = np.mean(self._featuresForDecision[1:31])

        # 31- 60 Selected Quality !
        self._featuresForDecision[31:60] = self.decisionMemory[1:30]

        if segment == 0:
            self._featuresForDecision[60] = 0
            self.decisionMemory[0:29] = self.decisionMemory[1:30]
            self.decisionMemory[29] = 0
        else:
            self._featuresForDecision[60] = ((self.lastDecision+1) * 0.2)
            self.decisionMemory[0:29] = self.decisionMemory[1:30]
            self.decisionMemory[29] = ((self.lastDecision + 1) * 0.2)

        # 61 - 90 Selected Representations !
        self._featuresForDecision[61:90] = self.representationsMemory[1:30]
        self._featuresForDecision[90] = decisionSegment

        self.representationsMemory[0:29] = self.representationsMemory[1:30]
        self.representationsMemory[29] = decisionSegment

        #  64-213  Next 150 Future Represenations
        if segment < self._featureLength:
            self._featuresForDecision[91:237:5] = segments[segment:segment + 30, 0]
            self._featuresForDecision[92:238:5] = segments[segment:segment + 30, 1]
            self._featuresForDecision[93:239:5] = segments[segment:segment + 30, 2]
            self._featuresForDecision[94:240:5] = segments[segment:segment + 30, 3]
            self._featuresForDecision[95:241:5] = segments[segment:segment + 30, 4]
        else:
            tempSegments = np.zeros([segments.shape[0] + 60, 5])
            tempSegments[0:segments.shape[0], :] = segments

            self._featuresForDecision[91:237:5] = tempSegments[segment:segment + 30, 0]
            self._featuresForDecision[92:238:5] = tempSegments[segment:segment + 30, 1]
            self._featuresForDecision[93:239:5] = tempSegments[segment:segment + 30, 2]
            self._featuresForDecision[94:240:5] = tempSegments[segment:segment + 30, 3]
            self._featuresForDecision[95:241:5] = tempSegments[segment:segment + 30, 4]

        # 224 Buffer Level !
        self._featuresForDecision[241] = bufferLevelSegments/20

    def decide(self, segment):

        bufferDelay = 0

        features = np.reshape(self._featuresForDecision, (1, 242))

        self.lastDecision = int(self._neural_network_model.predict_classes(features))
        return int(self._neural_network_model.predict_classes(features)), bufferDelay #
