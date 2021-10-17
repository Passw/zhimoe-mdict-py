import re
from typing import List

import inflect
from spellchecker import SpellChecker

from mdx.config import MdxIndexBuilders
from mdx.mdict_query import IndexBuilder

sing = inflect.engine()  # 单复数转换
spellchecker = SpellChecker()  # 拼写纠正


def plural2singular(plural) -> str:
    """return singular of the plural word, if the input is not plural then return input """
    singular = sing.singular_noun(plural)
    if not singular:
        return plural
    return singular


error_msg = """
            <link rel="stylesheet" type="text/css" href="O8C.css">
            <span backup-class="unbox_header_1" class="th">
            系统异常，请稍后再试
            </span>"""


def get_definition_mdx(word: str, dict_opt: str) -> str:
    """根据关键字得到MDX词典的解释"""
    dict_index_builder = MdxIndexBuilders[dict_opt]
    try:
        if not word:
            return ""
        word = word.lower()
        raw_result = dict_index_builder.mdx_lookup(word)
        # 复数转为单数
        if len(raw_result) < 1:
            raw_result = dict_index_builder.mdx_lookup(plural2singular(word))
        if len(raw_result) < 1:
            word = spellchecker.correction(word)
            raw_result = dict_index_builder.mdx_lookup(word)
        if len(raw_result) < 1:
            raw_result = dict_index_builder.mdx_lookup(word.upper())
        if len(raw_result) < 1:
            return ""
        # ???
        pattern = re.compile(r"@@@LINK=([\w\s]*)")
        rst = pattern.match(raw_result[0])
        if rst is not None:
            link = rst.group(1).strip()
            raw_result = dict_index_builder.mdx_lookup(link)

        # process the word link in result
        str_content = ""
        if len(raw_result) > 0:
            for c in raw_result:
                str_content += c.replace("\r\n", "").replace("entry:/", "")

        return str_content
    except:
        return error_msg


def get_definition_mdd(word: str, builder: IndexBuilder) -> List[str]:
    """根据关键字得到MDD词典的媒体 """
    word = word.replace("/", "\\")
    content = builder.mdd_lookup(word)
    if len(content) > 0:
        return [content[0]]
    else:
        return []
