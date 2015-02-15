import random 
from sklearn.ensemble import RandomForestClassifier

class Model:
    """Abstraction for gibberish model. Two methods: fit and predict."""    
    ntrees = 500
    def __init__(self, X, y):
        """Get data and fit model."""
        self.clf = RandomForestClassifier(n_estimators=self.ntrees)
        self.clf = self.clf.fit(X, y)
        

    def fit(self, X, y):
        """Updates model with data X, y."""
        self.clf = self.clf.fit(X, y)

    def predict(self, X):
        """Predict classification for X"""
        prediction = self.clf.predict(X)
        return(prediction)
        

