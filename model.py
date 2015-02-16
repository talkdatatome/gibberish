import random 
from sklearn.ensemble import RandomForestClassifier

class Model:
    """Abstraction for gibberish model. Two methods: fit and predict."""    
    def __init__(self, X, y, ntrees=500):
        """Get data and fit model."""
        self.clf = RandomForestClassifier(n_estimators=ntrees)
        self.ntrees = ntrees
        self.clf = self.clf.fit(X, y)
        self.version = 0

    def fit(self, X, y):
        """Updates model with data X, y."""
        self.clf = RandomForestClassifier(n_estimators=self.ntrees)
        self.clf = self.clf.fit(X, y)
        print("updating model from " + str(self.version) + " to " + str(self.version + 1) + ".")
        self.version += 1
        return(self)

    def predict(self, X):
        """Predict classification for X"""
        prediction = self.clf.predict(X)
        print("using version " + str(self.version))
        return(prediction)
        
    def __repr__(self):
        return("<Model(version='%s')>" % (self.version))


