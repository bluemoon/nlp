import cPickle
import os
__all__ = ["memoize"]

cachedir = "pickles/"
if not os.path.exists(cachedir): os.mkdir(cachedir)

def persistent_memoize(func, limit=None):
    if isinstance(func, int):
        def memoize_wrapper(f):
            return memoize(f, func)

        return memoize_wrapper
    
    file = os.path.join(cachedir, "%s.pickle" % func.func_name)
    
    def memoize_wrapper(*args, **kwargs):
        key = cPickle.dumps((args, kwargs))
        
        if os.path.exists(file):
            f = open(file)
            c = cPickle.load(f)
            f.close()
        else:
            c = {}
            
        if c.has_key(key):
            return c[key]
        else:
            c[key] = func(*args, **kwargs)
            ## pickle to disk
            f = open(file, 'w')
            cPickle.dump(c, f)
            f.close()
            ## then return
            return c[key]
        
    return memoize_wrapper

def memoize(function, limit=None):
    if isinstance(function, int):
        def memoize_wrapper(f):
            return memoize(f, function)

        return memoize_wrapper

    dict = {}
    list = []
    def memoize_wrapper(*args, **kwargs):
        key = cPickle.dumps((args, kwargs))
        try:
            list.append(list.pop(list.index(key)))
        except ValueError:
            dict[key] = function(*args, **kwargs)
            list.append(key)
            if limit is not None and len(list) > limit:
                del dict[list.pop(0)]

        return dict[key]

    memoize_wrapper._memoize_dict = dict
    memoize_wrapper._memoize_list = list
    memoize_wrapper._memoize_limit = limit
    memoize_wrapper._memoize_origfunc = function
    memoize_wrapper.func_name = function.func_name
    return memoize_wrapper
