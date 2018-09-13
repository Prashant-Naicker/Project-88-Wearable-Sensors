import numpy as np
import graphviz
from sklearn import tree

#Features array.
samples = []
#Labels array.
targets = [0]*120 + [1]*120 + [2]*120 + [3]*120
activities = ['Walking.txt','Shuffling.txt','UpDown.txt','Idle.txt']

#Reading in data from text files to appropriate array format.
for activity in activities:
    f = open(activity, 'r')
    for line in f.read().splitlines():
        y = [float(value.strip()) for value in line.split(",")]
        samples.append(y)
    f.close()

samples = np.asarray(samples)
targets = np.asarray(targets)

print ("\n")
print len(samples)

print ("\n")
print len(targets)


#Choosing some data samples to test on. These won't be included in the training set.
test_idx0 = [0,1,2,3,4,5,6,7,8,9,10,11,
            120,121,122,123,124,125,126,127,128,129,130,131,
            240,241,242,243,244,245,246,247,248,249,250,251,
            360,361,362,363,364,365,366,367,368,369,370,371]

test_idx1 = [x+24 for x in test_idx0]

print ("\n")
print test_idx0
print ("\n")
print test_idx1

#Removing the testing samples fromt the training set.
train_target = np.delete(targets, test_idx1)
train_data = np.delete(samples, test_idx1, axis=0)

test_target = targets[test_idx1]
test_data = samples[test_idx1]

#Creating and training the decision tree.
clf = tree.DecisionTreeClassifier()
clf.fit(train_data, train_target)

#If these two print statements match then the tree is doing good things.
print ("\n")
print test_target
print ("\n")
print clf.predict(test_data)
print ("\n")

#Exporting the tree to its visual representation.
featureNames = ['AccelXAv','AngVZAv','FEnergy']
targetNames = ['Walking','Shuffling','UpDown','Idle']
dot_data = tree.export_graphviz(clf, out_file=None,
                                feature_names=featureNames,
                                class_names=targetNames,
                                filled=True, rounded=True,
                                special_characters=True)
graph = graphviz.Source(dot_data)
graph.render("Tree")
