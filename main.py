from containers import sentence
from lg_test import irc_logParser

from grammar_fsm import Semantics
from rule_engine import rule_engine
from rule_engine import test_rules
from tagger      import braubt_tagger

from debug import *
import linkGrammar
import pprint

def main():
    semantics = Semantics()
    logParser = irc_logParser()
    log_data = logParser.loadLogs('logs/2009-08-1*', limit=200)
    #log_data = ['Alice looked at the cover of Shonen Jump.', 'She decided to buy it.']
    
    for sentences in log_data:
        rule_eng  = rule_engine()
        if not sentences:
            continue

        s = linkGrammar.sentence(sentences)
        if s:
            normal_words = sentences.split(' ')
            container = sentence(s, normal_words)
            container.atom = semantics.semanticsToAtoms(container)
            
            test_rules(container)
            for a in container.diagram:
                debug(a)
        
if __name__ == '__main__':
    main()
