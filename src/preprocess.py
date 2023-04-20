import concurrent.futures
from collections import defaultdict as defaultDict
from bs4 import BeautifulSoup, Tag
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import words
from nltk.corpus import stopwords

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('words')

stop_words = set(stopwords.words('english'))
english_words = set(words.words())
stemmer = PorterStemmer()

def process_doc(doc_tag):

    docno_tag = doc_tag.find('docno')
    html_tag = doc_tag.find('html')

    if docno_tag is None:
        print("Error: DOCNO tag not found")
        return None

    docno = docno_tag.get_text().strip()
    print(f"Converting DOCNO: {docno} to words...")

    if html_tag is None:
        # print("HTML tag not found, creating a new one...")
        soup = BeautifulSoup("", 'html.parser')
        new_html_tag = Tag(name='html', parser=soup.builder)

        for child in doc_tag.findChildren(recursive=False):
            if child.name not in ['docno', 'dochdr', 'docoldno']:
                # print('Appending \"', child.name, '\" ...')
                new_html_tag.append(child.extract())

        doc_tag.append(new_html_tag)

    words = []

    html_tag = doc_tag.find('html')
    content_str = ''
    for tag in html_tag.find_all():
        text = tag.get_text()
        if text is not None:
            content_str += text

    tokens = word_tokenize(content_str)
    tokens = [word.lower() for word in tokens if word.isalpha()]
    filtered_tokens = [word for word in tokens if word not in stop_words]
    stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]
    only_words = [word for word in stemmed_tokens if word in english_words]

    for word in only_words:
        words.append(word.encode('utf-8').decode('utf-8'))

    return docno, words


def xmls_to_word_dict(xmls,num_threads=14):
    print("Converting HTMLs to words...")

    result = defaultDict()

    for xml in xmls:
        soup = BeautifulSoup(xml, 'html.parser')
        doc_tags = soup.find_all('doc')

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            future_to_doc_tag = {executor.submit(process_doc, doc_tag): doc_tag for doc_tag in doc_tags}

            for future in concurrent.futures.as_completed(future_to_doc_tag):
                try:
                    docno, temp = future.result()
                    if docno is not None:
                        result[docno] = temp
                except Exception as exc:
                    print("Error processing doc: %s" % (exc))

    print("Finished converting HTMLs to words...")
    return result


def topics_to_numbers(topic_file):
    result = []

    # open the file and read its contents
    with open(topic_file, 'r', encoding='utf-8') as file:
        xml_string = file.read()

    xml_string = xml_string.replace('<title>', '</num>\n<title>')
    xml_string = xml_string.replace('<desc>', '</title>\n<desc>')
    xml_string = xml_string.replace('<narr>', '</desc>\n<narr>')
    xml_string = xml_string.replace('</top>', '</narr>\n</top>')

    soup = BeautifulSoup(xml_string, 'html.parser')

    top_tags = soup.find_all('top')

    for tag in top_tags:
        num = tag.find('num').text
        num = num.replace('Number: ', '')
        num = num.strip()

        result.append(num)

    return result


def topics_to_tokens(topic_file):

    result = []

    # open the file and read its contents
    with open(topic_file, 'r', encoding='utf-8') as file:
        xml_string = file.read()

    xml_string = xml_string.replace('<title>', '</num>\n<title>')
    xml_string = xml_string.replace('<desc>', '</title>\n<desc>')
    xml_string = xml_string.replace('<narr>', '</desc>\n<narr>')
    xml_string = xml_string.replace('</top>', '</narr>\n</top>')

    soup = BeautifulSoup(xml_string, 'html.parser')

    top_tags = soup.find_all('top')

    for tag in top_tags:
        num = tag.find('num').text
        num = num.replace('Number: ', '')
        num = num.strip()

        title = tag.find('title').text
        title = title.replace('\n', '')
        title = title.strip()
        title_tokens = word_tokenize(title)
        title_tokens = [word.lower()
                        for word in title_tokens if word.isalpha()]
        title_tokens = [
            word for word in title_tokens if word not in stop_words]
        title_tokens = [stemmer.stem(word) for word in title_tokens]
        title_tokens = [word for word in title_tokens if word in english_words]

        desc = tag.find('desc').text.strip()
        desc = desc.replace('Description:', '')
        desc = desc.replace('\n', '')
        desc = desc.strip()
        desc_tokens = word_tokenize(desc)
        desc_tokens = [word.lower() for word in desc_tokens if word.isalpha()]
        desc_tokens = [word for word in desc_tokens if word not in stop_words]
        desc_tokens = [stemmer.stem(word) for word in desc_tokens]
        desc_tokens = [word for word in desc_tokens if word in english_words]

        narr = tag.find('narr').text.strip()
        narr = narr.replace('Narrative:', '')
        narr = narr.replace('\n', '')
        narr = narr.strip()
        narr_tokens = word_tokenize(narr)
        narr_tokens = [word.lower() for word in narr_tokens if word.isalpha()]
        narr_tokens = [word for word in narr_tokens if word not in stop_words]
        narr_tokens = [stemmer.stem(word) for word in narr_tokens]
        narr_tokens = [word for word in narr_tokens if word in english_words]

        # add title tokens twice to increase its weight
        merged_tokens = title_tokens+title_tokens+desc_tokens+narr_tokens
        result.append(merged_tokens)

    return result
