#include "Python.h"
#include <locale.h>
#include "link-includes.h"


static PyObject *sentence(PyObject *self, PyObject *args){
    Dictionary    dict;
    Parse_Options opts;
    Sentence      sent;
    Linkage       linkage;
    //CNode *       cn;

    /// Link counts
    int   num_linkages;
    int   links;

    ///  Index's for the iterators
    int   link_idx;
    int   word_idx;
    long   span;
    int   num_words;
    int   sub_linkages;

    const char *text;
    const char *d_output;

    PyObject *output_list;
    PyObject *word_list;
    PyObject *word2_list;
    PyObject *span_list;
    PyObject *temp;

    output_list = PyList_New(0);
    word_list   = PyList_New(0);
    word2_list  = PyList_New(0);

    span_list = PyList_New(0);

    if (!PyArg_ParseTuple(args, "s", &text))
        return NULL;

    opts = parse_options_create();
    parse_options_set_verbosity(opts, -1);

    setlocale(LC_ALL, "");
    dict = dictionary_create_default_lang();

    if (!dict) {
        PyErr_SetString(PyExc_RuntimeError, "Fatal error: Unable to open the dictionary");
        Py_INCREF(Py_None);
        return Py_None;
    }
    
    sent = sentence_create(text, dict);
    sentence_split(sent, opts);
    num_linkages = sentence_parse(sent, opts);

    if (num_linkages > 0) {
            linkage = linkage_create(0, sent, opts);
            
            num_words = linkage_get_num_words(linkage);
            sub_linkages = linkage_get_num_sublinkages(linkage);
            links = linkage_get_num_links(linkage);

            for(link_idx=0; link_idx < links; link_idx++){
                span = linkage_get_link_length(linkage, link_idx);
                PyList_Append(span_list, PyInt_FromLong(span));
                
                PyObject *temp_list;
                temp_list = PyList_New(0);
                
                const char *t1 = linkage_get_link_llabel(linkage, link_idx);
                temp = PyString_FromString(t1);
                PyList_Append(temp_list, temp);
                //PyList_Append(output_list, temp);

                const char *t2 = linkage_get_link_rlabel(linkage, link_idx);
                temp = PyString_FromString(t2);
                PyList_Append(temp_list, temp);

                PyList_Append(output_list, temp_list);
                
                const char *t3 = linkage_get_link_label(linkage, link_idx);
                temp = PyString_FromString(t3);
                PyList_Append(word2_list, temp);
            }
            
            for(word_idx=0; word_idx < num_words; word_idx++){
                d_output = linkage_get_word(linkage, word_idx);
                PyObject *word;

                word = PyString_FromString(d_output);
                PyList_Append(word_list, word);
            }

            linkage_delete(linkage);

     } else{
        sentence_delete(sent);
        dictionary_delete(dict);
        parse_options_delete(opts);
 
        Py_INCREF(Py_None);
        return Py_None;
    }

    sentence_delete(sent);
    dictionary_delete(dict);
    parse_options_delete(opts);

    return Py_BuildValue("SSSS", word_list, span_list, output_list, word2_list);
} 

struct CNode_s {
  const char  * label;
  CNode * child;
  CNode * next;
  int   start, end;
};

PyObject *build_tree(CNode *n, Linkage linkage){
    CNode * m;
    int word_num = 1;
    PyObject *output;
    PyObject *temp;

    //PyObject *t2;
    //PyObject *t1;
    output = PyList_New(0);
    // sentence_get_word(Sentence sent, int wordnum)
    //static char * spacer=" ";

    if (n == NULL){
        Py_INCREF(Py_None);
        return Py_None;
    }
    for (m=n->child; m!=NULL; m=m->next) {
        //PyObject *t1;
        //t1 = PyList_New(0);
        if (m->child == NULL) {
            temp = PyString_FromString(m->label);
            //PyList_Append(t1, temp);
        }
        else {
            temp = build_tree(m, linkage);
            //PyList_Append(t1, temp);
        }
        /*PyObject *temp_list;
        PyObject *temp2_list;
        temp_list = PyList_New(0);
        temp2_list = PyList_New(0);

        const char *t3 = linkage_get_link_llabel(linkage, word_num);
        const char *t4 = linkage_get_link_rlabel(linkage, word_num);
        
        t1 = PyString_FromString(t3);
        t2 = PyString_FromString(t4);
        PyList_Append(temp_list, t1);
        PyList_Append(temp_list, t2);
        PyList_Append(temp2_list, temp);
        PyList_Append(temp2_list, temp_list);
        //PyDict_SetItem(output, temp, t2);
        PyList_Append(output, temp2_list);
        */
        PyList_Append(output, temp);
        word_num++;
    }
    Py_XINCREF(output);
    return output;
}

