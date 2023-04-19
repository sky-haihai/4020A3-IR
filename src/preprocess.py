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

def xmls_to_word_dict(xmls):
    print("Converting HTMLs to words...")

    result = defaultDict()

    stemmer = PorterStemmer()

    for xml in xmls:
        soup = BeautifulSoup(xml, 'html.parser')
        doc_tags = soup.find_all('doc')
        for doc_tag in doc_tags:
            docno_tag = doc_tag.find('docno')
            html_tag = doc_tag.find('html')

            if docno_tag is None:
                print("Error: DOCNO tag not found")
                continue

            docno = docno_tag.get_text().strip()
            print("Converting DOCNO: ", docno, " to words...")

            # if html tag is not found, create a new one
            if html_tag is None:
                print("HTML tag not found, creating a new one...")
                new_html_tag = Tag(name='html', parser=soup.builder)

                for child in doc_tag.findChildren(recursive=False):
                    if child.name not in ['docno', 'dochdr', 'docoldno']:
                        print('Appending \"',child.name,'\" ...')
                        new_html_tag.append(child.extract())

                doc_tag.append(new_html_tag)

            temp= []

            # extracting html
            print ("Extracting HTML...")
            html_tag = doc_tag.find('html')
            content_str=''
            for tag in html_tag.find_all():
                text=tag.get_text()
                if text is not None:
                    content_str+=text
            
            print('Preprocessing tokens')
            print('\tTokenizing')
            tokens = word_tokenize(content_str)

            print('\tCheck if token is alpha')
            tokens = [word.lower() for word in tokens if word.isalpha()]
            
            # process words
            print('\tRemoving stop words')
            filtered_tokens = [word for word in tokens if word not in stop_words]
            print('\tStemming')
            stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]
            print('\tRemoving non-english words')
            only_words = [word for word in stemmed_tokens if word in english_words]
            print('\tTo utf-8')
            for word in only_words:
                temp.append(word.encode('utf-8').decode('utf-8'))

            result[docno] = temp

    print("Finished converting HTMLs to words...")
    return result

def topics_to_numbers(topic_file):
    result=[]

    # open the file and read its contents
    with open(topic_file, 'r',encoding='utf-8') as file:
        xml_string = file.read()

    xml_string = xml_string.replace('<title>', '</num>\n<title>')
    xml_string = xml_string.replace('<desc>', '</title>\n<desc>')
    xml_string = xml_string.replace('<narr>', '</desc>\n<narr>')
    xml_string = xml_string.replace('</top>', '</narr>\n</top>')

    soup = BeautifulSoup(xml_string, 'html.parser')

    top_tags=soup.find_all('top')

    for tag in top_tags:
        num=tag.find('num').text
        num=num.replace('Number: ','')
        num=num.strip()

        result.append(num)

    return result

def topics_to_tokens(topic_file):
    
    result=[]

    # open the file and read its contents
    with open(topic_file, 'r',encoding='utf-8') as file:
        xml_string = file.read()

    xml_string = xml_string.replace('<title>', '</num>\n<title>')
    xml_string = xml_string.replace('<desc>', '</title>\n<desc>')
    xml_string = xml_string.replace('<narr>', '</desc>\n<narr>')
    xml_string = xml_string.replace('</top>', '</narr>\n</top>')

    soup = BeautifulSoup(xml_string, 'html.parser')

    top_tags=soup.find_all('top')

    stemmer=PorterStemmer()

    for tag in top_tags:
        num=tag.find('num').text
        num=num.replace('Number: ','')
        num=num.strip()

        title=tag.find('title').text
        title=title.replace('\n','')
        title=title.strip()
        title_tokens=word_tokenize(title)
        title_tokens=[word.lower() for word in title_tokens if word.isalpha()]
        title_tokens=[word for word in title_tokens if word not in stop_words]
        title_tokens = [stemmer.stem(word) for word in title_tokens]
        title_tokens = [word for word in title_tokens if word in english_words]

        desc=tag.find('desc').text.strip()
        desc=desc.replace('Description:','')
        desc=desc.replace('\n','')
        desc=desc.strip()
        desc_tokens=word_tokenize(desc)
        desc_tokens=[word.lower() for word in desc_tokens if word.isalpha()]
        desc_tokens=[word for word in desc_tokens if word not in stop_words]
        desc_tokens = [stemmer.stem(word) for word in desc_tokens]
        desc_tokens = [word for word in desc_tokens if word in english_words]

        narr=tag.find('narr').text.strip()
        narr=narr.replace('Narrative:','')
        narr=narr.replace('\n','')
        narr=narr.strip()
        narr_tokens=word_tokenize(narr)
        narr_tokens=[word.lower() for word in narr_tokens if word.isalpha()]
        narr_tokens=[word for word in narr_tokens if word not in stop_words]
        narr_tokens = [stemmer.stem(word) for word in narr_tokens]
        narr_tokens = [word for word in narr_tokens if word in english_words]

        # add title tokens twice to increase its weight 
        merged_tokens=title_tokens+title_tokens+desc_tokens+narr_tokens
        result.append(merged_tokens)

    return result