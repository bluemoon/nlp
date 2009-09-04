
def Error(fsm):
    #print 'That does not compute.',
    #print fsm.state_changes
    pass
    
def Period(fsm):
    #print str(fsm.memory.pop())
    print 'period(%d)' % (fsm.counter)

def Root(fsm):
    fsm.counter = fsm.counter - 1
    
def Declarative(fsm):
    print 'declarative(%d, %d)' % (fsm.counter, fsm.counter+1)
    
def Subject(fsm):
    print 'subject(%d, %d)' % (fsm.counter, fsm.counter+1)

def Object(fsm):
    print 'object(%d, %d)' % (fsm.counter, fsm.counter+1)

