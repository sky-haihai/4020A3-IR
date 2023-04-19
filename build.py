import helper.unzip_gz as unzip
import helper.preprocess as preprocess
import helper.create_indexer as index

input_path = r'input\data'
index_path = r'output\indexer'

#unzip all gz files
xmls=unzip.gzs_to_xmls(input_path)

#extract words from xmls
words_dict=preprocess.xmls_to_word_dict(xmls)

#build index
index.build_indexer(words_dict,index_path)
