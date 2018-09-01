import numpy as np
import graphviz
from sklearn import tree

#Features array.
lorenzo = []
#Labels array.
targets = [0]*30 + [1]*30 + [2]*30 + [3]*30
activities = ['walking.txt','shuffling.txt','UpDown.txt','Idle.txt']

#Reading in data from text files to appropriate array format.
for activity in activities:
    f = open(activity, 'r')
    for line in f.read().splitlines():
        y = [float(value.strip()) for value in line.split(",")]
        lorenzo.append(y)
    f.close()

lorenzo = np.asarray(lorenzo)
targets = np.asarray(targets)

print ("\n")
print lorenzo
print ("\n")
print len(lorenzo)
print ("\n")
print targets
print ("\n")
print len(targets)
print ("\n")

#Choosing some data samples to test on. These won't be included in the training set.
test_idx = [0,30,60,90]

#Removing the testing samples fromt the training set.
train_target = np.delete(targets, test_idx)
train_data = np.delete(lorenzo, test_idx, axis=0)

test_target = targets[test_idx]
test_data = lorenzo[test_idx]

#Creating and training the decision tree.
clf = tree.DecisionTreeClassifier()
clf.fit(train_data, train_target)

#If these two print statements match then the tree is doing good things.
print test_target
print clf.predict(test_data)

#Exporting the tree to its visual representation.
featureNames = ['AccelXAv','AngVZAv','FEnergy']
targetNames = ['Walking','Shuffling','UpDown','Idle']
dot_data = tree.export_graphviz(clf, out_file=None,
                                feature_names=featureNames,
                                class_names=targetNames,
                                filled=True, rounded=True,
                                special_characters=True)
graph = graphviz.Source(dot_data)
graph.render("Lorenzo's Aceleration Data")
