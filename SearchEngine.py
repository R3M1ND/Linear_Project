
from nltk import stem
import re
import json
import nltk
import math
nltk.download('wordnet')


class SearchEngine:
    except_words = set(['is', 'am', 'are', 'was', 'were', 'been', 'be'])

    def __init__(self, docs_path=None):
        self.lemma = stem.WordNetLemmatizer()
        if docs_path is not None:
            self.read_from_file(docs_path)

        self.create_words_dimension()

        self.parse_docs_to_vector()

        self.spell = SpellCorrection(set(self.words_dimension.keys()))

    def read_from_file(self, path):
        # Read zen_record from file
        with open(path, 'r') as file:
            self.database_json = json.load(file)

    def parse_words(self, sentence) -> list:
        # Parsing sentence to words vector + cleaning + Lemmatizing
        result = list()
        sentence = sentence.replace("-", " ")
        words = re.sub(r'[^a-zA-Z ]', "", sentence).lower().split()
        for word in words:
            if word not in SearchEngine.except_words:
                word_base = self.lemma.lemmatize(word, 'v')
                word_base = self.lemma.lemmatize(word_base)
                result.append(word_base)
            else:
                result.append(word)
        return result

    def create_words_dimension(self):
        # Create dimensions from all words from all sentences in database
        self.words_dimension = set()
        # Gattering data to form words dimensions
        for data in self.database_json:
            sentence = data['Quote']
            words_from_sentence = self.parse_words(sentence)
            self.words_dimension.update(words_from_sentence)

        self.words_dimension = dict.fromkeys(sorted(self.words_dimension))

    def parse_sentence_vector(self, sentence, words_dimension=None) -> dict:
        # Parse sentence to vector
        words_from_sentence = self.parse_words(sentence)
        if words_dimension is None:
            # the sentence does not math in any word dimension.
            sentence_vector = dict.fromkeys(self.words_dimension, 0)
            for word in words_from_sentence:
                try:
                    sentence_vector[word] += 1
                except:
                    # Key Error occure -> there is a word that does not involve in the dimension
                    # Do a 2nd step deep search.
                    # Or do the word correction.
                    if word not in self.spell.DICTIONARY:

                        # print("Showing result for", similar_word)
                        pass
            if sum(sentence_vector.values()) == 0:
                # does not math any words in docs.
                return None

        else:
            sentence_vector = dict.fromkeys(words_dimension, 0)
            for word in sentence_vector:
                try:
                    sentence_vector[word] += 1
                except:
                    pass
        return sentence_vector

    def pearson_calculate(self, a, b) -> float:
        if len(a) != len(b):
            raise ValueError('Both vectors must have the same lenght.')

        a_mean = sum(value for value in a if value > 0)/len(a)
        b_mean = sum(value for value in b if value > 0)/len(b)

        # numerator
        sum_cov = sum((a_i - a_mean)*(b_i - b_mean) for a_i, b_i in zip(a, b))
        # denominator
        sq_sig = math.sqrt(sum((a_i-a_mean)**2 for a_i in a) *
                            sum((b_i - b_mean)**2 for b_i in b))
        pearson_result = sum_cov/sq_sig

        return pearson_result

    def parse_docs_to_vector(self):
        result = dict()
        sentences_total = set()
        n = 0
        for data in self.database_json:
            sentence = data['Quote']
            if sentence not in sentences_total:  # avoid duplicated sentences,or docs
                result[n] = {'Quote': sentence, 'vector_data': self.parse_sentence_vector(
                    sentence)}
                sentences_total.add(sentence)
                n += 1
        self.parsed_doc = result
        return result

    def re_correction_sentence(self,sentence):
        sentence = self.parse_words(sentence)
        result = []
        for word in sentence:
            if word not in self.words_dimension:
                correct_word = self.spell.spell_correction(word)
                result.append(correct_word)
            else:
                result.append(word)
        
        return " ".join(result)


    def _perform_search(self, search_kw) -> dict:
        search_kw = self.parse_sentence_vector(search_kw)
        if search_kw == None:
            # search_kw does not match any result

            return None

        result = dict()

        for i in range(len(self.parsed_doc)):
            data = self.parsed_doc[i]
            sentence = data['Quote']
            result[i] = {'Quote': sentence, 'pearson_value': self.pearson_calculate(
                search_kw.values(), data['vector_data'].values())}

        result = dict(
            sorted(result.items(), key=lambda item: item[1]['pearson_value'], reverse=True))
        return result

    def search_by_keyword(self, **kwargs):
        check = []
        return_value = kwargs['return_value']
        keyword = kwargs['keyword']
        try:
            number_of_result = kwargs['number_of_result']
        except:
            number_of_result = 10

        r = self._perform_search(keyword)
        if r is None:
            # Keyword does not math any result
            re_corrected_keyword = self.re_correction_sentence(keyword)
            r = self._perform_search(re_corrected_keyword)
            print(f"No result for {keyword}")
            print(f"Showing result of '{re_corrected_keyword}'")
            #not have -> ![]
            check.append(re_corrected_keyword)

        result = []
        n = 0
        for data in r:
            if n >= number_of_result:
                break
            sentence = r[data][return_value]
            result.append(sentence)
            n += 1

        return result,check


