import glob
import os
import random

# Gets all files in all branches of the given path for selected files (passed as tuple)

def getFileList(ftypes, start_path = '.'):
    
    file_list = []
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if fp.endswith(ftypes):
                file_list.append(fp)
    
    return file_list

# reads txt, ann files (BRAT) and returns annotated data in spacy format

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

# DEPRECATED: View all annotation instances for a given list of types. Replaced by labelWords(), readSpan() and ViewTuple()

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

# function to transform annotations according to the passed transformation dic

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

# returns tuples of words and assigned labels from spacy formatted annotated data

def labelWords(annotation):

    outcome = []
    for i, article in enumerate(annotation):
        text = article[0]
        anns = article[1]['entities']
        for ann_ in anns:
            start, end, cat = ann_
            outcome.append((text[start:end], cat))

    return outcome


# returns characters (string) and type of a given annotation tuple

def readSpan(text, ann):
    
    start, end, cat = ann
    return (text[start:end], cat)

# prints content of a list of tuples, e.g. LabeledWords

def viewTuples(textlabels):
    for item in textlabels:
        print(item[0], ' : ', item[1])

# function to extract entities (list of lists of strings) in the annotated data

def calculateEnts(annotation_data):
    result = []
    for document in annotation_data:
        ents = []
        for ent in document[1]['entities']:
            a,b,c = ent
            ents.append(document[0][a:b])
        result.append(ents)
    return result

# function for dividing annotated corpus into test and training subsets, given the division ratio (for test) and tolerance from this ration

def devideCorpus(corpus, test_ratio, tolerance=0.05):

    ents = calculateEnts(corpus)
    total_ents = list(enumerate(len(item) for item in ents))
    sum_ents = sum([x[1] for x in total_ents])
    test_size = test_ratio*sum_ents
        
    while True:
        random.shuffle(total_ents)
        testsub = []
        trainsub = []

        for item in total_ents:
            if sum([x[1] for x in testsub]) < test_size:
                testsub.append(item)
            else:
                trainsub.append(item)

        offset = abs(sum([x[1] for x in testsub])/sum_ents - test_ratio)
        
        if offset < tolerance:
            test_corpus = [corpus[x] for (x,_) in testsub]
            train_corpus = [corpus[x] for (x,_) in trainsub]
            print("Size of Training Corpus: {}\nSize of Test Corpus: {}".format(sum([x[1] for x in trainsub]), sum([x[1] for x in testsub])))
            return test_corpus, train_corpus

# merges multiple annotated text documents (in spacy format) into a single document

def mergeAnnotations(data):
    out_text = ''
    out_ents = []
    for doc in data:
        l = len(out_text)
        out_text += (doc[0]+'\n')
        entities = doc[1]['entities']
        for ent in entities:
            (a,b,c) = ent
            ent_ = (a+l, b+l, c)
            out_ents.append(ent_)
            
    return out_text, out_ents

# function for caclulating the share of unique entities in annotated input

def uniqueRatio(data):
    entities = calculateEnts(data)
    flatten_ents = [ent for sublist in entities for ent in sublist]
    unique_ents = set(flatten_ents)
    ratio = len(unique_ents)/len(flatten_ents)
    return ratio

# lists unseen and seen entities and the ration of the unseen entities in the test corpus

def separateUnseen(test_data, train_data):
    
    testset = set(labelWords(test_data))
    trainset = set(labelWords(train_data))
    
    seen = testset & trainset
    unseen = testset - seen
    return unseen, seen, len(unseen)/(len(unseen)+len(seen))

# Separates test corpus into seen and unseen (in training)

def filterSeen(TEST_DATA, TRAIN_DATA):
    
    UNSEEN_TEST_DATA = []
    SEEN_TEST_DATA = []
    unseen_ents, seen_ents, _ = separateUnseen(TEST_DATA, TRAIN_DATA)
    
    for doc in TEST_DATA:
        seen = []
        unseen = []
        text = doc[0]
        anns = doc[1]['entities']
        for ann_ in anns:
            if readSpan(text, ann_) in seen_ents:
                seen.append(ann_)
            else:
                unseen.append(ann_)
                
        UNSEEN_TEST_DATA.append((text, {'entities':unseen}))
        SEEN_TEST_DATA.append((text, {'entities':seen}))
        
    return UNSEEN_TEST_DATA, SEEN_TEST_DATA

def splitAnnotations(old_train):
    new_train = []
    for article in old_train:
        old_ents = article[1]['entities']
        full_text = article[0]
        doc_sents = tokenize.sent_tokenize(article[0], language='french')
        offset = 0
        for ind, sent in enumerate(doc_sents):
            new_ents = []
            sent_start = full_text.index(sent)
            sent_end = sent_start + len(sent)
            
            for item in old_ents:
                if sent_start <= item[1] <= sent_end:
                    new_ents.append((item[0]-sent_start, item[1]-sent_start, item[2]))
            if new_ents:
                new_train.append((sent, {'entities': new_ents}))
    return new_train