import random 
from sklearn.ensemble import RandomForestClassifier

class Model:
    """Abstraction for gibberish model. Two methods: fit and predict."""    
    ntrees = 500
    version = 0

    def __init__(self, X, y):
        """Get data and fit model."""
        self.clf = RandomForestClassifier(n_estimators=self.ntrees)
        self.clf = self.clf.fit(X, y)
        self.version = 0
        

    def fit(self, X, y):
        """Updates model with data X, y."""
        print("Refitting model")
        self.clf = self.clf.fit(X, y)
#       print("updating model from " + str(self.version) + " to " + str(self.verison+1) + ".")
        self.version += 1

    def predict(self, X):
        """Predict classification for X"""
        prediction = self.clf.predict(X)
        print("using version " + str(self.version))
        return(prediction)
        

