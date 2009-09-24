from sentence import sentence
from lg_test import irc_logParser
from grammar_fsm import Semantics

from rule_engine import rule_engine
from rule_engine import test_rules

from debug import *
import linkGrammar

def main():
    semantics = Semantics()
    
    logParser = irc_logParser()

    log_data = logParser.loadLogs('logs/2009-08-1*', limit=200)
    for sentences in log_data:
        rule_eng  = rule_engine()
        if not sentences:
            continue

        s = linkGrammar.sentence(sentences)
        if s:
            container = sentence(s)
            container.atom = semantics.semanticsToAtoms(container)
            
            debug(container)
            test_rules(container)
            
            
            
        
if __name__ == '__main__':
    main()
