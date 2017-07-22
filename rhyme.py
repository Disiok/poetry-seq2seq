#! /usr/bin/env python
#-*- coding:utf-8 -*-

from utils import *
import pypinyin


py_raw = os.path.join(DATA_RAW_DIR, 'pinyin.txt')
_rhy_path = os.path.join(DATA_PROCESSED_DIR, 'rhy_dict.json')


'''
Tonal and rhyming reference from:
    https://baike.baidu.com/item/绝句律诗格律
'''


'''
类型一
⊙平平仄仄，⊙仄仄平平。（韵）⊙仄平平仄，平平仄仄平。（韵）
例诗： 山中 王勃
长江悲已滞，万里念将归。况属高秋晚，山中黄叶飞。
'''
five_char_type_a = {
    'tone': [
        '*ppzz',
        '*zzpp',
        '*zppz',
        'ppzzp'
    ],
    'rhyme': [1, 3]
}

'''
类型二
平平仄仄平，（韵）⊙仄仄平平。（韵）⊙仄⊙平仄，平平仄仄平。（韵）
例诗：壬辰元日试笔呈诸师友 陈忠远（即阿袁）
龙光绚九天，虎幄定三边。一守凤城道：“新年胜旧年！”
'''
five_char_type_b = {
    'tone': [
        'ppzzp',
        '*zzpp',
        '*z*pz',
        'ppzzp'
    ],
    'rhyme': [0, 1, 3]
}


'''
类型三
⊙仄平平仄，平平仄仄平。（韵）⊙平平仄仄，⊙仄仄平平。（韵）
例诗：南行别第 韦承庆
万里人南去，三春雁北飞。不知何岁月，得与尔同归。
'''
five_char_type_c = {
    'tone': [
        '*zppz',
        'ppzzp',
        '*ppzz',
        '*zzpp'
    ],
    'rhyme': [1, 3]
}


'''
类型四
⊙仄仄平平，（韵）平平仄仄平。（韵）⊙平平仄仄，⊙仄仄平平。（韵）
例诗： 塞下曲 卢纶
林暗草惊风，将军夜引弓。平明寻白羽，没在石棱中。
'''
five_char_type_d = {
    'tone': [
        '*zzpp',
        'ppzzp',
        '*ppzz',
        '*zzpp'
    ],
    'rhyme': [0, 1, 3]
}


five_char_tones = [
    five_char_type_a,
    five_char_type_b,
    five_char_type_c,
    five_char_type_d
]


'''
类型一
平起、首句不押韵
⊙平⊙仄平平仄， ⊙仄平平仄仄平。（韵） ⊙仄⊙平平仄仄， ⊙平⊙仄仄平平。（韵）
例诗：南游感兴 窦巩
伤心欲问前朝事， 惟见江流去不回。 日暮东风春草绿， 鹧鸪飞上越王台。
'''
seven_char_type_a = {
    'tone': [
        '*p*zppz',
        '*zppzzp',
        '*z*ppzz',
        '*p*zzpp'
    ],
    'rhyme': [1, 3]
}


'''
类型二
平起、首句押韵
⊙平⊙仄仄平平，（韵） ⊙仄平平仄仄平。（韵） ⊙仄⊙平平仄仄， ⊙平⊙仄仄平平。（韵）
例诗：出塞 王昌龄
秦时明月汉时关， 万里长征人未还。 但使龙城飞将在， 不教胡马度阴山。
'''
seven_char_type_b = {
    'tone': [
        '*p*zzpp',
        '*zppzzp',
        '*z*ppzz',
        '*p*zzpp'
    ],
    'rhyme': [0, 1, 3]
}


'''
类型三
仄起、首句不押韵
⊙仄⊙平平仄仄， ⊙平⊙仄仄平平。（韵） ⊙平⊙仄平平仄， ⊙仄平平仄仄平。（韵）
例诗：九月九日忆山东兄弟王维
独在异乡为异客， 每逢佳节倍思亲。 遥知兄弟登高处， 遍插茱萸少一人。
'''
seven_char_type_c = {
    'tone': [
        '*z*ppzz',
        '*p*zzpp',
        '*p*zppz',
        '*zppzzp'
    ],
    'rhyme': [1, 3]
}


'''
类型四
仄起、首句押韵
⊙仄平平仄仄平，（韵） ⊙平⊙仄仄平平。（韵） ⊙平⊙仄平平仄， ⊙仄平平仄仄平。（韵）
例诗：从军行 王昌龄
青海长云暗雪山， 孤城遥望玉门关。 黄沙百战穿金甲， 不破楼兰终不还！
'''
seven_char_type_d = {
    'tone': [
        '*zppzzp',
        '*p*zzpp',
        '*p*zppz',
        '*zppzzp'
    ],
    'rhyme': [0, 1, 3]
}


seven_char_tones = [
    seven_char_type_a,
    seven_char_type_b,
    seven_char_type_c,
    seven_char_type_d
]


tone_rules = {
    5: five_char_tones,
    7: seven_char_tones
}


