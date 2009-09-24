class tag:
    left  = None
    right = None
    tag   = None
    
    def __init__(self, left, right, tag):
        self.left = left
        self.right = right
        self.tag = tag
        
class sentence:
    words        = None
    spans        = None
    p_tags       = None
    tags         = None
    sub_links    = None
    atom         = None
    pos          = None
    tag_set      = None
    constituents = None
    
    def __init__(self, sentence):
        self.words      = sentence[0]
        self.spans      = sentence[1]
        self.p_tags     = sentence[2]
        self.tags       = sentence[3]
        self.sub_links  = sentence[4]
        self.tag_set    = []
        
    def __repr__(self):
        return '<sentence %s>' % (self.words)
