from optparse import OptionParser
from containers import sentence
from lg_test import irc_logParser

from grammar_fsm import Semantics
from rule_engine import rule_engine
from rule_engine import test_rules


from debug import *
import linkGrammar
import analysis
import relex
import pprint

class main:
    def option_parser(self):
        self.parser = OptionParser()
        self.parser.add_option("-r", action="store_true", dest="relex")
        self.parser.add_option("--default", action="store_true", dest="default")
        (self.options, self.args) = self.parser.parse_args()

    def main(self):
        semantics = Semantics()
        
        logParser = irc_logParser()
        log_data = logParser.loadLogs('logs/2009-08-1*', limit=200)
        
        for sentences in log_data:
            rule_eng  = rule_engine()
            if not sentences:
                continue

            if self.options.relex:
                r = relex.relex()
                sentence = r.process(sentences)

                for x in sentence:
                    y = x.split('\n')
                    for z in y:
                        if z:
                            print z
                    
            if self.options.default:

                from tagger import braubt_tagger
                analogy = analysis.Analogies()
                
                s = linkGrammar.sentence(sentences)
                if s:
                    normal_words = sentences.split(' ')
                    container = sentence(s, normal_words)
                    container.atom = semantics.semanticsToAtoms(container)

                    test_rules(container)
                    for a in container.diagram:
                        debug(a)

                    analogy.similar(container)

        
if __name__ == '__main__':
    m = main()
    m.option_parser()
    m.main()
