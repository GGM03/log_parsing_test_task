import re
from typing import Dict
from abc import ABC, abstractmethod


class SequenceSegmentExtractor(ABC):

    @abstractmethod
    def extract(self, line: str) -> Dict[str, str]:
        """
        This function must extract data dict from line by using some implemented logic
        :param line: string
        :return: dict of extracted data
        """
        pass

    @abstractmethod
    def crop(self, line: str) -> str:
        """
        This function must separate line in prefix (which can pe used to extract data with this extractor) and suffix,
        which must be passed in next extractor.
        :param line: string
        :return: an unhandled suffix to pass in next extractor
        """


class PositionalExtractor(SequenceSegmentExtractor):
    def __init__(self, values_amount: int, keys_prefix: str = 'param', unescape_values: bool = False):
        r"""
        Extractor, which can process strings in format " value1 | value 2 | value 3|".
        This extractor can handle escaped delimiters, like "\|" (ex: "value 1 \| and \| value 2 " -> one value)
        Amount of handled values must be passed in arguments

        :param values_amount: amount of handled positional values
        :param keys_prefix: positional values prefixes. This value used to construct found values keys by using pattern
            "{keys_prefix}{positional_id}"
        :param unescape_values: This flag will force "unescaping" sequences from found values.
        """
        positional_parts_string_regex = ''.join(
            self.positional_value_regex(keys_prefix, idx) for idx in range(1, values_amount + 1)
        )
        self.regex = re.compile(positional_parts_string_regex, flags=re.VERBOSE)
        # Escape replacements will be applied to every found positional value
        # format: (<escape symbol regex>, <replacement for this symbol>)
        self.escape_replacements = [
            # This rule will translate "\|" into "|"
            (re.compile(r'\\\|'), '|'),
        ]
        self.unescape_values = unescape_values

    @staticmethod
    def positional_value_regex(keys_prefix, positional_id):
        """
        Create regex for extracting values from lines
        :param keys_prefix: prefix, used to construct named capturing group
        :param positional_id: the positional id of capturing group
        :return: string with formatted regex
        """
        return r'''
        (?P<{keys_prefix}{id}>  # named group for extracting values from string
            (?:               # non-capturing group for "OR" statement
                [^|\\]        # any character except "|" (end char) or "\" (escape char)
                |             # or statement
                \\\|          # "\|" escaped "|" char (only this escape sequence supported)
                |             # or statement
                \\            # other escape sequences start
            )*                # zero or more symbols or escape symbols
        )                     # end of named group
        \|                    # trailing "|" symbol (end of value)
        '''.format(keys_prefix=keys_prefix, id=positional_id)

    def unescape_string(self, string: str) -> str:
        """
        This function unescapes sequences by using "self.escape_replacements" rules in string.
        :param string:
        :return: string with replaced chars
        """
        for escape_regex, escape_replacer in self.escape_replacements:
            string = escape_regex.sub(escape_replacer, string)
        return string

    def extract(self, line: str) -> Dict[str, str]:
        match = self.regex.search(line)
        if match:
            data_dict = match.groupdict()
            if self.unescape_values:
                data_dict = {k: self.unescape_string(v) for k, v in data_dict.items()}
            return data_dict
        else:
            return {}

    def crop(self, line: str) -> str:
        return self.regex.sub('', line)


class KeywordExtractor(SequenceSegmentExtractor):
    def __init__(self):
        self.regex = re.compile("""
                [ ]                 # space symbol on start of key=value pair
                ([^ =|]+)           # key definition (any symbol except " ", "|", "=")
                =                   # "=" symbol between parts
                ([^ ].*)            # value or other key=value pairs (any symbols except " " on start of group)
            """, flags=re.VERBOSE)

    def extract(self, line: str) -> Dict[str, str]:
        # Using example: input string: "key1=value1 key2=value2"
        extracted = {}
        match = self.regex.match(line)
        if not match:
            return extracted

        # Separate key value from tail part
        # example: key="key" tail="value1 key2=value2"
        key, tail = match.groups()

        match_in_tail = self.regex.search(tail)
        # If tail has some other pairs "key=value" - search for this part and use all data before next "key=value"
        # as value for current key.
        if match_in_tail:
            current_key_value = tail[:match_in_tail.start()]
            extracted[key] = current_key_value
            # Extracting rest of line and using recursion to extract other keys:
            rest_kw_pairs = tail[match_in_tail.start():]
            # example: key="key", current_key_value="value1", rest_kw_pairs=" key2=value2"
            extracted_from_value = self.extract(rest_kw_pairs)
            # Updating current "extracted" data with other key-value pairs from nested call
            # same keys from current "extracted" will be rewritten with keys from "extracted_from_value"
            extracted.update(extracted_from_value)
        else:
            # If no other "key=value" pairs found, use tail as found key value
            extracted[key] = tail
        return extracted

    def crop(self, line: str) -> str:
        match = self.regex.match(line)
        if not match:
            return ''
        _, tail = match.groups()
        if self.regex.search(tail):
            tail = self.crop(tail)
        return tail
