
def Error(fsm):
    #print 'That does not compute.',
    #print fsm.state_changes
    pass
    
def Period(fsm):
    #print str(fsm.memory.pop())
    #print 'period(%d)' % (fsm.counter)
    return ['period', fsm.counter]

def Root(fsm):
    fsm.counter = fsm.counter - 1
    
def Declarative(fsm):
    return ['declarative', fsm.counter, fsm.counter+1]

def Subject(fsm):
    return ['subject', fsm.counter, fsm.counter+1]

def Object(fsm):
    return ['object', fsm.counter, fsm.counter+1]

