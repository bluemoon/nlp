from distutils.core import setup, Extension
link_grammar = Extension("linkGrammar",
                         libraries = ['link-grammar'],
                         library_dirs = ['/usr/local/lib'],
                         include_dirs = ['/usr/local/include/link-grammar'],
                         sources=["lg_py.c"])

mm_hash = Extension("mm_hash", sources=['mm_hash.c'])

setup(name = "linkGrammar",
      version = "1.0",
      author = 'Alex Toney',
      ext_modules = [link_grammar, mm_hash]
      )
      
