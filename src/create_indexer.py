import os
import json
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

num_threads = multiprocessing.cpu_count()*2

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

def split_dict(word_dict, n):
    chunk_size = len(word_dict) // n
    word_dict_items = list(word_dict.items())
    return [dict(word_dict_items[i:i + chunk_size]) for i in range(0, len(word_dict_items), chunk_size)]

def merge_inverted_indexes(indexes):
    merged_index = defaultdict(lambda: defaultdict(int))
    for index in indexes:
        for word, postings in index.items():
            for docno, count in postings.items():
                merged_index[word][docno] += count
    
    return merged_index

def build_indexer(word_dict, output_dir, num_threads=4):
    print("Building indexer...")
    
    word_dict_chunks = split_dict(word_dict, num_threads)
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        partial_indexes = list(executor.map(process_word_dict, word_dict_chunks))

    inverted_index = merge_inverted_indexes(partial_indexes)
    
    print("Grouping by initials...")
    inverted_index_grouped = group_by_initial(inverted_index)
    
    print("Saving to json...")
    with ThreadPoolExecutor() as executor:
        for initial_letter, index in inverted_index_grouped.items():
            executor.submit(save_to_json, output_dir, initial_letter, index)

    print("Done!")