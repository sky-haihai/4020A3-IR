import os
import json
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

num_threads = multiprocessing.cpu_count()*2

# inverted_index = defaultdict(lambda: defaultdict(int))
def process_word_dict(word_dict):
    inverted_index = defaultdict(lambda: defaultdict(int))
    for docno, words in word_dict.items():
        word_counts = Counter(words)
        for word, count in word_counts.items():
            inverted_index[word][docno] += count
    
    return inverted_index

def group_by_initial(inverted_index):
    inverted_index_grouped = defaultdict(dict)
    for word, postings in inverted_index.items():# {word:{docno:count}}
        initial_letter = word[0].lower()
        inverted_index_grouped[initial_letter][word] = postings

    return inverted_index_grouped

def save_to_json(output_dir,inverted_index_grouped):
    os.makedirs(output_dir, exist_ok=True)

    for initial_letter, index in inverted_index_grouped.items():
        file_path = os.path.join(output_dir, f"{initial_letter}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

def build_indexer(word_dict,output_dir):
    print("Building indexer...")
    inverted_index=process_word_dict(word_dict)
    print("Grouping by initials...")
    inverted_index_grouped=group_by_initial(inverted_index)
    print("Saving to json...")
    save_to_json(output_dir,inverted_index_grouped)
    print("Done!")