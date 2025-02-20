"""
Module to provide helper functions for parsing.
"""

import logging
from typing import Any, List, Optional, Tuple

from pymarkdown.general.constants import Constants

LOGGER = logging.getLogger(__name__)


# pylint: disable=too-many-public-methods
class ParserHelper:
    """
    Class to provide helper functions for parsing.
    """

    __backspace_character = "\b"
    __alert_character = "\a"
    whitespace_split_character = "\x02"
    replace_noop_character = "\x03"
    escape_character = "\x05"

    backslash_character = "\\"
    newline_character = "\n"
    tab_character = "\t"
    space_character = " "

    all_escape_characters = (
        f"{__backspace_character}{__alert_character}{whitespace_split_character}"
        + f"{replace_noop_character}{escape_character}"
    )

    backslash_escape_sequence = f"{backslash_character}{__backspace_character}"

    __normal_whitespace = f" {tab_character}"

    @staticmethod
    def is_character_at_index(
        source_string: str, index_in_string: int, valid_character: str
    ) -> bool:
        """
        Determine if the specified character is at a valid location and is the
        specified valid character.
        """

        return (
            0 <= index_in_string < len(source_string)
            and source_string[index_in_string] == valid_character
        )

    @staticmethod
    def are_characters_at_index(
        source_string: str, index_in_string: int, string_to_match: str
    ) -> bool:
        """
        Determine if the specified character is at a valid location and is the
        specified valid character.
        """

        test_index = index_in_string + len(string_to_match)
        return (
            index_in_string >= 0
            and test_index <= len(source_string)
            and source_string[index_in_string:test_index] == string_to_match
        )

    @staticmethod
    def is_character_at_index_not(
        source_string: str, index_in_string: int, valid_character: str
    ) -> bool:
        """
        Determine if the specified character is at a valid location and is
        not the specified valid character.
        """

        return (
            0 <= index_in_string < len(source_string)
            and source_string[index_in_string] != valid_character
        )

    @staticmethod
    def is_character_at_index_whitespace(
        source_string: str, index_in_string: int
    ) -> bool:
        """
        Determine if the specified character is valid and a whitespace character.
        """

        return (
            0 <= index_in_string < len(source_string)
            and source_string[index_in_string] in ParserHelper.__normal_whitespace
        )

    @staticmethod
    def is_character_at_index_not_whitespace(
        source_string: str, index_in_string: int
    ) -> bool:
        """
        Determine if the specified character is valid and not a whitespace character.
        """

        return (
            0 <= index_in_string < len(source_string)
            and source_string[index_in_string] not in ParserHelper.__normal_whitespace
        )

    @staticmethod
    def is_character_at_index_one_of(
        source_string: str, index_in_string: int, valid_characters: str
    ) -> bool:
        """
        Determine if the specified character is at a valid location and is one
        of the specified valid characters.
        """

        return (
            0 <= index_in_string < len(source_string)
            and source_string[index_in_string] in valid_characters
        )

    @staticmethod
    def is_character_at_index_not_one_of(
        source_string: str, index_in_string: int, valid_characters: str
    ) -> bool:
        """
        Determine if the specified character is at a valid location and is not one
        of the specified valid characters.
        """

        return (
            0 <= index_in_string < len(source_string)
            and source_string[index_in_string] not in valid_characters
        )

    @staticmethod
    def extract_spaces(
        source_string: str, start_index: int
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        From the start_index, continue extracting whitespace while we have it.

        Returns the index of the first non-whitespace character and any extracted
        whitespace in a tuple.
        """

        if not 0 <= start_index <= len(source_string):
            return None, None

        index = start_index
        while ParserHelper.is_character_at_index_whitespace(source_string, index):
            index += 1

        return index, source_string[start_index:index]

    @staticmethod
    def extract_ascii_whitespace(
        source_string: str, start_index: int
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        From the start_index, continue extracting whitespace while we have it.

        Returns the index of the first non-whitespace character and any extracted
        whitespace in a tuple.
        """

        if not 0 <= start_index <= len(source_string):
            return None, None

        index = start_index
        while ParserHelper.is_character_at_index_one_of(
            source_string, index, Constants.ascii_whitespace
        ):
            index += 1

        return index, source_string[start_index:index]

    @staticmethod
    def extract_spaces_from_end(
        source_string: str, start_index: Optional[int] = None
    ) -> Tuple[int, str]:
        """
        From the end of the string, continue extracting whitespace while we have it.

        Returns the index of the last non-whitespace character and any extracted whitespace
        in a tuple.
        """
        if not source_string:
            return 0, ""

        index = (
            (start_index - 1) if start_index is not None else (len(source_string) - 1)
        )
        while ParserHelper.is_character_at_index_whitespace(source_string, index):
            index -= 1

        # if start_index is not None:
        #     return index + 1, source_string[index + 1 : start_index]
        return index + 1, source_string[index + 1 :]

    @staticmethod
    def extract_until_spaces(
        source_string: str, start_index: int
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        From the start_index, continue extracting until we hit whitespace.

        Returns the index of the first whitespace character and any extracted text
        in a tuple.
        """

        if not 0 <= start_index <= len(source_string):
            return None, None

        index = start_index
        while ParserHelper.is_character_at_index_not_whitespace(source_string, index):
            index += 1

        return index, source_string[start_index:index]

    @staticmethod
    def collect_while_character(
        source_string: str, start_index: int, match_character: str
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Collect a sequence of the same character from a given starting point in a string.

        Returns the number of characters collected and the index of the first non-matching
        character and any extracted text in a tuple.
        """

        source_string_size = len(source_string)

        if not 0 <= start_index <= source_string_size:
            return None, None

        index = start_index
        while index < source_string_size and source_string[index] == match_character:
            index += 1
        return index - start_index, index

    @staticmethod
    def collect_backwards_while_spaces(
        source_string: str, end_index: int
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Collect from a given starting point in a string going backwards
        towards the start of the string while the character is a space character
        or a tab character.

        Returns the number of characters collected and the index of the first non-matching
        character and any extracted text in a tuple.
        """
        return ParserHelper.collect_backwards_while_one_of_characters(
            source_string, end_index, ParserHelper.__normal_whitespace
        )

    @staticmethod
    def collect_backwards_while_character(
        source_string: str, end_index: int, match_character: str
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Collect a sequence of the same character from a given starting point in a
        string going backwards towards the start of the string.

        Returns the number of characters collected and the index of the first non-matching
        character and any extracted text in a tuple.
        """

        source_string_size = len(source_string)
        if not -1 <= end_index <= source_string_size:
            return None, None
        if end_index == -1:
            end_index = source_string_size

        index = end_index
        while index and source_string[index - 1] == match_character:
            index -= 1
        return end_index - index, index

    @staticmethod
    def collect_backwards_while_one_of_characters(
        source_string: str, end_index: int, match_characters: str
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Collect a sequence of the same character from a given starting point in
        a string going backwards towards the start of the string.

        Returns the number of characters collected and the index of the first non-matching
        character and any extracted text in a tuple.
        """

        source_string_size = len(source_string)
        if not -1 <= end_index <= source_string_size:
            return None, None
        if end_index == -1:
            end_index = source_string_size

        index = end_index
        while index and source_string[index - 1] in match_characters:
            index -= 1
        return end_index - index, index

    @staticmethod
    def collect_until_character(
        source_string: str, start_index: int, match_character: str
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        Collect a sequence of characters from a given starting point in a string until we hit a given character.

        Returns the index of the first non-matching character and any extracted text
        in a tuple.
        """

        source_string_size = len(source_string)
        if not 0 <= start_index <= source_string_size:
            return None, None

        index = start_index
        while index < source_string_size and source_string[index] != match_character:
            index += 1

        return index, source_string[start_index:index]

    @staticmethod
    def collect_while_spaces(
        source_string: str, start_index: int
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        Collect characters from a given starting point in a string as long
        as the character is either a string or a tab character.

        Returns the index of the first non-matching character and any extracted text
        in a tuple.
        """
        return ParserHelper.collect_while_one_of_characters(
            source_string, start_index, ParserHelper.__normal_whitespace
        )

    @staticmethod
    def collect_while_one_of_characters(
        source_string: str, start_index: int, match_characters: str
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        Collect a sequence of characters from a given starting point in a string as long
        as the character is one of the match characters.

        Returns the index of the first non-matching character and any extracted text
        in a tuple.
        """

        source_string_size = len(source_string)
        if not 0 <= start_index <= source_string_size:
            return None, None

        index = start_index
        while index < source_string_size and source_string[index] in match_characters:
            index += 1

        return index, source_string[start_index:index]

    @staticmethod
    def collect_until_one_of_characters(
        source_string: str, start_index: int, match_characters: str
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        Collect a sequence of characters from a given starting point in a string until
        we hit one of a given set of characters.

        Returns the index of the first non-matching character and any extracted text
        in a tuple.
        """

        source_string_size = len(source_string)
        if not 0 <= start_index <= source_string_size:
            return None, None

        index = start_index
        while (
            index < source_string_size and source_string[index] not in match_characters
        ):
            index += 1

        return index, source_string[start_index:index]

    @staticmethod
    def index_any_of(source_text: str, find_any: str, start_index: int = 0) -> int:
        """
        Determine if any of the specified characters are in the source string.
        """

        first_index = -1
        for next_character in find_any:
            found_index = source_text.find(next_character, start_index)
            if found_index != -1:
                first_index = (
                    found_index if first_index == -1 else min(first_index, found_index)
                )
                if first_index == 0:
                    break
        return first_index

    @staticmethod
    def replace_any_of(
        string_to_search_in: str, characters_to_search_for: str, replace_with: str
    ) -> str:
        """
        Replace any of a given set of characters with a given sequence.
        """

        start_index = 0
        index, ex_str = ParserHelper.collect_until_one_of_characters(
            string_to_search_in, start_index, characters_to_search_for
        )
        assert index is not None
        assert ex_str is not None
        string_to_search_in_size = len(string_to_search_in)
        replaced_parts: List[str] = []
        while index < string_to_search_in_size:
            replaced_parts.extend([ex_str, replace_with])
            start_index = index + 1
            index, ex_str = ParserHelper.collect_until_one_of_characters(
                string_to_search_in, start_index, characters_to_search_for
            )
            assert index is not None
            assert ex_str is not None
        replaced_parts.append(ex_str)
        return "".join(replaced_parts)

    @staticmethod
    def count_characters_in_text(text_to_examine: str, text_to_look_for: str) -> int:
        """
        Count the number of a given character in a given string.
        """
        original_length = len(text_to_examine)
        removed_length = len(text_to_examine.replace(text_to_look_for, ""))
        return original_length - removed_length

    @staticmethod
    def count_newlines_in_text(text_to_examine: str) -> int:
        """
        Count the number of new line characters in a given string.
        """
        return ParserHelper.count_characters_in_text(
            text_to_examine, ParserHelper.newline_character
        )

    @staticmethod
    def count_newlines_in_texts(*args: Any) -> int:
        """
        Count the number of new line characters in a given string.
        """
        return sum(
            ParserHelper.count_characters_in_text(
                next_argument, ParserHelper.newline_character
            )
            for next_argument in args
        )

    @staticmethod
    def calculate_deltas(text_to_analyze: str) -> Tuple[int, int]:
        """
        Calculate the deltas associated with a given string.
        """

        delta_line_number = 0
        if ParserHelper.newline_character in text_to_analyze:
            split_raw_tag = text_to_analyze.split(ParserHelper.newline_character)
            delta_line_number += len(split_raw_tag) - 1

            last_element = ParserHelper.__resolve_replacement_markers_from_text(
                split_raw_tag[-1]
            )
            last_element = ParserHelper.__remove_escapes_from_text(last_element)
            length_of_last_elements = len(last_element)

            delta_column_number = -(length_of_last_elements + 1)
        else:
            delta_column_number = len(text_to_analyze)
        return delta_line_number, delta_column_number

    # pylint: disable=too-many-arguments
    @staticmethod
    def recombine_string_with_whitespace(
        text_string: str,
        whitespace_string: str,
        start_index: int = 0,
        add_replace_marker_if_empty: bool = False,
        post_increment_index: bool = False,
        start_text_index: int = 1,
        add_whitespace_after: bool = False,
    ) -> Tuple[str, int]:
        """
        Properly recombine a text-string with a matching whitespace-string.
        """
        split_text_string, split_whitespace_string = (
            text_string.split(ParserHelper.newline_character),
            whitespace_string.split(ParserHelper.newline_character),
        )
        for i in range(start_text_index, len(split_text_string)):
            if not post_increment_index:
                start_index += 1
            ew_part = split_whitespace_string[start_index]
            if ew_part and add_replace_marker_if_empty:
                ew_part = ParserHelper.create_replace_with_nothing_marker(ew_part)
            split_text_string[i] = (
                f"{split_text_string[i]}{ew_part}"
                if add_whitespace_after
                else f"{ew_part}{split_text_string[i]}"
            )
            if post_increment_index:
                start_index += 1
        return ParserHelper.newline_character.join(split_text_string), start_index

    # pylint: enable=too-many-arguments

    @staticmethod
    def calculate_last_line(text_string: str) -> str:
        """
        Determine the last line of a multi-line string.
        """
        return text_string.split(ParserHelper.newline_character)[-1]

    @staticmethod
    def make_value_visible(value_to_modify: Any) -> str:
        """
        For the given value, turn it into a string if necessary, and then replace
        any known "invisible" characters with more visible strings.
        """
        return (
            str(value_to_modify)
            .replace(ParserHelper.__backspace_character, "\\b")
            .replace(ParserHelper.__alert_character, "\\a")
            .replace(ParserHelper.tab_character, "\\t")
            .replace(ParserHelper.newline_character, "\\n")
            .replace(ParserHelper.whitespace_split_character, "\\x02")
            .replace(ParserHelper.replace_noop_character, "\\x03")
            .replace(ParserHelper.escape_character, "\\x05")
            .replace("\\x07", "\\a")
            .replace("\\x08", "\\b")
        )

    @staticmethod
    def make_whitespace_visible(value_to_modify: str) -> str:
        """
        For the given value, turn it into a string if necessary, and then replace
        any known whitespace characters with more visible strings.
        """
        # sourcery skip: remove-unnecessary-cast
        return (
            str(value_to_modify)
            .replace(ParserHelper.newline_character, "\\n")
            .replace(" ", "\\s")
        )

    @staticmethod
    def valid_characters_to_escape() -> str:
        """
        List of valid characters that can be escaped.
        """
        return ParserHelper.all_escape_characters

    @staticmethod
    def escape_special_characters(string_to_escape: str) -> str:
        """
        Build another string that has any special characters in the argument escaped.
        """
        string_parts = []
        for next_char_index, next_character in enumerate(string_to_escape):
            if ParserHelper.is_character_at_index_one_of(
                string_to_escape, next_char_index, ParserHelper.all_escape_characters
            ):
                string_parts.append(ParserHelper.escape_character)
            string_parts.append(next_character)
        return "".join(string_parts)

    @staticmethod
    def __remove_backspaces_from_text(token_text: str) -> str:
        """
        Remove any backspaces from the text.
        """
        adjusted_text_token = token_text[:]
        next_backspace_index = ParserHelper.__find_with_escape(
            adjusted_text_token, ParserHelper.__backspace_character, 0
        )
        while next_backspace_index != -1:
            adjusted_text_token = (
                adjusted_text_token[:next_backspace_index]
                + adjusted_text_token[next_backspace_index + 1 :]
            )
            next_backspace_index = ParserHelper.__find_with_escape(
                adjusted_text_token,
                ParserHelper.__backspace_character,
                next_backspace_index,
            )
        return adjusted_text_token

    @staticmethod
    def resolve_backspaces_from_text(token_text: str) -> str:
        """
        Deal with any backslash encoding in text with backspaces.
        """
        adjusted_text_token = token_text[:]
        next_backspace_index = ParserHelper.__find_with_escape(
            adjusted_text_token, ParserHelper.__backspace_character, 0
        )
        while next_backspace_index != -1:
            adjusted_text_token = (
                adjusted_text_token[: next_backspace_index - 1]
                + adjusted_text_token[next_backspace_index + 1 :]
            )
            next_backspace_index = ParserHelper.__find_with_escape(
                adjusted_text_token,
                ParserHelper.__backspace_character,
                next_backspace_index,
            )
        return adjusted_text_token

    @staticmethod
    def create_replacement_markers(
        replace_this_string: str, with_this_string: str
    ) -> str:
        """
        Create a replacement marker indicating that the first string is being replaced
        by the second string.
        """
        return (
            f"{ParserHelper.__alert_character}{replace_this_string}{ParserHelper.__alert_character}"
            + f"{with_this_string}{ParserHelper.__alert_character}"
        )

    @staticmethod
    def create_replace_with_nothing_marker(replace_this_string: str) -> str:
        """
        Create a replacement marker of the given string with the noop character.
        """
        return (
            f"{ParserHelper.__alert_character}{replace_this_string}{ParserHelper.__alert_character}"
            + f"{ParserHelper.replace_noop_character}{ParserHelper.__alert_character}"
        )

    @staticmethod
    def __remove_sequence_from_text(token_text: str, sequence_to_remove: str) -> str:
        """
        Resolve the specific character out of the text string.
        """
        adjusted_text_token = token_text[:]
        next_backspace_index = ParserHelper.__find_with_escape(
            adjusted_text_token, sequence_to_remove, 0
        )
        while next_backspace_index != -1:
            adjusted_text_token = (
                adjusted_text_token[:next_backspace_index]
                + adjusted_text_token[next_backspace_index + 1 :]
            )
            next_backspace_index = ParserHelper.__find_with_escape(
                adjusted_text_token, sequence_to_remove, next_backspace_index
            )
        return adjusted_text_token

    @staticmethod
    def resolve_noops_from_text(token_text: str) -> str:
        """
        Resolve the replacement noop character out of the text string.
        """
        return ParserHelper.__remove_sequence_from_text(
            token_text, ParserHelper.replace_noop_character
        )

    @staticmethod
    def __resolve_escapes_from_text(token_text: str) -> str:
        """
        Resolve any escapes from the text, leaving only what they escaped.
        """
        adjusted_text_token = token_text[:]
        next_backspace_index = ParserHelper.__find_with_escape(
            adjusted_text_token, ParserHelper.escape_character, 0
        )
        while next_backspace_index != -1:
            adjusted_text_token = (
                adjusted_text_token[:next_backspace_index]
                + adjusted_text_token[next_backspace_index + 1 :]
            )
            next_backspace_index = ParserHelper.__find_with_escape(
                adjusted_text_token,
                ParserHelper.escape_character,
                next_backspace_index + 1,
            )
        return adjusted_text_token

    @staticmethod
    def __remove_escapes_from_text(token_text: str) -> str:
        """
        Remove any escape characters from the text.
        """
        return ParserHelper.__resolve_escapes_from_text(token_text)

    @staticmethod
    def __resolve_replacement_markers_from_text(main_text: str) -> str:
        """
        Resolve the alert characters (i.e. replacement markers) out of the text string.
        """
        start_replacement_index = ParserHelper.__find_with_escape(
            main_text, ParserHelper.__alert_character, 0
        )
        while start_replacement_index != -1:
            middle_replacement_index = main_text.index(
                ParserHelper.__alert_character, start_replacement_index + 1
            )
            end_replacement_index = main_text.index(
                ParserHelper.__alert_character, middle_replacement_index + 1
            )

            replace_text = main_text[
                start_replacement_index + 1 : middle_replacement_index
            ]

            # It is possible to have one level of nesting, so deal with it.
            if middle_replacement_index + 1 == end_replacement_index:
                inner_start_replacement_index = main_text.index(
                    ParserHelper.__alert_character, end_replacement_index + 1
                )
                inner_middle_replacement_index = main_text.index(
                    ParserHelper.__alert_character, inner_start_replacement_index + 1
                )
                inner_end_replacement_index = main_text.index(
                    ParserHelper.__alert_character, inner_middle_replacement_index + 1
                )
                assert inner_middle_replacement_index + 1 == inner_end_replacement_index
                end_replacement_index = inner_end_replacement_index

            length_before_mod = len(main_text)
            main_text = (
                (
                    main_text[:start_replacement_index]
                    + replace_text
                    + main_text[end_replacement_index + 1 :]
                )
                if start_replacement_index
                else (replace_text + main_text[end_replacement_index + 1 :])
            )
            length_after_mod = len(main_text)
            start_index = (
                end_replacement_index + 1 + (length_after_mod - length_before_mod)
            )
            start_replacement_index = ParserHelper.__find_with_escape(
                main_text, ParserHelper.__alert_character, start_index
            )
        return main_text

    @staticmethod
    def __find_with_escape(
        adjusted_text_token: str, find_char: str, start_index: int
    ) -> int:
        found_index = -1
        while start_index < len(adjusted_text_token):
            start_replacement_index = adjusted_text_token.find(find_char, start_index)
            if (
                start_replacement_index != -1
                and start_replacement_index > 0
                and adjusted_text_token[start_replacement_index - 1]
                == ParserHelper.escape_character
            ):
                start_index = start_replacement_index + 1
            else:
                found_index = start_replacement_index
                break
        return found_index

    @staticmethod
    def __resolve_references_from_text(adjusted_text_token: str) -> str:
        """
        The alert characters signal that a replacement has occurred, so make sure
        we take the right text from the replacement.
        """
        start_replacement_index = ParserHelper.__find_with_escape(
            adjusted_text_token, ParserHelper.__alert_character, 0
        )
        while start_replacement_index != -1:
            middle_replacement_index = adjusted_text_token.index(
                ParserHelper.__alert_character, start_replacement_index + 1
            )
            end_replacement_index = adjusted_text_token.index(
                ParserHelper.__alert_character, middle_replacement_index + 1
            )

            if middle_replacement_index + 1 == end_replacement_index:
                inner_start_replacement_index = adjusted_text_token.index(
                    ParserHelper.__alert_character, end_replacement_index + 1
                )
                inner_middle_replacement_index = adjusted_text_token.index(
                    ParserHelper.__alert_character, inner_start_replacement_index + 1
                )
                inner_end_replacement_index = adjusted_text_token.index(
                    ParserHelper.__alert_character, inner_middle_replacement_index + 1
                )
                replace_text = adjusted_text_token[
                    inner_start_replacement_index + 1 : inner_middle_replacement_index
                ]
                assert inner_middle_replacement_index + 1 == inner_end_replacement_index
                end_replacement_index = inner_end_replacement_index
            else:
                replace_text = adjusted_text_token[
                    middle_replacement_index + 1 : end_replacement_index
                ]

            length_before_mod = len(adjusted_text_token)
            adjusted_text_token = (
                (
                    adjusted_text_token[:start_replacement_index]
                    + replace_text
                    + adjusted_text_token[end_replacement_index + 1 :]
                )
                if start_replacement_index
                else replace_text + adjusted_text_token[end_replacement_index + 1 :]
            )
            length_after_mod = len(adjusted_text_token)
            start_index = (
                end_replacement_index + 1 + (length_after_mod - length_before_mod)
            )
            start_replacement_index = ParserHelper.__find_with_escape(
                adjusted_text_token, ParserHelper.__alert_character, start_index
            )
        return adjusted_text_token

    @staticmethod
    def resolve_all_from_text(text_to_resolve: str) -> str:
        """
        Combination to resolve all of these special characters from the text.
        """
        resolved_text = ParserHelper.resolve_backspaces_from_text(text_to_resolve)
        resolved_text = ParserHelper.__resolve_references_from_text(resolved_text)
        resolved_text = ParserHelper.resolve_noops_from_text(resolved_text)
        return ParserHelper.__resolve_escapes_from_text(resolved_text)

    @staticmethod
    def remove_all_from_text(text_to_remove: str, include_noops: bool = False) -> str:
        """
        Combination to remove all of these special characters from the text.
        """
        removed_text = ParserHelper.__remove_backspaces_from_text(text_to_remove)
        removed_text = ParserHelper.__resolve_replacement_markers_from_text(
            removed_text
        )
        if include_noops:
            removed_text = ParserHelper.resolve_noops_from_text(removed_text)
        return ParserHelper.__remove_escapes_from_text(removed_text)

    @staticmethod
    def repeat_string(string_to_repeat: str, repeat_count: int) -> str:
        """
        Repeat the given character the specified number of times.
        """
        return "".rjust(repeat_count, string_to_repeat)

    @staticmethod
    def find_nth_occurrence(search_in: str, search_for: str, nth: int) -> int:
        """
        Search for the nth (1-based) occurrence of the search_for
        string within the search_in string.
        """

        did_find_last, found_index, start_index = True, -1, 0
        while nth > 0 and did_find_last:
            found_index = search_in.find(search_for, start_index)
            did_find_last = found_index != -1
            if did_find_last:
                start_index = found_index + 1
                nth -= 1
        return found_index if did_find_last else -1

    @staticmethod
    def adjust_for_newlines(
        source_string: str, start_index: int, end_index: int
    ) -> Tuple[int, int]:
        """
        Given the various parameters, determine the column and
        line offsets implied by newline characters in the
        specified text.
        """

        col_adjust, line_adjust, newline_index = (
            end_index,
            0,
            source_string.find(ParserHelper.newline_character, start_index),
        )
        while newline_index != -1 and newline_index < end_index:
            line_adjust += 1
            col_adjust, newline_index = -(
                end_index - newline_index
            ), source_string.find(ParserHelper.newline_character, newline_index + 1)
        return col_adjust, line_adjust


# pylint: enable=too-many-public-methods
