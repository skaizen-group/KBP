import glob
import os

def getFileList(ftypes, start_path = '.'):
    
    file_list = []
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if fp.endswith(ftypes):
                file_list.append(fp)
    
    return file_list
	
def loadAnnotations(ann_files, txt_files, types):
    ANNOTATIONS = []
    
    for af, tf in zip(ann_files, txt_files):
        with open(af, 'r') as ann_data, open(tf, 'r') as text_data:
            text = text_data.read()
            res = []
            for line in ann_data:
                if line.startswith('T'):
                    content = line.split()
                    if content[1] in types:
                        res.append((int(content[2]), int(content[3]), content[1]))
            if res: ANNOTATIONS.append((text,{"entities": res}))
                
    return ANNOTATIONS

# View all annotation instances for a given list of types

def viewAnnotations(ann_files, txt_files, types, tf=None):
    
    raw_data = loadAnnotations(ann_files, txt_files, types)
    
    if tf==None:
        articles = raw_data
    else:
        articles = editAnnotations(raw_data, tf)
        
    for i in range(len(articles)):
        example = articles[i]
        mytext = example[0]
        myanns = example[1]['entities']
        for j in range(len(myanns)):
            start, end, cat = myanns[j]
            print(mytext[start:end],':', cat)

# Returns tag words used to annote given types
def getTags(ann_files, txt_files, types):
    
    articles = loadAnnotations(ann_files, txt_files, types)
    tags = []
    
    for i in range(len(articles)):
        example = articles[i]
        mytext = example[0]
        myanns = example[1]['entities']
        for j in range(len(myanns)):
            start, end, cat = myanns[j]
            tags.append(mytext[start:end])
    return tags
	
def editAnnotations(raw_annotations, transformation):

    annotation = raw_annotations
    for article in range(len(annotation)):
        output = []
        for item in annotation[article][1]['entities']:
            item = list(item)
            #old_tag = item[2]
            new_tag = transformation.get(item[2],"No_key")
            item[2]=new_tag
            item = tuple(item)
            output.append(item)
        annotation[article][1]['entities'] = output
        
    return annotation