def clean_non_alpha(text):
    chars = '-\''
    for c in chars:
        text = text.replace(c, "")
    return text


def hamming_distance(word_a, word_b) -> float:
    # Comparing the same character at the same position, return score of similar
    result = 0
    result += 2*abs(len(word_a)-len(word_b))
    length = min(len(word_a), len(word_b))
    for i in range(length):
        if word_a[i] != word_b[i]:
            result += 1
    return result


def parse_alphabet_vector(word) -> dict:
    # Parsing word to alphabet vector
    word = word.lower()
    A_Z = 'abcdefghijklmnopqrstuvwxyz'
    word_vector = dict.fromkeys(A_Z, 0)
    for c in word:
        try:
            word_vector[c] += 1
        except:
            print("Warning Error occured while parsing to alphabet vector.")
    return word_vector


class SpellCorrection:
    def __init__(self, iterable=None, **kw):
        if iterable is None:
            dp = kw['dictionary_path']
            if dp is not None:
                self.read_dictionary(dp)
        else:
            self._create_DICTIONARY(iterable)

    def read_dictionary(self, path):
        with open(path, 'r') as file:
            content = file.read()
            self._create_DICTIONARY(content.splitlines())

    def _create_DICTIONARY(self, iterable):
        self.DICTIONARY = dict.fromkeys(
            clean_non_alpha(word.lower()) for word in iterable)

        self.words_alphabet_dimension = {k: v for k, v in zip(self.DICTIONARY, [parse_alphabet_vector(a) for a in self.DICTIONARY])}

        for word in self.words_alphabet_dimension:
            self.words_alphabet_dimension[word] = parse_alphabet_vector(word)


    def spell_correction(self, word) -> list:
        word_vec = parse_alphabet_vector(word)
        pearson_result = dict()
        similarity = -1
        for w in self.words_alphabet_dimension:
            new_high = self.pearson_calculate(
                word_vec.values(), self.words_alphabet_dimension[w].values())
            pearson_result[new_high] = w
            if new_high >= similarity:
                similarity = new_high

        sorted_pearson_result = dict(
            sorted(pearson_result.items(), reverse=True))

        correctness_rank = list()
        for index in sorted_pearson_result:
            h_dist = hamming_distance(word, sorted_pearson_result[index])
            pearson_coef = float(index)
            correctness_rank.append(
                (h_dist, pearson_coef, sorted_pearson_result[index]))
            if float(index) < 0.8:
                break

        if correctness_rank == []:
            raise ValueError('No word match.')

        correctness_rank = sorted(correctness_rank, key=lambda i: i[0])
        return correctness_rank[0][2]

    def pearson_calculate(self, a, b) -> float:
        if len(a) != len(b):
            raise ValueError('Both vectors must have the same lenght.')

        a_mean = sum(value for value in a if value > 0)/len(a)
        b_mean = sum(value for value in b if value > 0)/len(b)

        # numerator
        sum_cov = sum((a_i - a_mean)*(b_i - b_mean) for a_i, b_i in zip(a, b))
        # denominator
        sq_sig = math.sqrt(sum((a_i-a_mean)**2 for a_i in a) *
                            sum((b_i - b_mean)**2 for b_i in b))

        pearson_result = sum_cov/sq_sig

        return pearson_result


if __name__ == "__main__":

    se = SearchEngine("zen_record.txt")
    # print(se.spell.spell_correction("bird"))
    # sp = SpellCorrection(None, dictionary_path="dictionary.txt")
    # print(sp.spell_correction('ola'))

    kw = input("Enter search keywords : ")
    x = se.search_by_keyword(keyword=kw, return_value ='Quote',number_of_result = 20)
    if x[1]==[]:
        print("EIEI mee ja")
    elif x[1]!=[]:
        print(f"EiEI Not have na {x[1]}")
    for i,data in enumerate(x):
        print(i+1,data.replace(kw,"'"+kw+"'"))