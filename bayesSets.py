import numpy as np
im
class bayesSets():
    def __init__(self):
        """
        Basic class for BS modeling

        """
        self.hyperParams = None
        self.binarizedData = None
        pass

    def loadBinarizedData(self, binData):
        self.binarizedData = binData
        pass

    def setHyperParams(self, c=2):
        self.alpha = c*np.mean(self.binarizedData, axis=1)
        self.beta = c - self.alpha
        pass


    def evaluateModel(self):
        pass

if __name__ == "__main__":
    bs = bayesSets()
    bs.loadBinarizedData(someFile)




