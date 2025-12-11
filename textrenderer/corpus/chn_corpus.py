import random
import numpy as np
import yaml
import os
from easydict import EasyDict
from libs.utils import load_chars
import glob

from textrenderer.corpus.corpus import Corpus


class ChnCorpus(Corpus):
    def __init__(self, chars_file, corpus_dir=None, length=None):
        self.corpus_dir = corpus_dir
        self.corpus_dir = corpus_dir
        self.length = length
        self.corpus = []

        self.chars_file = chars_file
        self.charsets = load_chars(chars_file)

        self.typed_corpus = {
            'name': [],
            'type': [],
            'legal_person': [],
            'operation_date': [],
            'location': [],
            'social_credit_code': [],
            'registration_capital': []
        }
        self.load()
        # super().__init__(chars_file, corpus_dir=None, length=None)

    def load_corpus_path(self, corpus_dir):
        """
        Load txt file path in corpus_dir
        """
        print("Loading corpus from: " + corpus_dir)
        self.corpus_path = glob.glob(corpus_dir + '/**/*.txt', recursive=True)
        if len(self.corpus_path) == 0:
            print("Corpus not found.")
            exit(-1)

    def load(self):
        """
        Load one corpus file as one line , and get random {self.length} words as result
        """
        self.load_corpus_path(self.corpus_dir)

        for i, p in enumerate(self.corpus_path):
            corpus_type = os.path.splitext(os.path.basename(p))[0]
            print_end = '\n' if i == len(self.corpus_path) - 1 else '\r'
            print("Loading chn corpus: {}/{}".format(i + 1, len(self.corpus_path)), end=print_end)
            with open(p, encoding='utf-8') as f:
                data = f.readlines()

            lines = []
            for line in data:
                line_striped = line.strip()
                line_striped = line_striped.replace('\u3000', '')
                line_striped = line_striped.replace('&nbsp', '')
                line_striped = line_striped.replace("\00", "")

                if line_striped != u'' and len(line.strip()) > 1:
                    lines.append(line_striped)

            # 所有行合并成一行
            # split_chars = [',', '，', '：', '-', ' ', ';', '。']
            # splitchar = random.choice(split_chars)
            # whole_line = splitchar.join(lines)

            # 在 crnn/libs/label_converter 中 encode 时还会进行过滤
            # whole_line = ''.join(filter(lambda x: x in self.charsets, whole_line))

            # if len(whole_line) > self.length:
            #     self.corpus.append(whole_line)
            self.corpus.extend(lines)
            self.typed_corpus[corpus_type].extend(lines)

        with open('./data/corpus/business_scopes.yaml', mode='r', encoding='utf-8') as f:
            self.business_types = EasyDict(yaml.load(f.read(), Loader=yaml.FullLoader))

    def get_sample(self, img_index):
        # 每次 gen_word，随机选一个预料文件，随机获得长度为 word_length 的字符
        line = random.choice(self.corpus)

        start = np.random.randint(0, len(line) - self.length)

        word = line[start:start + self.length]
        # return word
        return line

    def get_sample(self, entity_type, company_name):
        # 每次 gen_word，随机选一个预料文件，随机获得长度为 word_length 的字符
        counts = len(self.business_types.items())
        if entity_type == 'business_scopes':
            for key, value in self.business_types.items():
                keys = key.split('，')
                if any([e in company_name for e in keys]):
                    # print(''.join([e for e in keys]) + 'in ' + company_name)
                    num_items = len(value)
                    # Use num_items as the upper bound for sampling if it's smaller than the intended range
                    sample_size = random.randint(min(4, num_items), min(8, num_items))
                    # Ensure sample_size is at least 1 if value is not empty, though random.randint(a,b) where a=b is fine.
                    # If num_items < 4, min(4, num_items) is num_items. min(8, num_items) is num_items.
                    # So sample_size will be num_items.
                    result = random.sample(value, sample_size)
                    return '，'.join(result)
            print(company_name + 'does not have business scopes.\n')
            raise Exception
        # elif entity_type == 'company_name':
        #     return '北京慧诺国际建筑咨询有限公司'
        else:
            return random.choice(self.typed_corpus[entity_type])