import os
import json
from collections import defaultdict
import preprocess as preprocess
import calculate_similarity as similarity

inverted_index_dir=r"output\indexer"
topic_file=r"input\topics.txt"
result_file=r"output"

topic_numbers=preprocess.topics_to_numbers(topic_file)
topic_tokens=preprocess.topics_to_tokens(topic_file)

if os.path.exists(inverted_index_dir)==False:
    print("Please build inverted index first")
    exit(0)

#load inverted index
inverted_index = defaultdict(lambda: defaultdict(int))
for letter in 'abcdefghijklmnopqrstuvwxyz':
    file_path = os.path.join(inverted_index_dir, f"{letter}.json")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        inverted_index.update(data)

result_string=""
#calculate similarity
for i in range(len(topic_tokens)):
    tokens=topic_tokens[i]
    number=topic_numbers[i]
    docno_list=similarity.cal_sim(tokens,inverted_index,k=1000)
    for j in range(len(docno_list)):
        result_string+=f"{number} Q0 {docno_list[j][0]} {j+1} {docno_list[j][1]} Group9\n"

#save result
os.makedirs(result_file, exist_ok=True)
with open(os.path.join(result_file,'result.txt'),"w",encoding="utf-8") as f:
    f.write(result_string)