import re
import pickle
from suffix_trees import STree
from tqdm import tqdm

def findAll(lst, predicate):
    return [i for i in lst if predicate(i)]

def handleOverlap(spans):
    del_in = []
    for x in spans:
        if spans.index(x) in del_in: continue
        for y in spans:
            if spans.index(y) in del_in: continue
            if x == y: continue
            if len(set(list(range(x[0],x[1]+1))) & set(list(range(y[0],y[1]+1)))) > 0:
                if len(list(range(x[0],x[1]+1))) > len(list(range(y[0],y[1]+1))):
                    del_in.append(spans.index(y))
                    spans.pop(spans.index(y))
                elif len(list(range(y[0],y[1]+1))) > len(list(range(x[0],x[1]+1))):
                    del_in.append(spans.index(x))
                    spans.pop(spans.index(x))
    return spans

def findEntities(txt, kws):
    
    st = STree.STree(txt)
    spans = []
    
    for kw in kws:
        starts = st.find_all(kw)
        spans.extend([(item, item+len(kw)) for item in starts])
    
    bounds = handleOverlap(spans)
    
    return bounds

def annotate(txt, kws, label):
    bounds = findEntities(txt, kws)
    anns = [(a,b,label) for a,b in bounds]
    if anns:
        result = (txt, {'entities': anns})
        return result

def annotateText(sentences, kws, label):
    
    result = []

    for sent in sentences:
        ann = annotate(sent, kws, label)
        if ann:
            result.append(ann)
        
    return result