class RhymeUtil:
    def get_rhyme_category(self, vowel):
        vowel = vowel.upper()

        if vowel in ['A', 'IA', 'UA']:
            return 1
        elif vowel in ['O', 'E', 'UO']:
            return 2
        elif vowel in ['IE', 'VE']:
            return 3
        elif vowel in ['AI', 'UAI']:
            return 4
        elif vowel in ['EI', 'UI']:
            return 5
        elif vowel in ['AO', 'IAO']:
            return 6
        elif vowel in ['OU', 'IU']:
            return 7
        elif vowel in ['AN', 'IAN', 'UAN', 'VAN']:
            return 8
        elif vowel in ['EN', 'IN', 'UN', 'VN']:
            return 9
        elif vowel in ['ANG', 'IANG', 'UANG']:
            return 10
        elif vowel in ['ENG', 'ING']:
            return 11
        elif vowel in ['ONG', 'IONG']:
            return 12
        # elif (vowels == 'I' and not pinyin[0] in ['Z', 'C', 'S', 'R']) \
        #         or vowels == 'V':
        #     return 13
        elif vowel == 'I':
            return 14
        elif vowel == 'U':
            return 15
        else:
            return None

    def has_char(self, ch):
        """

        Args:
            ch: A unicode character

        Returns:
            bool: Whether rhyming information exists for this character
        """
        return True

    def get_possible_tones(self, ch):
        """
        Args:
            ch: A unicode character

        Returns:
            [int]: A list of possible tones

        """
        final_tones = pypinyin.pinyin(ch, style=pypinyin.FINALS_TONE3, heteronym=True, errors=u'default')[0] # select results for first and only char
        tones = map(lambda final_tone: final_tone[-1], final_tones)
        filtered_tones = filter(unicode.isdigit, tones)
        tones_int = map(int, filtered_tones)

        # deduplication
        deduped_tones = []
        for tone in tones_int:
            if tone not in deduped_tones:
                deduped_tones.append(tone)

        return deduped_tones

    def get_possible_vowels(self, ch):
        """
        Args:
            ch: A unicode character

        Returns:
            [str]: A list of possible vowels
        """
        vowels = pypinyin.pinyin(ch, style=pypinyin.FINALS, heteronym=True, errors=u'default')[0] # select results for first and only char
        return vowels

    def get_possible_tone_types(self, ch):
        """

        Args:
            ch: A unicode character

        Returns:
            str: 'p' or 'z' or '*' representing possible tone types
        """
        tones = self.get_possible_tones(ch)
        pin_tones = {1, 2} & set(tones)
        ze_tones = {3, 4} & set(tones)

        if pin_tones and ze_tones:
            return '*'
        elif pin_tones:
            return 'p'
        elif ze_tones:
            return 'z'
        else:
            raise Exception('No tones associated with the character')

    def get_possible_rhyme_categories(self, ch):
        """

        Args:
            ch: A unicode character

        Returns:
            [int]: A list of possible rhyme categories
        """
        vowels = self.get_possible_vowels(ch)
        rhyme_categories = map(self.get_rhyme_category, vowels)
        filtered_categories = filter(None, rhyme_categories)
        return filtered_categories

    def can_rhyme(self, ch_list):
        """

        Args:
            ch_list: A list of unicode characters

        Returns:
            bool: Whether if a list of unicode characters can rhyme
        """
        rhyme_categories_list = [set(self.get_possible_rhyme_categories(ch)) for ch in ch_list]
        common_categories = set.intersection(*rhyme_categories_list)
        result = True if common_categories else False

        return result


class RhymeEvaluator:

    def __init__(self):
        self.rhyme_util = RhymeUtil()

    def score_tone(self, rule, sentences):
        tone_rule = rule['tone']
        score = 0.
        max_score = float(len(sentences) * len(sentences[0]))

        for line_index, line in enumerate(sentences):
            for ch_index, ch in enumerate(line):
                expected_tone_type = tone_rule[line_index][ch_index]
                possible_tone_type = self.rhyme_util.get_possible_tone_types(ch)
                tone_type_set = {expected_tone_type, possible_tone_type}

                if '*' in tone_type_set or len(tone_type_set) == 1:
                    score += 1.

        percentage_score = score / max_score
        return percentage_score

    def score_rhyme(self, rule, sentences):
        rhyme_rule = rule['rhyme']
        rhyme_chars = [sentences[line_number][-1] for line_number in rhyme_rule]

        score = 1. if self.rhyme_util.can_rhyme(rhyme_chars) else 0.

        return score

    def score(self, rule, sentences, split=0.5, output_split=False):
        tone_score = self.score_tone(rule, sentences)
        rhyme_score = self.score_rhyme(rule, sentences)

        tone_weight = split
        rhyme_weight = 1. - split

        combined_score = tone_score * tone_weight + rhyme_score * rhyme_weight

        if output_split:
            return combined_score, tone_score, rhyme_score
        else:
            return combined_score


    def eval(self, sentences, output_all_scores=False, output_split=False):
        """
        Args:
            sentences: A list of unicode strings

        Returns:
            float: A score from 0 to 1
        """

        # check 4 lines
        if len(sentences) != 4:
            return 0.

        # check all lines are either 5 or 7 characters and same number of characters
        sentence_lengths = set([len(sentence) for sentence in sentences])
        sentence_length = list(sentence_lengths)[0]
        if len(sentence_lengths) != 1 or sentence_length not in [5, 7]:
            return 0.

        rules = tone_rules[sentence_length]
        scores = map(lambda rule: self.score(rule, sentences, output_split=output_split), rules)

        if output_split:
            max_combined = max([score[0] for score in scores])
            max_tone = max([score[1] for score in scores])
            max_rhyme = max([score[2] for score in scores])

            max_score = (max_combined, max_tone, max_rhyme)
        else:
            max_score = max(scores)

        if output_all_scores:
            return max_score, scores
        else:
            return max_score
