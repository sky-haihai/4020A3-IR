from collections import defaultdict, Counter
import numpy as np

def cal_sim(query_tokens,inverted_index,k=1000):
    print("Applying query...")
    result=defaultdict(float)

    # count the frequency of each token in the query and form a query vector 
    query_counter = Counter(query_tokens)
    dimensions=Counter(query_tokens).keys()
    print("dimensions:",dimensions)
    query_vector=np.array(list(query_counter.values()),dtype=np.int32)
    print("Query Vector:",query_vector)

    doc_counters=defaultdict(lambda: defaultdict(int))
    for dimension in dimensions:
        if dimension not in inverted_index.keys():
            print("Token not found:",dimension)
            continue

        for docno,frequency in inverted_index[dimension].items():
            doc_counters[docno][dimension]=frequency

    for docno,counter in doc_counters.items():
        doc_list=[]
        for dimension in dimensions:
            doc_list.append(counter[dimension])
        doc_vector=np.array(doc_list,dtype=np.int32)

        # use dot product to calculate similarity
        sim=np.dot(query_vector, doc_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(doc_vector))
        result[docno]=float(sim)
        #print("Docno:",docno,"Similarity:",sim)

    sorted_result = sorted(result.items(), key=lambda x: x[1], reverse=True)
    keep_count=min(k,len(sorted_result))
    docno_list = [(x[0],x[1]) for x in sorted_result[:keep_count]]

    return docno_list