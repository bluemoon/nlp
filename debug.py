# -*- coding: utf-8 -*-
import inspect
import time
import pylab

TERM_GREEN   = "\033[1;32m"
TERM_ORANGE  = '\033[93m'
TERM_BLUE    = '\033[94m'
TERM_RED     = '\033[91m'
TERM_END     = "\033[1;m"

START_TIME = time.time()
DEBUG_CALL_LIST = []
DEBUG_PREFIX = u'[t:%.1f tΔ:%.3f line:%d]'

def debug(obj, prefix=None):    
    CALL_TIME = time.time()
    caller_module = inspect.stack()[1][1]
    caller_method = inspect.stack()[1][3]
    from_line     = inspect.stack()[1][2]
    time_delta    = 0.0
    function      = True


    d_time = CALL_TIME - START_TIME

    if caller_method == '<module>':
        caller_method = caller_module
        function = False

    if '/' in caller_module:
        caller_module = caller_module.split('/')[-1]
            
    #f_prefix = function == True and 'function' or 'module'
    f_formatting =  '%s--> [m:%s f:%s]%s'
    if len(DEBUG_CALL_LIST) >= 1:
        time_delta = time.time() - DEBUG_CALL_LIST[-1]['time']
        if DEBUG_CALL_LIST[-1]['method'] != caller_method:
            print f_formatting % (TERM_BLUE, caller_module, caller_method, TERM_END)
    else:
        print f_formatting % (TERM_BLUE, caller_module, caller_method, TERM_END)

        
    if not prefix:
        n_prefix = DEBUG_PREFIX + ': '
        print n_prefix % (d_time, time_delta,  from_line),
        #pprint.pprint(obj)
        print obj
    else:
        n_prefix = DEBUG_PREFIX + ' %s:'
        print n_prefix% (d_time, time_delta, from_line, prefix),
        #pprint.pprint(obj)
        print obj
        
    DEBUG_CALL_LIST.append({'method':caller_method, 'time':CALL_TIME})

def graphDebugTimes():
    callIterator = 0
    totalCalls   = []
    totalDelta   = []
    for x in DEBUG_CALL_LIST[1:]:
        currentDelta = x['time'] - DEBUG_CALL_LIST[callIterator]['time']
        if currentDelta >= 0.2:
            totalDelta.append(currentDelta)
            totalCalls.append(callIterator)
            callIterator += 1

    pylab.title('Calls vs. Delta time')
    pylab.xlabel('calls over 0.2s')
    pylab.ylabel('delta time (s)')

    pylab.plot(totalCalls, totalDelta)
    pylab.savefig('debug-time-callgraph')
