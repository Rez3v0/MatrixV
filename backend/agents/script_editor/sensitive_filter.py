import ahocorasick

class SensitiveFilter:
    """
    敏感词过滤引擎，基于 Aho-Corasick 多模式匹配算法。
    """
    def __init__(self, bad_words: list[str] = None):
        self.automaton = ahocorasick.Automaton()
        
        # 默认内置的一些敏感词测试用例
        default_bad_words = ["傻逼", "弱智", "黄片", "赌博"]
        words_to_add = bad_words if bad_words else default_bad_words
        
        for idx, word in enumerate(words_to_add):
            self.automaton.add_word(word, (idx, word))
            
        self.automaton.make_automaton()

    def find_all(self, text: str) -> list[str]:
        """
        查找文本中包含的所有敏感词。
        :return: 敏感词列表
        """
        found_words = set()
        for end_index, (insert_order, original_value) in self.automaton.iter(text):
            found_words.add(original_value)
        return list(found_words)

    def contains_sensitive_words(self, text: str) -> bool:
        """快速判断是否包含敏感词"""
        for _ in self.automaton.iter(text):
            return True
        return False
        
    def replace_sensitive_words(self, text: str, replace_char: str = "*") -> str:
        """
        替换敏感词为指定字符。
        由于 Aho-Corasick 返回的是结束索引，为了精确替换，需要一些字符串切片处理。
        （此处为简化版的贪婪替换，实际业务中可优化）
        """
        words = self.find_all(text)
        for w in words:
            text = text.replace(w, replace_char * len(w))
        return text

sensitive_filter = SensitiveFilter()
