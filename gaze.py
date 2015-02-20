from gi.repository.GLib import spawn_async, IOChannel, IO_IN, IO_HUP, PRIORITY_HIGH, SpawnFlags
from traceback import print_exception,print_tb
from sys import exc_info

class Connection():
    def __init__(self, callback = lambda x,y,face_ratio: None):
        # eyeTracker in line buffered mode
        self.params = ["stdbuf", "-oL", "build/bin/eyeLike"]

        # spawn child
        self.pid, self.stdin, self.stdout, self.stderr = spawn_async(
                self.params,
                working_directory = "../eyeLike",
                flags = SpawnFlags.SEARCH_PATH,
                standard_output = True)

        # add watch on stdout
        self.watch = IOChannel(self.stdout).add_watch(
                IO_HUP | IO_IN,
                self,
                priority = PRIORITY_HIGH)

        # store our callback
        self.callback = callback

    def on(self, event, callback):
        # provided for conformity
        self.callback = callback

    def __call__(self, io, condition):
        # called when gaze tracker prints a new line
        if condition is IO_IN:
            try:
                track = [float(x) for x in io.readline().split()]
                self.callback(*track)
            except Exception as e:
                print_exception(*exc_info())

            return True # more update please
        return False # no further updates please