static PyObject *constituents(PyObject *self, PyObject *args){
    Dictionary    dict;
    Parse_Options opts;
    Sentence      sent;
    Linkage       linkage;
    CNode *       cn;

    /// Link counts
    int   num_linkages;


    const char *text;

    PyObject *output_list;

    if (!PyArg_ParseTuple(args, "s", &text))
        return NULL;

    opts = parse_options_create();
    parse_options_set_verbosity(opts, -1);

    setlocale(LC_ALL, "");
    dict = dictionary_create_default_lang();

    if (!dict) {
        PyErr_SetString(PyExc_RuntimeError, "Fatal error: Unable to open the dictionary");
        Py_INCREF(Py_None);
        return Py_None;
    }
    
    sent = sentence_create(text, dict);
    sentence_split(sent, opts);
    num_linkages = sentence_parse(sent, opts);

    if (num_linkages > 0) {
             linkage = linkage_create(0, sent, opts);
            
             cn = linkage_constituent_tree(linkage);
             output_list = build_tree(cn, linkage);
             if(output_list == Py_None){
                Py_INCREF(output_list);
                return output_list;
             }
             linkage_free_constituent_tree(cn);

             linkage_delete(linkage);
     } else{
        sentence_delete(sent);
        dictionary_delete(dict);
        parse_options_delete(opts);

        Py_INCREF(Py_None);
        return Py_None;
    }
    sentence_delete(sent);
    dictionary_delete(dict);
    parse_options_delete(opts);

    return Py_BuildValue("S", output_list);
} 
static PyObject *domains(PyObject *self, PyObject *args){
    Dictionary    dict;
    Parse_Options opts;
    Sentence      sent;
    Linkage       linkage;
    //CNode *       cn;

    /// Link counts
    int   num_linkages;
    int   links;
    int   i;
    int   j = 0;
    int num_domains;
    const char *text;

    PyObject *output_list;
    PyObject *temp;
    output_list = PyList_New(0);

    if (!PyArg_ParseTuple(args, "s", &text))
        return NULL;

    opts = parse_options_create();
    parse_options_set_verbosity(opts, -1);

    setlocale(LC_ALL, "");
    dict = dictionary_create_default_lang();

    if (!dict) {
        PyErr_SetString(PyExc_RuntimeError, "Fatal error: Unable to open the dictionary");
        Py_INCREF(Py_None);
        return Py_None;
    }
    
    sent = sentence_create(text, dict);
    sentence_split(sent, opts);
    num_linkages = sentence_parse(sent, opts);

    if (num_linkages > 0) {
             linkage = linkage_create(0, sent, opts);
             links = linkage_get_num_sublinkages(linkage);
             for(i=0; i<=links; i++){
                num_domains = linkage_get_link_num_domains(linkage, i);
                const char **temp1 = linkage_get_link_domain_names(linkage, i);
                //for(j=0; j<=num_domains; j++){
                while(num_domains < j){ 
                    temp = PyString_FromString(temp1[j]);
                    PyList_Append(output_list, temp);
                    j++;
                }
                j = 0;
             }
             linkage_delete(linkage);
     } else{
        sentence_delete(sent);
        dictionary_delete(dict);
        parse_options_delete(opts);
        Py_INCREF(Py_None);
        return Py_None;
    }
    sentence_delete(sent);
    dictionary_delete(dict);
    parse_options_delete(opts);

    return Py_BuildValue("Si", output_list, num_domains);
} 

PyMethodDef methods[] = {
    {"sentence", sentence, METH_VARARGS, ""},
    {"constituents", constituents, METH_VARARGS, ""},
    {"domains", domains, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL},
};

PyMODINIT_FUNC initlinkGrammar(void){
    (void) Py_InitModule("linkGrammar", methods);



}
