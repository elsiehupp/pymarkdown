"""
Module to provide processing for the list blocks.
"""

import logging
import string
from typing import Callable, List, Optional, Tuple

from pymarkdown.block_quote_data import BlockQuoteData
from pymarkdown.container_markdown_token import (
    BlockQuoteMarkdownToken,
    ListStartMarkdownToken,
    NewListItemMarkdownToken,
    OrderedListStartMarkdownToken,
    UnorderedListStartMarkdownToken,
)
from pymarkdown.html_helper import HtmlHelper
from pymarkdown.leaf_block_processor import LeafBlockProcessor
from pymarkdown.markdown_token import MarkdownToken
from pymarkdown.parser_helper import ParserHelper
from pymarkdown.parser_logger import ParserLogger
from pymarkdown.parser_state import ParserState
from pymarkdown.position_marker import PositionMarker
from pymarkdown.requeue_line_info import RequeueLineInfo
from pymarkdown.stack_token import (
    ListStackToken,
    OrderedListStackToken,
    StackToken,
    UnorderedListStackToken,
)

POGGER = ParserLogger(logging.getLogger(__name__))


# pylint: disable=too-many-lines
class ListBlockProcessor:
    """
    Class to provide processing for the list blocks.
    """

    __ulist_start_characters = "-+*"
    __olist_start_characters = ".)"

    @staticmethod
    # pylint: disable=too-many-arguments
    def is_ulist_start(
        parser_state: ParserState,
        line_to_parse: str,
        start_index: int,
        extracted_whitespace: Optional[str],
        skip_whitespace_check: bool,
        adj_ws: Optional[str] = None,
    ) -> Tuple[bool, int, Optional[int], Optional[int]]:
        """
        Determine if we have the start of an un-numbered list.
        """
        POGGER.debug("is_ulist_start>>pre>>")
        POGGER.debug("is_ulist_start>>start_index>>$<<", start_index)
        POGGER.debug("is_ulist_start>>adj_ws>>$<<", adj_ws)
        POGGER.debug("is_ulist_start>>extracted_whitespace>>$<<", extracted_whitespace)
        adj_ws, parent_indent = ListBlockProcessor.__adjust_whitespace_for_nested_lists(
            parser_state,
            extracted_whitespace if adj_ws is None else adj_ws,
            line_to_parse,
            start_index,
        )

        assert adj_ws is not None
        POGGER.debug("skip_whitespace_check>>$", skip_whitespace_check)
        POGGER.debug("len(adj_ws)>>$", len(adj_ws))
        POGGER.debug("parent_indent>>$", parent_indent)

        if (
            ParserHelper.is_length_less_than_or_equal_to(adj_ws, 3 + parent_indent)
            or skip_whitespace_check
        ):
            is_start = ListBlockProcessor.__is_start_ulist(
                line_to_parse, start_index, extracted_whitespace
            )
        else:
            is_start = False
        if is_start:
            (
                is_start,
                after_all_whitespace_index,
            ) = ListBlockProcessor.__is_start_phase_one(
                parser_state, line_to_parse, start_index, False
            )
        else:
            after_all_whitespace_index = -1
        if is_start:
            is_start = ListBlockProcessor.__is_start_phase_two(
                parser_state,
                line_to_parse[start_index],
                True,
                False,
                after_all_whitespace_index,
                line_to_parse,
                start_index,
            )

        return is_start, after_all_whitespace_index, start_index, 0
        # pylint: enable=too-many-arguments

    # pylint: disable=too-many-arguments
    @staticmethod
    def is_olist_start(
        parser_state: ParserState,
        line_to_parse: str,
        start_index: int,
        extracted_whitespace: Optional[str],
        skip_whitespace_check: bool,
        adj_ws: Optional[str] = None,
    ) -> Tuple[bool, int, Optional[int], Optional[int]]:
        """
        Determine if we have the start of a numbered or ordered list.
        """

        POGGER.debug("is_olist_start>>pre>>")
        POGGER.debug("is_olist_start>>start_index>>$<<", start_index)
        POGGER.debug("is_olist_start>>adj_ws>>$<<", adj_ws)
        POGGER.debug("is_olist_start>>extracted_whitespace>>$<<", extracted_whitespace)
        adj_ws, parent_indent = ListBlockProcessor.__adjust_whitespace_for_nested_lists(
            parser_state,
            extracted_whitespace if adj_ws is None else adj_ws,
            line_to_parse,
            start_index,
        )
        POGGER.debug("after_adjust>>ws=$=", adj_ws)
        POGGER.debug("after_adjust>>parent_indent=$=", parent_indent)

        assert adj_ws is not None

        POGGER.debug("skip_whitespace_check>>$", skip_whitespace_check)
        POGGER.debug("len(adj_ws)>>$", len(adj_ws))

        if (
            ParserHelper.is_length_less_than_or_equal_to(adj_ws, 3 + parent_indent)
            or skip_whitespace_check
        ):
            (
                is_start,
                index,
                number_of_digits,
                is_not_one,
            ) = ListBlockProcessor.__is_start_olist(line_to_parse, start_index)
        else:
            is_start, index, number_of_digits, is_not_one = False, None, None, False
        if is_start:
            assert index is not None
            assert is_not_one is not None
            (
                is_start,
                after_all_whitespace_index,
            ) = ListBlockProcessor.__is_start_phase_one(
                parser_state, line_to_parse, index, is_not_one
            )
        else:
            after_all_whitespace_index = -1
        if is_start:
            assert index is not None
            assert is_not_one is not None
            is_start = ListBlockProcessor.__is_start_phase_two(
                parser_state,
                line_to_parse[index],
                False,
                is_not_one,
                after_all_whitespace_index,
                line_to_parse,
                start_index,
            )

        return is_start, after_all_whitespace_index, index, number_of_digits

    # pylint: enable=too-many-arguments

    @staticmethod
    def __is_start_ulist(
        line_to_parse: str, start_index: int, extracted_whitespace: Optional[str]
    ) -> bool:
        is_start = ParserHelper.is_character_at_index_one_of(
            line_to_parse, start_index, ListBlockProcessor.__ulist_start_characters
        )

        # Thematic breaks have precedence, so stop a list start if we find one.
        if is_start:
            is_break, _ = LeafBlockProcessor.is_thematic_break(
                line_to_parse, start_index, extracted_whitespace
            )
            is_start = is_start and not is_break
        return is_start

    @staticmethod
    def __is_start_olist(
        line_to_parse: str, start_index: int
    ) -> Tuple[bool, Optional[int], Optional[int], Optional[bool]]:
        is_start = ParserHelper.is_character_at_index_one_of(
            line_to_parse, start_index, string.digits
        )
        if is_start:
            index, olist_index_number = ParserHelper.collect_while_one_of_characters(
                line_to_parse, start_index, string.digits
            )
            assert olist_index_number is not None
            assert index is not None
            number_of_digits = len(olist_index_number)

            POGGER.debug("olist?$<<count>>$<<", olist_index_number, number_of_digits)
            is_not_one = olist_index_number != "1"
            is_start = (
                number_of_digits <= 9
                and ParserHelper.is_character_at_index_one_of(
                    line_to_parse, index, ListBlockProcessor.__olist_start_characters
                )
            )
        else:
            index, number_of_digits, is_not_one = None, None, None

        POGGER.debug("is_olist_start>>$", is_start)
        return is_start, index, number_of_digits, is_not_one

    @staticmethod
    def __determine_child_and_parent_tokens(
        parser_state: ParserState,
    ) -> Tuple[Optional[ListStackToken], Optional[ListStackToken]]:
        child_list_token, parent_list_token = None, None
        if parser_state.token_stack[-1].is_list:
            child_list_token = parser_state.token_stack[-1]
            if (
                len(parser_state.token_stack) > 1
                and parser_state.token_stack[-2].is_list
            ):
                parent_list_token = parser_state.token_stack[-2]
        elif len(parser_state.token_stack) > 1 and parser_state.token_stack[-2].is_list:
            child_list_token = parser_state.token_stack[-2]
            if (
                len(parser_state.token_stack) > 2
                and parser_state.token_stack[-3].is_list
            ):
                parent_list_token = parser_state.token_stack[-3]
        POGGER.debug("child_list_token>>$", child_list_token)
        POGGER.debug("parent_list_token>>$", parent_list_token)
        return child_list_token, parent_list_token

    @staticmethod
    def __adjust_whitespace_for_nested_lists(
        parser_state: ParserState,
        adj_ws: Optional[str],
        line_to_parse: str,
        start_index: int,
    ) -> Tuple[Optional[str], int]:

        assert adj_ws is not None
        (
            child_list_token,
            parent_list_token,
        ) = ListBlockProcessor.__determine_child_and_parent_tokens(parser_state)
        POGGER.debug("len(adj_ws)>>$", len(adj_ws))

        if child_list_token and parent_list_token:
            parent_indent, child_indent = (
                parent_list_token.indent_level,
                child_list_token.indent_level,
            )
            POGGER.debug("parent_indent>>$", parent_indent)
            POGGER.debug("child_indent>>$", child_indent)
            if len(adj_ws) > parent_indent and len(adj_ws) < child_indent:
                adj_ws = adj_ws[parent_indent:]
        elif child_list_token:
            POGGER.debug("current_start>>$", child_list_token.matching_markdown_token)
            POGGER.debug(
                "current_start.last_new_list_token>>$",
                child_list_token.last_new_list_token,
            )
            POGGER.debug("line_to_parse>>:$:", line_to_parse)
            POGGER.debug("start_index>>$", start_index)

            indent_level = (
                child_list_token.last_new_list_token.indent_level
                if child_list_token.last_new_list_token
                else child_list_token.indent_level
            )
            parent_indent = (
                child_list_token.indent_level if start_index >= indent_level else 0
            )
        else:
            parent_indent = 0
        return adj_ws, parent_indent

    @staticmethod
    def __is_start_phase_one(
        parser_state: ParserState,
        line_to_parse: str,
        start_index: int,
        is_not_one: bool,
    ) -> Tuple[bool, int]:

        start_index += 1
        line_to_parse_size = len(line_to_parse)
        after_all_whitespace_index, _ = ParserHelper.extract_whitespace(
            line_to_parse, start_index
        )
        assert after_all_whitespace_index is not None
        POGGER.debug(
            "after_all_whitespace_index>>$>>len>>$",
            after_all_whitespace_index,
            line_to_parse_size,
        )
        at_end_of_line = after_all_whitespace_index == line_to_parse_size
        POGGER.debug("at_end_of_line>>$", at_end_of_line)

        is_in_paragraph = parser_state.token_stack[-1].is_paragraph
        is_paragraph_in_list = (
            parser_state.token_stack[-2].is_list if is_in_paragraph else False
        )

        is_start = not (
            is_in_paragraph
            and not is_paragraph_in_list
            and (at_end_of_line or is_not_one)
        ) and (
            ParserHelper.is_character_at_index_whitespace(line_to_parse, start_index)
            or ((start_index) == line_to_parse_size)
        )
        return is_start, after_all_whitespace_index

    # pylint: disable=too-many-arguments
    @staticmethod
    def __is_start_phase_two(
        parser_state: ParserState,
        xx_seq: str,
        is_unordered_list: bool,
        is_not_one: bool,
        after_all_whitespace_index: int,
        line_to_parse: str,
        start_index: int,
    ) -> bool:
        (is_in_paragraph, at_end_of_line) = (
            parser_state.token_stack[-1].is_paragraph,
            (after_all_whitespace_index == len(line_to_parse)),
        )

        if is_in_paragraph:
            (
                is_first_item_in_list,
                is_sub_list,
            ) = ListBlockProcessor.__calculate_starts_within_paragraph(
                parser_state, line_to_parse, start_index, is_unordered_list, xx_seq
            )
        else:
            is_first_item_in_list, is_sub_list = False, False

        POGGER.debug(
            "is_in_para>>$(>>EOL>$>>is_not_one>$)>>is_first>$>>is_sub_list>$",
            is_in_paragraph,
            at_end_of_line,
            is_not_one,
            is_first_item_in_list,
            is_sub_list,
        )
        return not (
            is_in_paragraph
            and (at_end_of_line or is_not_one)
            and is_first_item_in_list
            and is_sub_list
        )

    # pylint: enable=too-many-arguments

    @staticmethod
    def __calculate_starts_within_paragraph(
        parser_state: ParserState,
        line_to_parse: str,
        start_index: int,
        is_unordered_list: bool,
        xx_seq: str,
    ) -> Tuple[bool, bool]:
        is_first_item_in_list = True
        if not parser_state.token_stack[-2].is_list:
            POGGER.debug("top of stack is not list>>$", parser_state.token_stack[-2])
        elif is_unordered_list and parser_state.token_stack[-2].is_ordered_list:
            POGGER.debug(
                "top of stack is ordered list>>$", parser_state.token_stack[-2]
            )
        elif xx_seq != parser_state.token_stack[-2].list_character[-1]:
            POGGER.debug(
                "xx>>$!=$",
                line_to_parse[start_index],
                parser_state.token_stack[-2].list_character,
            )
        else:
            is_first_item_in_list = (
                start_index >= parser_state.token_stack[-2].indent_level
            )
            POGGER.debug(
                "start_index>>$>=$",
                start_index,
                parser_state.token_stack[-2].indent_level,
            )
        POGGER.debug("is_first_item_in_list>>$", is_first_item_in_list)

        is_sub_list = (
            parser_state.token_stack[-2].is_list
            and start_index >= parser_state.token_stack[-2].indent_level
        )
        return is_first_item_in_list, is_sub_list

    @staticmethod
    def __get_list_functions(
        is_ulist: bool,
    ) -> Tuple[
        Callable[
            [ParserState, str, int, Optional[str], bool, Optional[str]],
            Tuple[bool, int, Optional[int], Optional[int]],
        ],
        Callable[
            [PositionMarker, int, Optional[str], int, int, int],
            Tuple[ListStartMarkdownToken, ListStackToken],
        ],
    ]:
        if is_ulist:
            POGGER.debug("hlb>>searching for ulist")
            is_start_fn = ListBlockProcessor.is_ulist_start
            create_token_fn = ListBlockProcessor.__handle_list_block_unordered
        else:
            POGGER.debug("hlb>>searching for olist")
            is_start_fn = ListBlockProcessor.is_olist_start
            create_token_fn = ListBlockProcessor.__handle_list_block_ordered
        return is_start_fn, create_token_fn

    @staticmethod
    def __calculate_create_adj_ws(
        adj_ws: Optional[str],
        position_marker: PositionMarker,
        parser_state: ParserState,
    ) -> Optional[str]:
        create_adj_ws = adj_ws
        POGGER.debug("adj_ws=>:$:<", create_adj_ws)
        if position_marker.index_number:
            POGGER.debug("adjusting for nested")
            POGGER.debug("afn>>$", parser_state.token_stack)
            search_index = parser_state.find_last_container_on_stack()
            if parser_state.token_stack[search_index].is_list:
                create_adj_ws = None
        POGGER.debug("create_adj_ws=$=", create_adj_ws)
        return create_adj_ws

    @staticmethod
    def __handle_list_with_leading_indent_loop(
        acceptable_indent_stack_index: int,
        parser_state: ParserState,
        stack_index: int,
        extracted_whitespace: Optional[str],
    ) -> int:
        box_start = 1 if stack_index == 1 else ((stack_index + 1) * 4) + stack_index
        box_end = (stack_index * 4) + (stack_index - 1)

        assert extracted_whitespace is not None
        is_in_this_box = box_start <= len(extracted_whitespace) + 1 <= box_end
        can_promote_to_next_box = (stack_index + 1) < len(
            parser_state.token_stack
        ) and parser_state.token_stack[stack_index + 1].is_list

        # POGGER.debug("ra>$<", box_start)
        # POGGER.debug("rb>$<", box_end)
        # POGGER.debug("is_in_this_box>$<", is_in_this_box)
        # POGGER.debug("can_promote_to_next_box>$<", can_promote_to_next_box)

        if is_in_this_box or can_promote_to_next_box:
            acceptable_indent_stack_index = stack_index
        return acceptable_indent_stack_index

    # pylint: disable=too-many-arguments
    @staticmethod
    def __handle_list_with_leading_indent(
        parser_state: ParserState,
        container_depth: int,
        removed_chars_at_start: int,
        extracted_whitespace: Optional[str],
        indent_already_processed: bool,
        adj_ws: Optional[str],
    ) -> Tuple[int, Optional[str], Optional[str], Optional[str], bool]:

        indent_already_used, forced_container_whitespace = 0, None
        is_in_root_list = (
            not container_depth
            and parser_state.token_stack
            and len(parser_state.token_stack) >= 2
            and parser_state.token_stack[1].is_list
        )

        # POGGER.debug("container_depth>$<", container_depth)
        # POGGER.debug("removed_chars_at_start>$<", removed_chars_at_start)
        # POGGER.debug("is_in_root_list>$<", is_in_root_list)
        assert extracted_whitespace is not None
        if (
            not removed_chars_at_start
            and is_in_root_list
            and adj_ws == extracted_whitespace
            and len(extracted_whitespace) >= 4
            and not indent_already_processed
        ):

            # POGGER.debug("extracted_whitespace>$<", extracted_whitespace)
            # POGGER.debug("parser_state.token_stack>$<", parser_state.token_stack)
            stack_index = 1
            acceptable_indent_stack_index = 0
            while (
                stack_index < len(parser_state.token_stack)
                and parser_state.token_stack[stack_index].is_list
            ):
                acceptable_indent_stack_index = (
                    ListBlockProcessor.__handle_list_with_leading_indent_loop(
                        acceptable_indent_stack_index,
                        parser_state,
                        stack_index,
                        extracted_whitespace,
                    )
                )
                stack_index += 1

            # POGGER.debug("acceptable_indent_stack_index>$<", acceptable_indent_stack_index)
            if acceptable_indent_stack_index:
                indent_already_used = parser_state.token_stack[
                    acceptable_indent_stack_index
                ].matching_markdown_token.indent_level
                forced_container_whitespace = extracted_whitespace[:indent_already_used]
                extracted_whitespace = extracted_whitespace[indent_already_used:]
                adj_ws = adj_ws[indent_already_used:]
                indent_already_processed = True
        return (
            indent_already_used,
            forced_container_whitespace,
            extracted_whitespace,
            adj_ws,
            indent_already_processed,
        )

    # pylint: enable=too-many-arguments

    # pylint: disable=too-many-locals, too-many-arguments
    @staticmethod
    def __handle_list_block_init(
        parser_state: ParserState,
        position_marker: PositionMarker,
        extracted_whitespace: Optional[str],
        adj_ws: Optional[str],
        is_ulist: bool,
        container_depth: int,
        removed_chars_at_start: int,
        indent_already_processed: bool,
    ) -> Tuple[
        Callable[
            [PositionMarker, int, Optional[str], int, int, int],
            Tuple[ListStartMarkdownToken, ListStackToken],
        ],
        bool,
        int,
        Optional[int],
        Optional[int],
        int,
        Optional[str],
        Optional[str],
        Optional[str],
        bool,
    ]:
        POGGER.debug(
            "hlb>>parser_state.nested_list_start>$", parser_state.nested_list_start
        )
        POGGER.debug("hlb>>extracted_whitespace>$<", extracted_whitespace)
        POGGER.debug("hlb>>adj_ws>$<", adj_ws)
        POGGER.debug("hlb>>removed_chars_at_start>$<", removed_chars_at_start)
        POGGER.debug(
            "text_to_parse[index=$:]>:$:<",
            position_marker.index_number,
            position_marker.text_to_parse[position_marker.index_number :],
        )

        (
            indent_already_used,
            forced_container_whitespace,
            extracted_whitespace,
            adj_ws,
            indent_already_processed,
        ) = ListBlockProcessor.__handle_list_with_leading_indent(
            parser_state,
            container_depth,
            removed_chars_at_start,
            extracted_whitespace,
            indent_already_processed,
            adj_ws,
        )

        is_start_fn, create_token_fn = ListBlockProcessor.__get_list_functions(is_ulist)
        (
            started_ulist,
            end_of_ulist_start_index,
            index,
            number_of_digits,
        ) = is_start_fn(
            parser_state,
            position_marker.text_to_parse,
            position_marker.index_number,
            extracted_whitespace,
            False,
            adj_ws,
        )
        return (
            create_token_fn,
            started_ulist,
            end_of_ulist_start_index,
            index,
            number_of_digits,
            indent_already_used,
            forced_container_whitespace,
            extracted_whitespace,
            adj_ws,
            indent_already_processed,
        )

    # pylint: enable=too-many-locals, too-many-arguments

    # pylint: disable=too-many-locals, too-many-arguments
    @staticmethod
    def handle_list_block(
        is_ulist: bool,
        parser_state: ParserState,
        position_marker: PositionMarker,
        extracted_whitespace: Optional[str],
        adj_ws: Optional[str],
        block_quote_data: BlockQuoteData,
        removed_chars_at_start: int,
        current_container_blocks: List[StackToken],
        container_depth: int,
        indent_already_processed: bool,
    ) -> Tuple[
        bool,
        int,
        Optional[str],
        List[MarkdownToken],
        int,
        BlockQuoteData,
        Optional[RequeueLineInfo],
        bool,
        Optional[str],
    ]:
        """
        Handle the processing of a ulist block.
        """
        (
            did_process,
            requeue_line_info,
            old_extracted_whitespace,
            old_indent_already_processed,
        ) = (
            False,
            None,
            extracted_whitespace,
            indent_already_processed,
        )
        adjusted_text_to_parse: Optional[str] = position_marker.text_to_parse
        container_level_tokens: List[MarkdownToken] = []

        (
            create_token_fn,
            started_ulist,
            end_of_ulist_start_index,
            index,
            number_of_digits,
            indent_already_used,
            forced_container_whitespace,
            extracted_whitespace,
            adj_ws,
            indent_already_processed,
        ) = ListBlockProcessor.__handle_list_block_init(
            parser_state,
            position_marker,
            extracted_whitespace,
            adj_ws,
            is_ulist,
            container_depth,
            removed_chars_at_start,
            indent_already_processed,
        )
        POGGER.debug("clt>>list-start=$", started_ulist)
        if started_ulist:

            # if not j:
            #     parser_state.token_stack[j].matching_markdown_token.add_leading_spaces(dfg)

            POGGER.debug("clt>>ulist-start")
            removed_chars_at_start = indent_already_used
            assert index is not None
            assert number_of_digits is not None
            (
                indent_level,
                remaining_whitespace,
                ws_after_marker,
                after_marker_ws_index,
                ws_before_marker,
                container_level_tokens,
                block_quote_data,
            ) = ListBlockProcessor.__pre_list(
                parser_state,
                position_marker.text_to_parse,
                index,
                extracted_whitespace,
                number_of_digits,
                block_quote_data,
                adj_ws,
                position_marker,
            )

            POGGER.debug(
                "total=$;ws-before=$;ws_after=$;start_index=$",
                indent_level,
                ws_before_marker,
                ws_after_marker,
                position_marker.index_number,
            )
            POGGER.debug("extracted_whitespace=$=", extracted_whitespace)
            if indent_level >= 0:
                POGGER.debug("indent_level=$=", indent_level)
                POGGER.debug("ws_before_marker=$=", ws_before_marker)
                POGGER.debug(
                    "forced_container_whitespace=$=", forced_container_whitespace
                )
                create_adj_ws = ListBlockProcessor.__calculate_create_adj_ws(
                    adj_ws, position_marker, parser_state
                )
                (
                    adjusted_text_to_parse,
                    requeue_line_info,
                ) = ListBlockProcessor.__create_new_list(
                    parser_state,
                    position_marker,
                    indent_level,
                    extracted_whitespace,
                    ws_before_marker,
                    ws_after_marker,
                    index,
                    container_level_tokens,
                    remaining_whitespace,
                    after_marker_ws_index,
                    current_container_blocks,
                    create_token_fn,
                    container_depth,
                    adj_ws=create_adj_ws,
                    alt_adj_ws=adj_ws,
                    forced_container_whitespace=forced_container_whitespace,
                )
                did_process = True
        else:
            extracted_whitespace = old_extracted_whitespace
            indent_already_processed = old_indent_already_processed
        return (
            did_process,
            end_of_ulist_start_index,
            adjusted_text_to_parse,
            container_level_tokens,
            removed_chars_at_start,
            block_quote_data,
            requeue_line_info,
            indent_already_processed,
            extracted_whitespace,
        )
        # pylint: enable=too-many-locals, too-many-arguments

    @staticmethod
    def __find_block_quote_before_list(
        parser_state: ParserState,
    ) -> Optional[BlockQuoteMarkdownToken]:
        POGGER.debug_with_visible_whitespace(
            "parser_state.token_stack>$", parser_state.token_stack
        )
        found_block_quote_before_list = None
        token_stack_index = parser_state.find_last_container_on_stack()
        POGGER.debug_with_visible_whitespace("token_stack_index>$", token_stack_index)
        if parser_state.token_stack[token_stack_index].is_list:
            while token_stack_index > 0:
                if parser_state.token_stack[token_stack_index].is_block_quote:
                    found_block_quote_before_list = parser_state.token_stack[
                        token_stack_index
                    ]
                    break
                token_stack_index -= 1
        POGGER.debug_with_visible_whitespace(
            "found_block_quote_before_list>$", found_block_quote_before_list
        )
        return found_block_quote_before_list

    # pylint: disable=too-many-locals, too-many-arguments
    @staticmethod
    def __create_new_list(
        parser_state: ParserState,
        position_marker: PositionMarker,
        indent_level: int,
        extracted_whitespace: Optional[str],
        ws_before_marker: int,
        ws_after_marker: int,
        index: int,
        container_level_tokens: List[MarkdownToken],
        remaining_whitespace: int,
        after_marker_ws_index: int,
        current_container_blocks: List[StackToken],
        create_token_fn: Callable[
            [PositionMarker, int, Optional[str], int, int, int],
            Tuple[ListStartMarkdownToken, ListStackToken],
        ],
        container_depth: int,
        adj_ws: Optional[str] = None,
        alt_adj_ws: Optional[str] = None,
        forced_container_whitespace: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[RequeueLineInfo]]:
        found_block_quote_before_list = (
            ListBlockProcessor.__find_block_quote_before_list(parser_state)
        )
        if found_block_quote_before_list and adj_ws is None and alt_adj_ws is not None:
            adj_ws = alt_adj_ws

        POGGER.debug("ws_before_marker=$=", ws_before_marker)
        POGGER.debug("forced_container_whitespace=$=", forced_container_whitespace)
        if forced_container_whitespace:
            whitespace_to_add: Optional[str] = forced_container_whitespace
            assert whitespace_to_add is not None
            if alt_adj_ws:
                whitespace_to_add += alt_adj_ws
            ws_before_marker += len(forced_container_whitespace)
            indent_level += len(forced_container_whitespace)
            assert alt_adj_ws is not None
            alt_adj_ws += forced_container_whitespace
        else:
            whitespace_to_add = extracted_whitespace if adj_ws is None else adj_ws
        POGGER.debug("ws_before_marker=$=", ws_before_marker)
        POGGER.debug_with_visible_whitespace("whitespace_to_add>$:", whitespace_to_add)
        POGGER.debug_with_visible_whitespace("adj_ws>$<", adj_ws)
        POGGER.debug_with_visible_whitespace("alt_adj_ws>$<", alt_adj_ws)
        new_token, new_stack = create_token_fn(
            position_marker,
            indent_level,
            whitespace_to_add,
            ws_before_marker,
            ws_after_marker,
            index,
        )
        POGGER.debug_with_visible_whitespace("__create_new_list>$", new_token)

        (
            new_container_level_tokens,
            adjusted_text_to_parse,
            requeue_line_info,
        ) = ListBlockProcessor.__post_list(
            parser_state,
            new_stack,
            new_token,
            position_marker.text_to_parse,
            remaining_whitespace,
            after_marker_ws_index,
            indent_level,
            current_container_blocks,
            position_marker,
            adj_ws,
            alt_adj_ws,
            container_depth,
        )
        assert new_container_level_tokens is not None
        container_level_tokens.extend(new_container_level_tokens)
        return adjusted_text_to_parse, requeue_line_info

    # pylint: enable=too-many-locals, too-many-arguments

    # pylint: disable=too-many-arguments
    @staticmethod
    def __handle_list_block_unordered(
        position_marker: PositionMarker,
        indent_level: int,
        extracted_whitespace: Optional[str],
        ws_before_marker: int,
        ws_after_marker: int,
        index: int,
    ) -> Tuple[ListStartMarkdownToken, ListStackToken]:
        # This is done to allow for this function and __handle_list_block_ordered
        # to be called using the same pattern.
        _ = index

        assert extracted_whitespace is not None
        new_token = UnorderedListStartMarkdownToken(
            position_marker.text_to_parse[position_marker.index_number],
            indent_level,
            extracted_whitespace,
            position_marker,
        )

        POGGER.debug("unordered-token-->$", new_token)

        return new_token, UnorderedListStackToken(
            indent_level,
            position_marker.text_to_parse[position_marker.index_number],
            ws_before_marker,
            ws_after_marker,
            position_marker.index_number,
            new_token,
        )

    # pylint: enable=too-many-arguments

    # pylint: disable=too-many-arguments
    @staticmethod
    def __handle_list_block_ordered(
        position_marker: PositionMarker,
        indent_level: int,
        extracted_whitespace: Optional[str],
        ws_before_marker: int,
        ws_after_marker: int,
        index: int,
    ) -> Tuple[ListStartMarkdownToken, ListStackToken]:
        assert extracted_whitespace is not None
        new_token = OrderedListStartMarkdownToken(
            position_marker.text_to_parse[index],
            position_marker.text_to_parse[position_marker.index_number : index],
            indent_level,
            extracted_whitespace,
            position_marker,
        )

        POGGER.debug("ordered-token-->$", new_token)

        return new_token, OrderedListStackToken(
            indent_level,
            position_marker.text_to_parse[position_marker.index_number : index + 1],
            ws_before_marker,
            ws_after_marker,
            position_marker.index_number,
            new_token,
        )

    # pylint: enable=too-many-arguments

    @staticmethod
    def __list_in_process_update_containers(
        parser_state: ParserState,
        ind: Optional[int],
        used_indent: Optional[str],
        was_paragraph_continuation: bool,
        start_index: int,
    ) -> None:
        POGGER.debug(">>used_indent>>$<<", used_indent)
        POGGER.debug(">>was_paragraph_continuation>>$<<", was_paragraph_continuation)
        if used_indent is not None:
            POGGER.debug(
                ">>adj_before>>$<<",
                parser_state.token_stack[ind].matching_markdown_token,
            )
            POGGER.debug(
                "lip>>last_block_token>>$",
                parser_state.token_stack[ind].matching_markdown_token,
            )
            parser_state.token_stack[ind].matching_markdown_token.add_leading_spaces(
                used_indent
            )
            POGGER.debug(
                "lip>>last_block_token>>$",
                parser_state.token_stack[ind].matching_markdown_token,
            )

            POGGER.debug(
                ">>adj_after>>$<<",
                parser_state.token_stack[ind].matching_markdown_token,
            )
        else:
            need_to_add_leading_spaces = False
            stack_index = parser_state.find_last_list_block_on_stack()
            if stack_index > 0:

                assert parser_state.original_line_to_parse is not None

                last_container_index = parser_state.find_last_container_on_stack()
                POGGER.debug("ind=:$:", ind)
                POGGER.debug("parser_state.token_stack=:$:", parser_state.token_stack)
                POGGER.debug(
                    "parser_state.token_stack[ind]=:$:", parser_state.token_stack[ind]
                )
                POGGER.debug(
                    "parser_state.original_line_to_parse=:$:",
                    parser_state.original_line_to_parse,
                )
                POGGER.debug("start_index=:$:", start_index)
                POGGER.debug("stack_index=:$:", stack_index)
                consumed_text = parser_state.original_line_to_parse[:start_index]
                POGGER.debug("consumed_text=:$:", consumed_text)
                back_index = stack_index
                while back_index and parser_state.token_stack[back_index].is_list:
                    back_index -= 1
                POGGER.debug("back_index=:$:", back_index)
                need_to_add_leading_spaces = not (
                    back_index > 0
                    and consumed_text
                    and ">" not in consumed_text
                    and stack_index == last_container_index
                )
                POGGER.debug(
                    "need_to_add_leading_spaces=:$:", need_to_add_leading_spaces
                )

            if need_to_add_leading_spaces:
                POGGER.debug(
                    ">>adj_before>>$<<",
                    parser_state.token_stack[stack_index].matching_markdown_token,
                )

                POGGER.debug(
                    "lip>>last_block_token>>$",
                    parser_state.token_stack[stack_index].matching_markdown_token,
                )
                parser_state.token_stack[
                    stack_index
                ].matching_markdown_token.add_leading_spaces("")
                POGGER.debug(
                    "lip>>last_block_token>>$",
                    parser_state.token_stack[stack_index].matching_markdown_token,
                )

                POGGER.debug(
                    ">>adj_after>>$<<",
                    parser_state.token_stack[stack_index].matching_markdown_token,
                )

    @staticmethod
    def list_in_process(
        parser_state: ParserState,
        line_to_parse: str,
        start_index: int,
        extracted_whitespace: Optional[str],
        ind: Optional[int],
    ) -> Tuple[
        List[MarkdownToken], str, Optional[str], Optional[RequeueLineInfo], bool
    ]:
        """
        Handle the processing of a line where there is a list in process.
        """
        assert extracted_whitespace is not None
        (before_ws_length, leading_space_length,) = (
            parser_state.token_stack[ind].ws_before_marker,
            ParserHelper.calculate_length(extracted_whitespace),
        )
        if parser_state.token_stack[ind].last_new_list_token:
            requested_list_indent = parser_state.token_stack[
                ind
            ].last_new_list_token.indent_level
        else:
            requested_list_indent = parser_state.token_stack[ind].indent_level

        POGGER.debug("!!!!!FOUND>>$", parser_state.token_stack[ind])
        POGGER.debug("!!!!!FOUND>>$", parser_state.token_stack[ind].extra_data)
        POGGER.debug("!!!!!ALL>>$", parser_state.token_stack)
        POGGER.debug("!!!!!ALL>>$", parser_state.token_document)

        POGGER.debug(
            "!!!!!requested_list_indent>>$,before_ws=$",
            requested_list_indent,
            before_ws_length,
        )

        allow_list_continue = ListBlockProcessor.__can_list_continue(
            parser_state,
            line_to_parse,
            start_index,
            extracted_whitespace,
            leading_space_length,
        )

        POGGER.debug(
            "leading_space_length>>$>>requested_list_indent>>$>>is_in_paragraph>>$",
            leading_space_length,
            requested_list_indent,
            parser_state.token_stack[-1].is_paragraph,
        )

        used_indent = None
        was_paragraph_continuation = (
            leading_space_length >= requested_list_indent and allow_list_continue
        )
        if was_paragraph_continuation:

            container_level_tokens: List[MarkdownToken] = []
            POGGER.debug("before>>$>>", line_to_parse)
            (
                line_to_parse,
                used_indent,
            ) = ListBlockProcessor.__adjust_line_for_list_in_process(
                line_to_parse,
                start_index,
                extracted_whitespace,
                leading_space_length,
                requested_list_indent,
            )
            POGGER.debug(
                "after>>$>>$>>",
                line_to_parse,
                used_indent,
            )
        else:
            (
                container_level_tokens,
                line_to_parse,
                used_indent,
                ind,
                requeue_line_info,
                was_paragraph_continuation,
            ) = ListBlockProcessor.__process_list_non_continue(
                parser_state,
                requested_list_indent,
                leading_space_length,
                before_ws_length,
                line_to_parse,
                start_index,
                extracted_whitespace,
                allow_list_continue,
                ind,
            )
            if requeue_line_info:
                return [], line_to_parse, None, requeue_line_info, False

        ListBlockProcessor.__list_in_process_update_containers(
            parser_state, ind, used_indent, was_paragraph_continuation, start_index
        )
        return (
            container_level_tokens,
            line_to_parse,
            used_indent,
            None,
            was_paragraph_continuation,
        )

    @staticmethod
    def __can_list_continue(
        parser_state: ParserState,
        line_to_parse: str,
        start_index: int,
        extracted_whitespace: Optional[str],
        leading_space_length: int,
    ) -> bool:
        started_ulist, _, _, _ = ListBlockProcessor.is_ulist_start(
            parser_state,
            line_to_parse,
            start_index,
            extracted_whitespace,
            True,
        )
        started_olist, _, _, _ = ListBlockProcessor.is_olist_start(
            parser_state,
            line_to_parse,
            start_index,
            extracted_whitespace,
            True,
        )
        return (
            (not parser_state.token_document[-1].is_blank_line)
            if leading_space_length >= 4 and (started_ulist or started_olist)
            else True
        )

    @staticmethod
    def __check_for_paragraph_break(
        parser_state: ParserState,
        line_to_parse: str,
        start_index: int,
        extracted_whitespace: Optional[str],
    ) -> bool:
        is_theme_break, _ = LeafBlockProcessor.is_thematic_break(
            line_to_parse,
            start_index,
            extracted_whitespace,
            skip_whitespace_check=True,
        )
        POGGER.debug("is_theme_break>>$", is_theme_break)
        is_atx_heading, _, _, _ = LeafBlockProcessor.is_atx_heading(
            line_to_parse, start_index, extracted_whitespace, skip_whitespace_check=True
        )
        POGGER.debug("is_atx_heading>>$", is_atx_heading)
        is_fenced_start, _, _, _ = LeafBlockProcessor.is_fenced_code_block(
            line_to_parse, start_index, extracted_whitespace, skip_whitespace_check=True
        )
        POGGER.debug("is_fenced_start>>$", is_fenced_start)
        is_html_start, _ = HtmlHelper.is_html_block(
            line_to_parse,
            start_index,
            extracted_whitespace,
            parser_state.token_stack,
        )
        POGGER.debug("is_html_start>>$", is_html_start)
        return (
            bool(is_theme_break)
            or is_atx_heading
            or is_fenced_start
            or bool(is_html_start)
        )

    # pylint: disable=too-many-arguments
    @staticmethod
    def __process_list_non_continue(
        parser_state: ParserState,
        requested_list_indent: int,
        leading_space_length: int,
        before_ws_length: int,
        line_to_parse: str,
        start_index: int,
        extracted_whitespace: Optional[str],
        allow_list_continue: bool,
        ind: Optional[int],
    ) -> Tuple[
        List[MarkdownToken],
        str,
        Optional[str],
        Optional[int],
        Optional[RequeueLineInfo],
        bool,
    ]:

        POGGER.debug(
            "requested_list_indent>>$<<",
            requested_list_indent,
        )
        original_requested_list_indent = requested_list_indent
        requested_list_indent -= before_ws_length

        POGGER.debug(
            "leading_space_length>>$>>adj requested_list_indent>>$>>$<<",
            leading_space_length,
            requested_list_indent,
            parser_state.token_stack[-1].is_paragraph,
        )

        was_breakable_leaf_detected = ListBlockProcessor.__check_for_paragraph_break(
            parser_state, line_to_parse, start_index, extracted_whitespace
        )

        was_paragraph_continuation = (
            parser_state.token_stack[-1].is_paragraph
            and leading_space_length >= requested_list_indent
            and allow_list_continue
            and not was_breakable_leaf_detected
        )
        if was_paragraph_continuation:
            container_level_tokens: List[MarkdownToken] = []
            POGGER.debug(
                "1>>line_to_parse>>$>>",
                line_to_parse,
            )
            (
                line_to_parse,
                used_indent,
            ) = ListBlockProcessor.__adjust_line_for_list_in_process(
                line_to_parse,
                start_index,
                extracted_whitespace,
                leading_space_length,
                original_requested_list_indent,
            )
            was_paragraph_continuation = used_indent is None
            POGGER.debug(
                ">>line_to_parse>>$>>",
                line_to_parse,
            )
            POGGER.debug(">>used_indent>>$>>", used_indent)
        else:
            POGGER.debug(
                "2>>line_to_parse>>$>>",
                line_to_parse,
            )
            (
                container_level_tokens,
                requeue_line_info,
            ) = ListBlockProcessor.__check_for_list_closures(
                parser_state,
                line_to_parse,
                start_index,
                extracted_whitespace,
                ind,
                leading_space_length,
            )
            POGGER.debug(
                "2>>requeue_line_info>>$>>",
                requeue_line_info,
            )
            if requeue_line_info:
                used_indent = None
                ind = None
                return [], line_to_parse, used_indent, ind, requeue_line_info, False

            (
                line_to_parse,
                used_indent,
                ind,
            ) = ListBlockProcessor.__adjust_for_nested_list(
                parser_state,
                container_level_tokens,
                ind,
                line_to_parse,
                extracted_whitespace,
                start_index,
                before_ws_length,
                leading_space_length,
            )

        return (
            container_level_tokens,
            line_to_parse,
            used_indent,
            ind,
            None,
            was_paragraph_continuation,
        )

    # pylint: enable=too-many-arguments

    # pylint: disable=too-many-arguments
    @staticmethod
    def __adjust_for_nested_list(
        parser_state: ParserState,
        container_level_tokens: List[MarkdownToken],
        ind: Optional[int],
        line_to_parse: str,
        extracted_whitespace: Optional[str],
        start_index: int,
        before_ws_length: int,
        leading_space_length: int,
    ) -> Tuple[str, Optional[str], Optional[int]]:

        POGGER.debug(
            "2>>__check_for_list_closures>>$>>",
            container_level_tokens,
        )
        POGGER.debug(
            "2>>parser_state.token_stack>>$>>",
            parser_state.token_stack,
        )
        POGGER.debug(
            "2>>ind>>$>>",
            ind,
        )

        if container_level_tokens:
            (
                did_find,
                last_list_index,
            ) = LeafBlockProcessor.check_for_list_in_process(parser_state)
            POGGER.debug(
                "2>>did_find>>$>>$>>",
                did_find,
                last_list_index,
            )
            if did_find:
                ind = last_list_index
                found_owning_list = parser_state.token_stack[ind]
            else:
                found_owning_list = None
        else:
            assert parser_state.token_stack[ind].is_list
            found_owning_list = parser_state.token_stack[ind]

        if found_owning_list:
            POGGER.debug(">>in list>>")
            requested_list_indent = (
                (found_owning_list.last_new_list_token.indent_level)
                if found_owning_list.last_new_list_token
                else found_owning_list.indent_level
            )
            POGGER.debug(">>line_to_parse>>$>>", line_to_parse)
            POGGER.debug(">>extracted_whitespace>>$<<", extracted_whitespace)
            POGGER.debug(">>start_index>>$", start_index)
            POGGER.debug(">>requested_list_indent>>$", requested_list_indent)
            POGGER.debug(">>before_ws_length>>$", before_ws_length)
            (
                line_to_parse,
                used_indent,
            ) = ListBlockProcessor.__adjust_line_for_list_in_process(
                line_to_parse,
                start_index,
                extracted_whitespace,
                leading_space_length,
                requested_list_indent,
            )
            POGGER.debug(">>line_to_parse>>$", line_to_parse)
            POGGER.debug(">>used_indent>>$<<", used_indent)
        else:
            used_indent = None
        return line_to_parse, used_indent, ind

    # pylint: enable=too-many-arguments

    # pylint: disable=too-many-arguments, too-many-locals
    @staticmethod
    def __pre_list(
        parser_state: ParserState,
        line_to_parse: str,
        start_index: int,
        extracted_whitespace: Optional[str],
        marker_width_minus_one: int,
        block_quote_data: BlockQuoteData,
        adj_ws: Optional[str],
        position_marker: PositionMarker,
    ) -> Tuple[int, int, int, int, int, List[MarkdownToken], BlockQuoteData]:
        """
        Handle the processing of the first part of the list.
        """
        (
            after_marker_ws_index,
            ws_after_marker,
            ws_before_marker,
            line_to_parse_size,
        ) = ListBlockProcessor.__calculate_whitespace_values(
            line_to_parse, start_index, extracted_whitespace
        )

        POGGER.debug("--$--$", start_index, start_index + 1)
        assert adj_ws is not None
        (
            indent_level,
            remaining_whitespace,
            ws_after_marker,
        ) = ListBlockProcessor.__calculate_indents(
            after_marker_ws_index,
            line_to_parse_size,
            marker_width_minus_one,
            ws_after_marker,
            ws_before_marker,
            adj_ws,
        )

        check_list_nesting = True
        if (
            parser_state.token_stack[-1].is_html_block
            or parser_state.token_stack[-1].is_fenced_code_block
        ):
            did_find, _ = LeafBlockProcessor.check_for_list_in_process(parser_state)
            if not did_find:
                indent_level = -1
                after_marker_ws_index = -1
                POGGER.debug("BAIL!")
        else:
            POGGER.debug("stack:$:", parser_state.token_stack)
            POGGER.debug("document:$:", parser_state.token_document)
            did_find, last_list_index = LeafBlockProcessor.check_for_list_in_process(
                parser_state
            )
            if did_find:
                POGGER.debug(
                    "stack[last_list_index]:$:",
                    parser_state.token_stack[last_list_index],
                )
                POGGER.debug(
                    "stack[last_list_index].mmt:$:",
                    parser_state.token_stack[last_list_index].matching_markdown_token,
                )
                check_list_nesting = False

        if check_list_nesting:
            (
                container_level_tokens,
                block_quote_data,
            ) = ListBlockProcessor.__handle_list_nesting(
                parser_state, block_quote_data, position_marker
            )
        else:
            container_level_tokens = []

        return (
            indent_level,
            remaining_whitespace,
            ws_after_marker,
            after_marker_ws_index,
            ws_before_marker,
            container_level_tokens,
            block_quote_data,
        )
        # pylint: enable=too-many-arguments, too-many-locals

    @staticmethod
    def __calculate_whitespace_values(
        line_to_parse: str, start_index: int, extracted_whitespace: Optional[str]
    ) -> Tuple[int, int, int, int]:
        (
            after_marker_ws_index,
            after_marker_whitespace,
        ) = ParserHelper.extract_whitespace(line_to_parse, start_index + 1)
        assert after_marker_ws_index is not None
        assert after_marker_whitespace is not None
        assert extracted_whitespace is not None
        ws_after_marker, ws_before_marker, line_to_parse_size = (
            ParserHelper.calculate_length(
                after_marker_whitespace, start_index=start_index + 1
            ),
            ParserHelper.calculate_length(extracted_whitespace),
            len(line_to_parse),
        )
        POGGER.debug(
            "after-marker>>$>>total=$", after_marker_whitespace, ws_after_marker
        )
        return (
            after_marker_ws_index,
            ws_after_marker,
            ws_before_marker,
            line_to_parse_size,
        )

    # pylint: disable=too-many-arguments
    @staticmethod
    def __calculate_indents(
        after_marker_ws_index: int,
        line_to_parse_size: int,
        marker_width_minus_one: int,
        ws_after_marker: int,
        ws_before_marker: int,
        adj_ws: str,
    ) -> Tuple[int, int, int]:
        POGGER.debug(
            "--ws_before_marker>>$>>marker_width_minus_one>>$",
            ws_before_marker,
            marker_width_minus_one,
        )
        POGGER.debug(">>>>>XX>>$>>$<<", after_marker_ws_index, line_to_parse_size)
        if after_marker_ws_index == line_to_parse_size and ws_after_marker:
            indent_level, remaining_whitespace, ws_after_marker = (
                2 + marker_width_minus_one + len(adj_ws),
                ws_after_marker,
                0,
            )
        else:
            if after_marker_ws_index == line_to_parse_size and ws_after_marker == 0:
                ws_after_marker += 1

            indent_level = (
                ws_before_marker + 1 + ws_after_marker + marker_width_minus_one
            )
            if ws_after_marker > 4:
                indent_level, remaining_whitespace, ws_after_marker = (
                    indent_level - ws_after_marker + 1,
                    ws_after_marker - 1,
                    1,
                )
            else:
                remaining_whitespace = 0

        POGGER.debug(
            "ws_after_marker>>$<<indent_level<<$<<rem<<$<<",
            ws_after_marker,
            indent_level,
            remaining_whitespace,
        )
        return indent_level, remaining_whitespace, ws_after_marker

    # pylint: enable=too-many-arguments

    @staticmethod
    def __handle_list_nesting(
        parser_state: ParserState,
        block_quote_data: BlockQuoteData,
        position_marker: PositionMarker,
    ) -> Tuple[List[MarkdownToken], BlockQuoteData]:
        """
        Resolve any nesting issues with block quotes.
        """
        POGGER.debug(
            ">>block_quote_data.stack_count>>$>>block_quote_data.current_count>>$",
            block_quote_data.stack_count,
            block_quote_data.current_count,
        )
        container_level_tokens: List[MarkdownToken] = []
        adjusted_stack_count = block_quote_data.stack_count
        while block_quote_data.current_count < adjusted_stack_count:

            assert not container_level_tokens
            last_block_index = parser_state.find_last_block_quote_on_stack()
            previous_last_block_token = parser_state.token_stack[
                last_block_index
            ].matching_markdown_token
            POGGER.debug(
                "last_block_index>>$-->$", last_block_index, previous_last_block_token
            )
            container_level_tokens, _ = parser_state.close_open_blocks_fn(
                parser_state,
                until_this_index=last_block_index,
                include_block_quotes=True,
                include_lists=True,
            )
            POGGER.debug("container_level_tokens>>$", container_level_tokens)
            POGGER.debug("stack>>$", parser_state.token_stack)
            POGGER.debug(
                "last token>>$", parser_state.token_stack[-1].matching_markdown_token
            )
            POGGER.debug("position_marker.line_number>>$", position_marker.line_number)
            last_block_index = parser_state.find_last_block_quote_on_stack()
            POGGER.debug("last_block_index>>$", last_block_index)
            POGGER.debug(
                "parser_state.token_stack[-1]>>$", parser_state.token_stack[-1]
            )
            POGGER.debug(
                "parser_state.token_stack[-1].matching_markdown_token>>$",
                parser_state.token_stack[-1].matching_markdown_token,
            )

            first_conditional = not parser_state.token_stack[-1].matching_markdown_token
            second_conditional = (not first_conditional) and (
                position_marker.line_number
                == parser_state.token_stack[-1].matching_markdown_token.line_number
            )
            third_conditional = parser_state.token_stack[-1].is_block_quote

            secondary_conditionals = (
                first_conditional or second_conditional or third_conditional
            )
            POGGER.debug(
                "secondary_conditionals>>$ = first_conditional:$ or second_conditional:$ or "
                + "third_conditional:$",
                secondary_conditionals,
                first_conditional,
                second_conditional,
                third_conditional,
            )
            all_conditionals = last_block_index and secondary_conditionals
            POGGER.debug(
                "all_conditionals>>$ = last_block_index:$ or a2:$",
                all_conditionals,
                last_block_index,
                secondary_conditionals,
            )
            if all_conditionals:
                ListBlockProcessor.__handle_list_nesting_all_conditionals(
                    parser_state, last_block_index, previous_last_block_token
                )

            adjusted_stack_count -= 1

        if adjusted_stack_count != block_quote_data.stack_count:
            block_quote_data = BlockQuoteData(
                block_quote_data.current_count, adjusted_stack_count
            )
        return container_level_tokens, block_quote_data

    @staticmethod
    def __handle_list_nesting_all_conditionals(
        parser_state: ParserState,
        last_block_index: int,
        previous_last_block_token: BlockQuoteMarkdownToken,
    ) -> None:
        current_last_block_token = parser_state.token_stack[
            last_block_index
        ].matching_markdown_token
        POGGER.debug(
            "last_block_index>>$-->$",
            last_block_index,
            current_last_block_token,
        )

        POGGER.debug(
            "prev>>$<<, current>>$<<",
            previous_last_block_token,
            current_last_block_token,
        )
        removed_leading_spaces = previous_last_block_token.remove_last_leading_space()
        POGGER.debug("removed_leading_spaces>>$<<", removed_leading_spaces)
        assert removed_leading_spaces is not None
        POGGER.debug(
            "prev>>$<<, current>>$<<",
            previous_last_block_token,
            current_last_block_token,
        )
        current_last_block_token.add_leading_spaces(
            removed_leading_spaces, skip_adding_newline=True
        )
        POGGER.debug(
            "prev>>$<<, current>>$<<",
            previous_last_block_token,
            current_last_block_token,
        )

    # pylint: disable=too-many-arguments, too-many-locals
    @staticmethod
    def __post_list(
        parser_state: ParserState,
        new_stack: ListStackToken,
        new_token: ListStartMarkdownToken,
        line_to_parse: str,
        remaining_whitespace: int,
        after_marker_ws_index: int,
        indent_level: int,
        current_container_blocks: List[StackToken],
        position_marker: PositionMarker,
        adj_ws: Optional[str],
        alt_adj_ws: Optional[str],
        container_depth: int,
    ) -> Tuple[Optional[List[MarkdownToken]], Optional[str], Optional[RequeueLineInfo]]:
        """
        Handle the processing of the last part of the list.
        """

        POGGER.debug("new_stack>>$", new_stack)
        POGGER.debug("indent_level>>$", indent_level)

        did_find, last_list_index = LeafBlockProcessor.check_for_list_in_process(
            parser_state
        )
        if did_find:
            POGGER.debug(
                "list-in-process>>$",
                parser_state.token_stack[last_list_index],
            )
            (
                container_level_tokens,
                emit_li,
                requeue_line_info,
            ) = ListBlockProcessor.__close_required_lists_after_start(
                parser_state,
                last_list_index,
                new_stack,
                new_token,
                current_container_blocks,
                container_depth,
            )
            if requeue_line_info:
                return [], None, requeue_line_info
        else:
            POGGER.debug(
                "NOT list-in-process>>$",
                parser_state.token_stack[last_list_index],
            )
            container_level_tokens, _ = parser_state.close_open_blocks_fn(
                parser_state, was_forced=True
            )
        POGGER.debug("container_level_tokens>>$", container_level_tokens)

        assert container_level_tokens is not None
        POGGER.debug("__post_list>>before>>$", container_level_tokens)
        if not did_find or not emit_li:
            POGGER.debug("__post_list>>adding>>$", new_token)
            parser_state.token_stack.append(new_stack)
            container_level_tokens.append(new_token)
        else:
            POGGER.debug("__post_list>>new list item>>")
            assert emit_li
            ListBlockProcessor.__post_list_use_new_list_item(
                parser_state,
                new_token,
                container_level_tokens,
                indent_level,
                position_marker,
                adj_ws,
                alt_adj_ws,
            )
        POGGER.debug(
            "__post_list>>rem>>$>>after_in>>$",
            remaining_whitespace,
            after_marker_ws_index,
        )
        POGGER.debug("__post_list>>after>>$", container_level_tokens)

        parser_state.set_no_para_start_if_empty()
        padded_spaces = ParserHelper.repeat_string(
            ParserHelper.space_character, remaining_whitespace
        )
        return (
            container_level_tokens,
            f"{padded_spaces}{line_to_parse[after_marker_ws_index:]}",
            None,
        )
        # pylint: enable=too-many-arguments, too-many-locals

    # pylint: disable=too-many-arguments
    @staticmethod
    def __post_list_use_new_list_item(
        parser_state: ParserState,
        new_token: ListStartMarkdownToken,
        container_level_tokens: List[MarkdownToken],
        indent_level: int,
        position_marker: PositionMarker,
        adj_ws: Optional[str],
        alt_adj_ws: Optional[str],
    ) -> None:
        POGGER.debug("instead of-->$", new_token)

        stack_index = len(parser_state.token_stack) - 1
        while stack_index and not parser_state.token_stack[stack_index].is_list:
            stack_index -= 1
        if stack_index != len(parser_state.token_stack) - 1:
            POGGER.debug("stack_index>$", stack_index)
            POGGER.debug("parser_state.token_stack>$", parser_state.token_stack)
            POGGER.debug(
                "len(parser_state.token_stack)>$", len(parser_state.token_stack) - 1
            )
            new_tokens, _ = parser_state.close_open_blocks_fn(
                parser_state,
                until_this_index=stack_index + 1,
                include_block_quotes=True,
            )
            POGGER.debug("new_tokens>$", new_tokens)
            POGGER.debug("parser_state.token_stack>$", parser_state.token_stack)
            POGGER.debug(
                "len(parser_state.token_stack)>$", len(parser_state.token_stack) - 1
            )
            container_level_tokens.extend(new_tokens)

        top_stack_item = parser_state.token_stack[-1]
        assert top_stack_item.is_list
        POGGER.debug("new_token>$", new_token)
        POGGER.debug("top_stack_item>$", top_stack_item)
        POGGER.debug("top_stack_item.mmt>$", top_stack_item.matching_markdown_token)
        list_start_content = (
            new_token.list_start_content if new_token.is_ordered_list_start else ""
        )

        POGGER.debug("adj_ws-->:$:<", adj_ws)
        POGGER.debug("alt_adj_ws-->:$:<", alt_adj_ws)
        exws = (
            alt_adj_ws
            if adj_ws is None and alt_adj_ws is not None
            else new_token.extracted_whitespace
        )

        # Replace the "other" list start token with a new list item token.
        # The overwritting of the value of new_token is specifically called for.
        replacement_token = NewListItemMarkdownToken(
            indent_level,
            position_marker,
            exws,
            list_start_content,
        )
        top_stack_item.set_last_new_list_token(replacement_token)
        container_level_tokens.append(replacement_token)

    # pylint: enable=too-many-arguments

    # pylint: disable=too-many-arguments
    @staticmethod
    def __close_required_lists_after_start(
        parser_state: ParserState,
        last_list_index: int,
        new_stack: ListStackToken,
        new_token: ListStartMarkdownToken,
        current_container_blocks: List[StackToken],
        container_depth: int,
    ) -> Tuple[
        Optional[List[MarkdownToken]], Optional[bool], Optional[RequeueLineInfo]
    ]:
        """
        After a list start, check to see if any others need closing.
        """
        POGGER.debug("list-in-process>>$", parser_state.token_stack[last_list_index])
        POGGER.debug(
            "list-in-process.token>>$",
            parser_state.token_stack[last_list_index].matching_markdown_token,
        )
        POGGER.debug("new_token>>$", new_token)
        (
            container_level_tokens,
            requeue_line_info,
        ) = parser_state.close_open_blocks_fn(
            parser_state,
            until_this_index=last_list_index + 1,
            caller_can_handle_requeue=True,
            requeue_reset=True,
        )
        if requeue_line_info:
            return None, None, requeue_line_info

        repeat_check, emit_li_token_instead_of_list_start_token = True, False

        POGGER.debug("token_stack>>$", parser_state.token_stack)
        if (
            not container_depth
            and len(parser_state.token_stack) > 1
            and parser_state.token_stack[1].is_block_quote
        ):
            extra_tokens, _ = parser_state.close_open_blocks_fn(
                parser_state,
                until_this_index=1,
                include_lists=True,
                include_block_quotes=True,
            )
            POGGER.debug("extra_tokens>>$", extra_tokens)
            container_level_tokens.extend(extra_tokens)
            POGGER.debug("token_stack>>$", parser_state.token_stack)
            repeat_check = False

        POGGER.debug("old-stack>>$<<", container_level_tokens)
        while repeat_check:
            (
                repeat_check,
                emit_li_token_instead_of_list_start_token,
                last_list_index,
            ) = ListBlockProcessor.__close_next_level_of_lists(
                parser_state,
                new_stack,
                new_token,
                current_container_blocks,
                container_level_tokens,
                last_list_index,
                container_depth,
            )
        return container_level_tokens, emit_li_token_instead_of_list_start_token, None

    # pylint: enable=too-many-arguments

    # pylint: disable=too-many-arguments, too-many-locals
    @staticmethod
    def __close_next_level_of_lists(
        parser_state: ParserState,
        new_stack: ListStackToken,
        new_token: ListStartMarkdownToken,
        current_container_blocks: List[StackToken],
        container_level_tokens: List[MarkdownToken],
        last_list_index: int,
        container_depth: int,
    ) -> Tuple[bool, bool, int]:
        POGGER.debug("start")

        (
            do_not_emit,
            emit_li_token_instead_of_list_start_token,
            extra_tokens,
        ) = ListBlockProcessor.__are_list_starts_equal(
            parser_state,
            last_list_index,
            new_stack,
            new_token,
            current_container_blocks,
            container_depth,
        )
        POGGER.debug("extra_tokens>>$", extra_tokens)
        POGGER.debug(
            "emit_li_token_instead_of_list_start_token>>$",
            emit_li_token_instead_of_list_start_token,
        )
        POGGER.debug("do_not_emit>>$", do_not_emit)
        container_level_tokens.extend(extra_tokens)
        repeat_check = False
        if do_not_emit:
            (
                did_find,
                last_list_index,
                repeat_check,
            ) = ListBlockProcessor.__close_next_level_of_lists_do_not_emit(
                parser_state,
                new_stack,
                new_token,
                current_container_blocks,
                emit_li_token_instead_of_list_start_token,
                container_level_tokens,
                container_depth,
            )
        else:
            POGGER.debug("post_list>>close open blocks and emit")
            close_tokens, _ = parser_state.close_open_blocks_fn(
                parser_state,
                until_this_index=last_list_index,
                include_lists=True,
                include_block_quotes=True,
            )
            container_level_tokens.extend(close_tokens)

            (
                did_find,
                last_list_index,
            ) = LeafBlockProcessor.check_for_list_in_process(parser_state)
            POGGER.debug(
                "did_find>>$--last_list_index--$",
                did_find,
                last_list_index,
            )
            if did_find:
                POGGER.debug(
                    "ARE-EQUAL>>stack>>$>>new>>$",
                    parser_state.token_stack[last_list_index],
                    new_stack,
                )
                repeat_check = (
                    new_stack.indent_level
                    <= parser_state.token_stack[last_list_index].indent_level
                )
                POGGER.debug("repeat_check>>$", repeat_check)
        return repeat_check, emit_li_token_instead_of_list_start_token, last_list_index

    @staticmethod
    def __close_next_level_of_lists_do_not_emit(
        parser_state: ParserState,
        new_stack: ListStackToken,
        new_token: ListStartMarkdownToken,
        current_container_blocks: List[StackToken],
        emit_li_token_instead_of_list_start_token: bool,
        container_level_tokens: List[MarkdownToken],
        container_depth: int,
    ) -> Tuple[bool, int, bool]:
        POGGER.debug("post_list>>don't emit")
        (
            did_find,
            last_list_index,
        ) = LeafBlockProcessor.check_for_list_in_process(parser_state)
        POGGER.debug("parser_state.token_stack>>$", parser_state.token_stack)
        POGGER.debug(
            "did_find>>$--last_list_index--$",
            did_find,
            last_list_index,
        )
        assert did_find
        POGGER.debug(
            "ARE-EQUAL>>stack>>$>>new>>$",
            parser_state.token_stack[last_list_index],
            new_stack,
        )
        repeat_check = not (
            parser_state.token_stack[last_list_index].type_name == new_stack.type_name
            or new_stack.start_index
            > parser_state.token_stack[last_list_index].start_index
        )
        POGGER.debug("current_container_blocks>>$", current_container_blocks)
        POGGER.debug(
            "emit_li_token_instead_of_list_start_token>:$:  repeat_check:$:",
            emit_li_token_instead_of_list_start_token,
            repeat_check,
        )

        if not repeat_check and not emit_li_token_instead_of_list_start_token:
            assert last_list_index > 0
            parent_list_indent = parser_state.token_stack[last_list_index].indent_level
            POGGER.debug("parent_list_indent>>$", parent_list_indent)
            new_token_column_number = new_token.column_number
            POGGER.debug("new_token_column_number>>$", new_token_column_number)
            assert parser_state.original_line_to_parse is not None
            intermediate_line_content = parser_state.original_line_to_parse[
                parent_list_indent : new_token_column_number - 1
            ]
            POGGER.debug("intermediate_line_content:$:", intermediate_line_content)
            if ">" not in intermediate_line_content:
                close_tokens, _ = parser_state.close_open_blocks_fn(
                    parser_state,
                    until_this_index=last_list_index,
                    include_block_quotes=True,
                )
                if close_tokens:
                    container_level_tokens.extend(close_tokens)
                    assert not container_depth
                    delta = (
                        new_token.column_number
                        - parser_state.token_stack[
                            last_list_index
                        ].matching_markdown_token.column_number
                    )
                    new_token.set_extracted_whitespace("".rjust(delta, " "))
        return did_find, last_list_index, repeat_check

    # pylint: enable=too-many-arguments, too-many-locals

    # pylint: disable=too-many-arguments
    @staticmethod
    def __are_list_starts_equal(
        parser_state: ParserState,
        last_list_index: int,
        new_stack: ListStackToken,
        new_token: ListStartMarkdownToken,
        current_container_blocks: List[StackToken],
        container_depth: int,
    ) -> Tuple[bool, bool, List[MarkdownToken]]:
        """
        Check to see if the list starts are equal, and hence a continuation of
        the current list.
        """

        POGGER.debug(
            "ARE-EQUAL>>stack>>$>>new>>$",
            parser_state.token_stack[last_list_index],
            new_stack,
        )
        if parser_state.token_stack[last_list_index] == new_stack:
            balancing_tokens, _ = parser_state.close_open_blocks_fn(
                parser_state,
                until_this_index=last_list_index,
                include_block_quotes=True,
            )
            return True, True, balancing_tokens

        document_token_index = len(parser_state.token_document) - 1
        while document_token_index >= 0 and not (
            parser_state.token_document[document_token_index].is_any_list_token
        ):
            document_token_index -= 1
        assert document_token_index >= 0

        POGGER.debug(
            "ARE-EQUAL>>Last_List_token=$",
            parser_state.token_document[document_token_index],
        )
        old_start_index, old_last_marker_character, current_start_index = (
            parser_state.token_document[document_token_index].indent_level,
            parser_state.token_stack[last_list_index].list_character[-1],
            new_stack.ws_before_marker,
        )
        POGGER.debug(
            "old>>$>>$",
            parser_state.token_stack[last_list_index].extra_data,
            old_last_marker_character,
        )
        POGGER.debug("new>>$>>$", new_stack.extra_data, new_stack.list_character[-1])
        if (
            parser_state.token_stack[last_list_index].type_name == new_stack.type_name
            and old_last_marker_character == new_stack.list_character[-1]
        ):
            balancing_tokens = []
            POGGER.debug("new_stack>$<", new_stack)
            POGGER.debug("new_stack>$<", new_stack.matching_markdown_token)
            POGGER.debug("old_stack>$<", parser_state.token_stack[last_list_index])
            POGGER.debug(
                "old_stack>$<",
                parser_state.token_stack[last_list_index].matching_markdown_token,
            )
            emit_li_token_instead_of_list_start_token = (
                ListBlockProcessor.__process_eligible_list_start(
                    parser_state,
                    balancing_tokens,
                    current_start_index,
                    old_start_index,
                    current_container_blocks,
                    new_stack,
                )
            )
            return True, emit_li_token_instead_of_list_start_token, balancing_tokens

        POGGER.debug("SUBLIST WITH DIFFERENT")
        POGGER.debug("container_depth:$:", container_depth)
        POGGER.debug("are_list_starts_equal>>ELIGIBLE!!!")
        POGGER.debug(
            "are_list_starts_equal>>current_start_index>>$>>old_start_index>>$",
            current_start_index,
            old_start_index,
        )
        (
            are_equal,
            balancing_tokens,
        ) = ListBlockProcessor.__are_list_starts_equal_cleanup(
            parser_state,
            current_start_index,
            old_start_index,
            new_token,
            container_depth,
        )

        return are_equal, False, balancing_tokens

    # pylint: enable=too-many-arguments

    @staticmethod
    def __are_list_starts_equal_cleanup(
        parser_state: ParserState,
        current_start_index: int,
        old_start_index: int,
        new_token: ListStartMarkdownToken,
        container_depth: int,
    ) -> Tuple[bool, List[MarkdownToken]]:
        balancing_tokens: List[MarkdownToken] = []
        are_equal = current_start_index >= old_start_index
        POGGER.debug("are_list_starts_equal>>$", are_equal)

        if (
            are_equal
            and not container_depth
            and not parser_state.token_stack[-1].is_list
        ):
            POGGER.debug("parser_state.token_stack>>$", parser_state.token_stack)
            stack_index = len(parser_state.token_stack) - 1
            while stack_index and not parser_state.token_stack[stack_index].is_list:
                stack_index -= 1
            assert stack_index
            balancing_tokens, _ = parser_state.close_open_blocks_fn(
                parser_state,
                until_this_index=stack_index + 1,
                include_block_quotes=True,
            )
            POGGER.debug("parser_state.token_stack>>$", parser_state.token_stack)
            new_token.set_extracted_whitespace(
                "".rjust(new_token.column_number - 1, " ")
            )
        return are_equal, balancing_tokens

    # pylint: disable=too-many-arguments
    @staticmethod
    def __process_eligible_list_start(
        parser_state: ParserState,
        balancing_tokens: List[MarkdownToken],
        current_start_index: int,
        old_start_index: int,
        current_container_blocks: List[StackToken],
        new_stack: StackToken,
    ) -> bool:
        POGGER.debug("are_list_starts_equal>>ELIGIBLE!!!")
        POGGER.debug(
            "are_list_starts_equal>>current_start_index>>$>>old_start_index>>$",
            current_start_index,
            old_start_index,
        )
        if current_start_index >= old_start_index:
            return False

        POGGER.debug("current_container_blocks>>$", current_container_blocks)
        if len(current_container_blocks) > 1:
            POGGER.debug("current_container_blocks-->$", parser_state.token_stack)
            allow_list_removal = ListBlockProcessor.__calculate_can_remove_list(
                parser_state, current_start_index
            )
            POGGER.debug("allow_list_removal-->$", allow_list_removal)
            ListBlockProcessor.__close_required_lists(
                parser_state,
                allow_list_removal,
                balancing_tokens,
                new_stack,
            )

        return True

    # pylint: enable=too-many-arguments

    @staticmethod
    def __calculate_can_remove_list(
        parser_state: ParserState, current_start_index: int
    ) -> bool:
        POGGER.debug_with_visible_whitespace(
            "parser_state.token_stack>$", parser_state.token_stack
        )
        POGGER.debug_with_visible_whitespace(
            "current_start_index>$", current_start_index
        )
        if len(parser_state.token_stack) <= 2:
            return False

        stack_index = len(parser_state.token_stack) - 1
        while stack_index and not parser_state.token_stack[stack_index].is_list:
            stack_index -= 1
        assert stack_index
        last_stack_index = stack_index
        assert parser_state.token_stack[stack_index].is_list
        stack_index -= 1
        while stack_index and not parser_state.token_stack[stack_index].is_list:
            stack_index -= 1
        if not stack_index:
            return False

        POGGER.debug(
            "parser_state.token_stack[i]>$", parser_state.token_stack[stack_index]
        )
        previous_list_start_index = parser_state.token_stack[stack_index].indent_level
        previous_list_end_index = (
            previous_list_start_index
            + len(parser_state.token_stack[stack_index].list_character)
            + parser_state.token_stack[stack_index].ws_after_marker
        )
        POGGER.debug(
            "token_stack[i]:  previous_list_start_index=$,previous_list_end_index=$",
            previous_list_start_index,
            previous_list_end_index,
        )
        with_previous_list_bounds = (
            previous_list_start_index <= current_start_index < previous_list_end_index
        )

        adjusted_index = (
            parser_state.token_stack[last_stack_index].indent_level
            - parser_state.token_stack[last_stack_index].ws_before_marker
            if parser_state.token_stack[last_stack_index].is_ordered_list
            else parser_state.token_stack[last_stack_index].indent_level - 2
        )

        POGGER.debug(
            "adjusted_index>$ > parser_state.token_stack[stack_index].indent_level>$ ) "
            + "or not with_previous_list_bounds=$",
            adjusted_index,
            parser_state.token_stack[stack_index].indent_level,
            with_previous_list_bounds,
        )
        return (
            adjusted_index > parser_state.token_stack[stack_index].indent_level
            or not with_previous_list_bounds
        )

    @staticmethod
    def __close_required_lists_calc(parser_state: ParserState) -> Tuple[int, int]:

        token_stack_index = len(parser_state.token_stack) - 1
        found_list_tokens = []
        while token_stack_index:
            if parser_state.token_stack[token_stack_index].is_list:
                found_list_tokens.append(parser_state.token_stack[token_stack_index])
            token_stack_index -= 1

        parent_indent_level = (
            found_list_tokens[1].matching_markdown_token.indent_level
            if len(found_list_tokens) > 1
            else -1
        )
        return len(found_list_tokens), parent_indent_level

    @staticmethod
    def __close_required_lists(
        parser_state: ParserState,
        allow_list_removal: bool,
        balancing_tokens: List[MarkdownToken],
        new_stack: StackToken,
    ) -> None:
        assert new_stack.matching_markdown_token is not None
        matching_column_number = new_stack.matching_markdown_token.column_number

        (
            list_count,
            parent_indent_level,
        ) = ListBlockProcessor.__close_required_lists_calc(parser_state)

        POGGER.debug(
            "matching_column_number=$ <= parent_indent_level=$ and allow_list_removal=$ and list_count=$ > 1",
            matching_column_number,
            parent_indent_level,
            allow_list_removal,
            list_count,
        )
        while (
            matching_column_number <= parent_indent_level
            and allow_list_removal
            and list_count > 1
        ):
            stack_index = len(parser_state.token_stack) - 2
            while stack_index and not parser_state.token_stack[stack_index].is_list:
                stack_index -= 1
            last_stack_index = parser_state.token_stack.index(
                parser_state.token_stack[-1]
            )
            POGGER.debug("parser_state.token_stack>>$", parser_state.token_stack)
            POGGER.debug("last_stack_index>>$", last_stack_index)
            POGGER.debug("stack_index>>$", stack_index)
            last_stack_index = stack_index + 1

            close_tokens, _ = parser_state.close_open_blocks_fn(
                parser_state,
                until_this_index=last_stack_index,
                include_lists=True,
                include_block_quotes=True,
            )
            assert close_tokens
            balancing_tokens.extend(close_tokens)
            POGGER.debug("close_tokens>>$", close_tokens)
            POGGER.debug("parser_state.token_stack>>$", parser_state.token_stack)
            assert parser_state.token_stack[-1].is_list

            (
                list_count,
                parent_indent_level,
            ) = ListBlockProcessor.__close_required_lists_calc(parser_state)
            POGGER.debug(
                "matching_column_number=$ < parent_indent_level=$ and "
                + "allow_list_removal=$ and list_count=$ > 1",
                matching_column_number,
                parent_indent_level,
                allow_list_removal,
                list_count,
            )

    @staticmethod
    def __adjust_line_for_list_in_process(
        line_to_parse: str,
        start_index: int,
        leading_space: Optional[str],
        leading_space_length: int,
        requested_list_indent: int,
    ) -> Tuple[str, Optional[str]]:
        """
        Alter the current line to better represent the current level of lists.
        """
        remaining_indent = leading_space_length - requested_list_indent
        POGGER.debug(
            "enough ws to continue; line($),start_index($),leading_space($)",
            line_to_parse,
            start_index,
            leading_space,
        )
        POGGER.debug(
            "enough ws to continue; lsl($)-rsi($)=ri($)",
            leading_space_length,
            requested_list_indent,
            remaining_indent,
        )
        if remaining_indent < 0:
            padded_spaces = ""
            start_index = 0
            removed_whitespace = None
        else:
            assert leading_space is not None
            removed_whitespace = leading_space[:requested_list_indent]
            padded_spaces = ParserHelper.repeat_string(
                ParserHelper.space_character, remaining_indent
            )
        return (
            f"{padded_spaces}{line_to_parse[start_index:]}",
            removed_whitespace,
        )

    # pylint: disable=too-many-arguments
    @staticmethod
    def __check_for_list_closures(
        parser_state: ParserState,
        line_to_parse: str,
        start_index: int,
        extracted_whitespace: Optional[str],
        ind: Optional[int],
        leading_space_length: int,
    ) -> Tuple[List[MarkdownToken], Optional[RequeueLineInfo]]:
        """
        Check to see if the list in progress and the level of lists shown require
        the closing of some of the sublists.
        """
        POGGER.debug("ws(naa)>>line_to_parse>>$<<", line_to_parse)
        POGGER.debug("ws(naa)>>stack>>$", parser_state.token_stack)
        POGGER.debug("ws(naa)>>tokens>>$", parser_state.token_document)
        assert ind is not None

        is_leaf_block_start = LeafBlockProcessor.is_paragraph_ending_leaf_block_start(
            parser_state, line_to_parse, start_index, extracted_whitespace
        )
        if not parser_state.token_stack[-1].is_paragraph or is_leaf_block_start:
            POGGER.debug("ws (normal and adjusted) not enough to continue")

            POGGER.debug("lsl $", leading_space_length)
            POGGER.debug("lsl $", parser_state.token_stack[ind])
            search_index = ind
            POGGER.debug(
                "lsl $>$",
                search_index,
                parser_state.token_stack[search_index - 1],
            )
            while (
                parser_state.token_stack[search_index - 1].is_list
                and parser_state.token_stack[search_index - 1].indent_level
                > leading_space_length
            ):
                search_index -= 1
                POGGER.debug(
                    "lsl $>$",
                    search_index,
                    parser_state.token_stack[search_index],
                )

            POGGER.debug("lsl $", parser_state.token_stack[search_index])

            (
                container_level_tokens,
                requeue_line_info,
            ) = parser_state.close_open_blocks_fn(
                parser_state,
                until_this_index=search_index,
                include_lists=True,
                caller_can_handle_requeue=True,
                requeue_reset=True,
            )
        else:
            container_level_tokens, requeue_line_info = [], None

        return container_level_tokens, requeue_line_info

    # pylint: enable=too-many-arguments
