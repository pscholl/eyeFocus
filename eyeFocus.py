#!/usr/bin/env python3

from gi.repository import i3ipc

from sklearn.cross_validation import StratifiedShuffleSplit
from sklearn import svm, neighbors
from numpy import array, mean, save
from datetime import datetime, timedelta
from collections import Counter
import sys, gaze, focus, atexit

i3  = i3ipc.Connection()
i3f = focus.I3Focus(i3)
eye = gaze.Connection()

class EyeFocus(object):
    def __init__(self, i3focus, eyetrack):
        eyetrack.on('change', self.on_gaze)
        self.i3f = i3focus
        self.last_focus = None
        #self.classifier = svm.SVC()
        self.classifier = neighbors.KNeighborsClassifier()
        self.not_trained = True
        self.predictions = []

    def on_gaze(self, lx,ly,rx,ry,w,h):
        focus = self.i3f.current_focus
        if focus is None: return

        #features = (lx,ly,rx,ry,w,h)
        #features = (rx,ry,w)
        features = (rx/w, ry/w)

        since = datetime.now() - focus.focused_since

        if self.last_focus != focus and self.last_focus != None:
            self.train()

        elif since > timedelta(seconds=4) and self.not_trained:
            # looked at the same window for 40 seconds
            #    => time to retrain our model <=
            self.train()
            self.not_trained = False

        elif since > timedelta(seconds=1) and since < timedelta(seconds=4):
            # looked at the same window for 20 seconds
            #    => time to get some ground truth <=
            focus.data.insert( 0, features )
            self.not_trained = True

            if len(focus.data) > 500:
                focus.data.pop()

            print ("training for " + str(focus));
            sys.stdout.write(".")

        else:
            # none of the above? let's predict and switch
            try:
                winid = self.classifier.predict( features )[0]
                print ("prediction:", winid)

                self.predictions.insert(0, winid)
                if len(self.predictions) > 25:
                    self.predictions.pop()

                winid = Counter(self.predictions).most_common(1)[0]
                winid = self.i3f[winid[0]].id

                i3.command( '[con_id="%s"] border normal' % focus.id )
                i3.command( '[con_id="%s"] border none' % winid )
            except Exception as e:
                print ("predict", e)
            pass

        self.last_focus = focus

    def train(self):
        try:
            y = array([ str(k) for k,v in self.i3f.items() for x in v.data ])
            X = array([ x for k,v in self.i3f.items() for x in v.data ])
            self.classifier.fit(X,y)
        except Exception as e:
            print(e)

    def ex_data(self):
        y = array([ str(k) for k,v in self.i3f.items() for x in v.data ])
        X = array([ x for k,v in self.i3f.items() for x in v.data ])
        save('X.npy', X)
        save('y.npy', y)

e=EyeFocus(i3f, eye)
atexit.register(e.ex_data)

i3.main()
