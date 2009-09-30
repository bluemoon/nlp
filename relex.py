import sys
from subprocess import Popen, PIPE
from memoize import persistent_memoize
RELEX_DIRECTORY = './'
RELEX_VM_OPTS = "-Xmx1024m -Djava.library.path=/usr/lib:/usr/local/lib"
RELEX_CLASSPATH = "-classpath \
bin:\
/home/bluemoon/Downloads/jwnl.jar:\
/usr/local/share/java/jwnl-1.4rc2.jar:\
/usr/local/share/java/jwnl-1.3.3.jar:\
/usr/local/share/java/opennlp-tools-1.4.3.jar:\
/usr/local/share/java/opennlp-tools-1.3.0.jar:\
/usr/local/share/java/maxent-2.5.2.jar:\
/usr/local/share/java/maxent-2.4.0.jar:\
/usr/local/share/java/trove.jar:\
/usr/local/share/java/linkgrammar.jar:\
/usr/share/java/linkgrammar-4.6.0.jar:\
/usr/share/java/commons-logging-1.1.1-SNAPSHOT.jar:\
/usr/share/java/gnu-getopt.jar:\
/usr/share/java/xercesImpl.jar:\
/opt/GATE-5.0/bin/gate.jar:\
/opt/GATE-5.0/lib/jdom.jar:\
/opt/GATE-5.0/lib/jasper-compiler-jdt.jar:\
/opt/GATE-5.0/lib/nekohtml-0.9.5.jar:\
/opt/GATE-5.0/lib/ontotext.jar:\
/opt/GATE-5.0/lib/stax-api-1.0.1.jar:\
/opt/GATE-5.0/lib/PDFBox-0.7.2.jar:\
/opt/GATE-5.0/lib/wstx-lgpl-2.0.6.jar"

class relex:
    @persistent_memoize
    def process(self, sentence):
        output = []
        command = 'java %s %s relex.RelationExtractor -n 4 -l -t -f -a -s "%s"' % (RELEX_VM_OPTS, RELEX_CLASSPATH, sentence)
        p = Popen(command, stdout=PIPE, stderr=open('/dev/null', 'w'), shell=True)
        while True:
            o = p.stdout.readline()
            output.append(o)
            if o == '' and p.poll() != None: break
        
        return output

    
