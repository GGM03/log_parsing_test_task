from .parsing import SerialParser
from .extracting import PositionalExtractor, KeywordExtractor

__all__ = ['parse_log_line', 'parse_log_lines']


parser = SerialParser(
    PositionalExtractor(
        7,
        keys_prefix='param',
        escape_replacements=[
            (r'\\\|', '|')
        ]
    ),
    KeywordExtractor(
        escape_replacements=[
            (r'\\\=', '=')
        ]
    )
)

parse_log_line = parser.parseline
parse_log_lines = parser.parse
