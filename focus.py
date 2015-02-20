from datetime import datetime
from pdb import set_trace

class FocusArea(object):
    def __repr__(self):
        return "_".join([str(self.__getattribute__(attr)) for attr in "x y w h".split()])

class I3Focus(dict):
    def __init__(self, i3):
        i3.on('window', self.on_focus)
        i3.on('output', self.on_output)

        self.current_focus = None

    def on_focus(self,con,ev):
        # we keep track of the currently focused window
        if ev == None or ev.change != 'focus':
            return # XXX what about size changes?

        r = ev.container.get_property('rect')
        i = ev.container.get_property('id')
        n = ev.container.get_property('name')
        w = ev.container.workspace.get_name()
        #o = [o for o in con.get_outputs() if o.current_workspace==w]

        #print (o,w)
        # set_trace()

        obj = FocusArea()
        obj.x,obj.y = r.x,r.y
        obj.w,obj.h = r.width, r.height
        obj.name,obj.id = n, i
        obj.data = []

        if obj.y != 0: obj.y-=18; obj.h+=18

        if str(obj) not in self:
            self[str(obj)] = obj
        else:
            obj = self[str(obj)]

        obj.focused_since  = datetime.now()
        self.current_focus = obj

    def on_output(self,con,ev):
        # gets called when the output configuration, i.e. available
        # monitors or relative layout changes.
        # We need to react to this by reloading what is currently
        # stored as focused areas in our dictionary
        # TODO
        o = sorted( [o for o in con.get_outputs() if o.active],
                    key = lambda o: o.name )

        tostr = lambda o: o.name + str(o.rect.x) + str(o.rect.y) +\
                          str(o.rect.width) + str(o.rect.height)

        key = "_".join([tostr(o) for o in o])
        pass
