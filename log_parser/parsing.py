from typing import List, Dict

from .extracting import SequenceSegmentExtractor


class SerialParser:
    def __init__(self, *segment_extractors: SequenceSegmentExtractor):
        """
        This is segment parser, which can work with "SequenceSegmentExtractor" instances.
        :param segment_extractors: instances of SequenceSegmentExtractor
        """
        self.segment_extractors = segment_extractors

    def parseline(self, line: str) -> Dict[str, str]:
        """
        This function execute "segment_extractors" pipeline.
        Each SequenceSegmentExtractor return own chunk of data, which added to "parsed_data" (keys can be overwritten!).
        After extracting useful data, SequenceSegmentExtractor used to crop line.
        Rest of line passed in the other extractor as argument to extract other parts of data.
        :param line: string to parse
        :return: dict with all extracted values
        """
        parsed_data = {}
        for segment_extractor in self.segment_extractors:
            parsed_data.update(segment_extractor.extract(line))
            line = segment_extractor.crop(line)
        return parsed_data

    def parse(self, lines: str) -> List[Dict[str, str]]:
        """
        This function splits different lines and use "self.parseline" to parse each.
        :param lines: string with lines, delimited with "\n"
        :return: list of extracted data, one dict equal to one parsed line.
        """
        parsed_data = []
        for line in lines.split('\n'):
            if line:
                parsed_data.append(self.parseline(line.strip()))
        return parsed_data
