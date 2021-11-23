"""
Module to provide processing for the container blocks.
"""
import logging

from pymarkdown.block_quote_processor import BlockQuoteProcessor
from pymarkdown.container_indices import ContainerIndices
from pymarkdown.extensions.pragma_token import PragmaExtension
from pymarkdown.html_helper import HtmlHelper
from pymarkdown.inline_markdown_token import TextMarkdownToken
from pymarkdown.leaf_block_processor import LeafBlockProcessor
from pymarkdown.link_reference_definition_helper import LinkReferenceDefinitionHelper
from pymarkdown.list_block_processor import ListBlockProcessor
from pymarkdown.parser_helper import ParserHelper
from pymarkdown.parser_logger import ParserLogger
from pymarkdown.position_marker import PositionMarker

POGGER = ParserLogger(logging.getLogger(__name__))

# pylint: disable=too-many-lines


class ContainerBlockProcessor:
    """
    Class to provide processing for the container blocks.
    """

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-arguments
    @staticmethod
    def parse_line_for_container_blocks(
        parser_state,
        position_marker,
        ignore_link_definition_start,
        parser_properties,
        container_start_bq_count,
        container_depth=0,
        foobar=None,
        init_bq=None,
    ):
        """
        Parse the line, taking care to handle any container blocks before deciding
        whether or not to pass the (remaining parts of the) line to the leaf block
        processor.

        Note: This is one of the more heavily traffic functions in the
        parser.  Debugging should be uncommented only if needed.
        """

        start_index, extracted_whitespace = ParserHelper.extract_whitespace(
            position_marker.text_to_parse, 0
        )
        if ContainerBlockProcessor.__look_for_pragmas(
            position_marker,
            position_marker.text_to_parse,
            container_depth,
            extracted_whitespace,
            parser_properties,
        ):
            return None, None, None, None, False

        (
            line_to_parse,
            current_container_blocks,
            adj_ws,
            stack_bq_count,
            this_bq_count,
        ) = ContainerBlockProcessor.__prepare_container_start_variables(
            parser_state,
            position_marker,
            container_depth,
            extracted_whitespace,
            foobar,
            init_bq,
        )

        (
            end_container_indices,
            did_process,
            was_container_start,
            this_bq_count,
            stack_bq_count,
            line_to_parse,
            start_index,
            leaf_tokens,
            container_level_tokens,
            removed_chars_at_start,
            did_blank,
            last_block_quote_index,
            text_removed_by_container,
            avoid_block_starts,
            requeue_line_info,
        ) = ContainerBlockProcessor.__check_for_container_starts(
            parser_state,
            position_marker,
            extracted_whitespace,
            adj_ws,
            this_bq_count,
            stack_bq_count,
            start_index,
            container_start_bq_count,
            current_container_blocks,
        )
        if requeue_line_info or did_blank:
            return (
                container_level_tokens,
                line_to_parse,
                this_bq_count,
                requeue_line_info,
                did_blank,
            )

        (
            can_continue,
            line_to_parse,
            leaf_tokens,
            container_level_tokens,
            this_bq_count,
            last_list_start_index,
        ) = ContainerBlockProcessor.__handle_nested_blocks(
            parser_state,
            container_depth,
            this_bq_count,
            stack_bq_count,
            parser_properties,
            end_container_indices,
            leaf_tokens,
            container_level_tokens,
            was_container_start,
            avoid_block_starts,
            start_index,
            removed_chars_at_start,
            text_removed_by_container,
            position_marker,
            line_to_parse,
            last_block_quote_index,
        )

        if can_continue:
            (
                can_continue,
                did_process,
                line_to_parse,
                container_level_tokens,
                used_indent,
                requeue_line_info,
            ) = ContainerBlockProcessor.__handle_block_continuations(
                parser_state,
                did_process,
                line_to_parse,
                start_index,
                container_level_tokens,
                extracted_whitespace,
                leaf_tokens,
                this_bq_count,
                stack_bq_count,
                container_start_bq_count,
            )
        if can_continue:
            requeue_line_info = ContainerBlockProcessor.__handle_leaf_tokens(
                parser_state,
                position_marker,
                line_to_parse,
                used_indent,
                text_removed_by_container,
                start_index,
                container_level_tokens,
                leaf_tokens,
                this_bq_count,
                removed_chars_at_start,
                ignore_link_definition_start,
                last_block_quote_index,
                last_list_start_index,
            )

        return (
            container_level_tokens,
            line_to_parse,
            this_bq_count,
            requeue_line_info,
            False,
        )
        # pylint: enable=too-many-locals
        # pylint: enable=too-many-arguments

    # pylint: disable=too-many-arguments
    @staticmethod
    def __prepare_container_start_variables(
        parser_state,
        position_marker,
        container_depth,
        extracted_whitespace,
        foobar,
        init_bq,
    ):
        line_to_parse = position_marker.text_to_parse
        if container_depth == 0:
            parser_state.mark_start_information(position_marker)

            parser_state.copy_of_token_stack = []
            for next_item in parser_state.token_stack:
                parser_state.copy_of_token_stack.append(next_item)

        # POGGER.debug("Line:$:", line_to_parse)
        # POGGER.debug("Stack Depth:$:", parser_state.original_stack_depth)
        # POGGER.debug("Document Depth:$:", parser_state.original_document_depth)

        # Debug to be used for block quotes if needed.
        # POGGER.debug(
        #    "Last Block Quote:$:",
        #    parser_state.last_block_quote_stack_token,
        # )
        # POGGER.debug(
        #    "Last Block Quote:$:",
        #    parser_state.last_block_quote_markdown_token_index,
        # )
        # POGGER.debug(
        #    "Last Block Quote:$:", parser_state.copy_of_last_block_quote_markdown_token
        # )

        (
            current_container_blocks,
            adj_ws,
            stack_bq_count,
            this_bq_count,
        ) = ContainerBlockProcessor.__calculate_for_container_blocks(
            parser_state,
            line_to_parse,
            extracted_whitespace,
            foobar,
            init_bq,
        )
        return (
            line_to_parse,
            current_container_blocks,
            adj_ws,
            stack_bq_count,
            this_bq_count,
        )

    # pylint: enable=too-many-arguments

    # pylint: disable=too-many-arguments
    @staticmethod
    def __handle_block_continuations(
        parser_state,
        did_process,
        line_to_parse,
        start_index,
        container_level_tokens,
        extracted_whitespace,
        leaf_tokens,
        this_bq_count,
        stack_bq_count,
        container_start_bq_count,
    ):
        # POGGER.debug_with_visible_whitespace(
        #     ">>__process_list_in_progress>>$>>",
        #     line_to_parse,
        # )
        requeue_line_info, used_indent = None, None
        if not did_process:
            (
                did_process,
                line_to_parse,
                container_level_tokens,
                used_indent,
                requeue_line_info,
            ) = ContainerBlockProcessor.__process_list_in_progress(
                parser_state,
                line_to_parse,
                start_index,
                container_level_tokens,
                extracted_whitespace,
            )
        if not requeue_line_info:
            # POGGER.debug_with_visible_whitespace(
            #     ">>__process_list_in_progress>>$>>", line_to_parse
            # )
            # POGGER.debug("container_start_bq_count>>$", container_start_bq_count)
            # POGGER.debug("this_bq_count>>$", this_bq_count)
            # POGGER.debug("stack_bq_count>>$", stack_bq_count)
            ContainerBlockProcessor.__process_lazy_lines(
                parser_state,
                leaf_tokens,
                this_bq_count,
                stack_bq_count,
                line_to_parse,
                container_level_tokens,
                container_start_bq_count,
            )

        return (
            not requeue_line_info,
            did_process,
            line_to_parse,
            container_level_tokens,
            used_indent,
            requeue_line_info,
        )

    # pylint: enable=too-many-arguments

    # pylint: disable=too-many-arguments, too-many-locals
    @staticmethod
    def __check_for_container_starts(
        parser_state,
        position_marker,
        extracted_whitespace,
        adj_ws,
        this_bq_count,
        stack_bq_count,
        start_index,
        container_start_bq_count,
        current_container_blocks,
    ):

        # POGGER.debug("this_bq_count>>$", this_bq_count)

        end_container_indices = ContainerIndices(-1, -1, -1)
        parser_state.nested_list_start = None
        (
            can_continue,
            did_process,
            was_container_start,
            end_container_indices.block_index,
            this_bq_count,
            stack_bq_count,
            line_to_parse,
            start_index,
            leaf_tokens,
            container_level_tokens,
            removed_chars_at_start,
            did_blank,
            last_block_quote_index,
            text_removed_by_container,
            avoid_block_starts,
            requeue_line_info,
        ) = ContainerBlockProcessor.__get_block_start_index(
            position_marker,
            parser_state,
            extracted_whitespace,
            adj_ws,
            this_bq_count,
            stack_bq_count,
            start_index,
            container_start_bq_count,
        )
        if can_continue:
            # POGGER.debug("this_bq_count>>$", this_bq_count)
            # POGGER.debug("stack_bq_count>>$", stack_bq_count)
            # POGGER.debug(">>avoid_block_starts>>$", avoid_block_starts)
            # POGGER.debug(">>did_process>>$", did_process)

            (
                did_process,
                was_container_start,
                end_container_indices.ulist_index,
                line_to_parse,
                removed_chars_at_start,
                requeue_line_info,
            ) = ContainerBlockProcessor.__get_list_start_index(
                position_marker,
                line_to_parse,
                start_index,
                True,
                parser_state,
                did_process,
                was_container_start,
                extracted_whitespace,
                adj_ws,
                stack_bq_count,
                this_bq_count,
                removed_chars_at_start,
                current_container_blocks,
                container_level_tokens,
            )
            if requeue_line_info:
                POGGER.debug(
                    ">>requeuing lines after looking for ordered list start. returning."
                )
                can_continue = False

        if can_continue:
            # POGGER.debug("this_bq_count>>$", this_bq_count)
            # POGGER.debug("stack_bq_count>>$", stack_bq_count)
            # POGGER.debug("was_container_start>>$", was_container_start)
            (
                did_process,
                was_container_start,
                end_container_indices.olist_index,
                line_to_parse,
                removed_chars_at_start,
                requeue_line_info,
            ) = ContainerBlockProcessor.__get_list_start_index(
                position_marker,
                line_to_parse,
                start_index,
                False,
                parser_state,
                did_process,
                was_container_start,
                extracted_whitespace,
                adj_ws,
                stack_bq_count,
                this_bq_count,
                removed_chars_at_start,
                current_container_blocks,
                container_level_tokens,
            )
            if requeue_line_info:
                POGGER.debug(
                    ">>requeuing lines after looking for unordered list start. returning."
                )
        return (
            end_container_indices,
            did_process,
            was_container_start,
            this_bq_count,
            stack_bq_count,
            line_to_parse,
            start_index,
            leaf_tokens,
            container_level_tokens,
            removed_chars_at_start,
            did_blank,
            last_block_quote_index,
            text_removed_by_container,
            avoid_block_starts,
            requeue_line_info,
        )

    # pylint: enable=too-many-arguments, too-many-locals

    # pylint: disable=too-many-arguments, too-many-locals
    @staticmethod
    def __handle_nested_blocks(
        parser_state,
        container_depth,
        this_bq_count,
        stack_bq_count,
        parser_properties,
        end_container_indices,
        leaf_tokens,
        container_level_tokens,
        was_container_start,
        avoid_block_starts,
        start_index,
        removed_chars_at_start,
        text_removed_by_container,
        position_marker,
        line_to_parse,
        last_block_quote_index,
    ):

        # POGGER.debug("this_bq_count>>$", this_bq_count)
        # POGGER.debug("stack_bq_count>>$", stack_bq_count)

        # POGGER.debug("last_block_quote_index>>$", last_block_quote_index)
        # POGGER.debug("indices>>$", end_container_indices)
        # POGGER.debug("line_to_parse(after containers)>>$", line_to_parse)
        # POGGER.debug("was_container_start>>$", was_container_start)

        last_list_start_index = 0
        if end_container_indices.block_index != -1:
            assert last_block_quote_index in (
                end_container_indices.block_index - 1,
                end_container_indices.block_index,
            )
        elif end_container_indices.olist_index != -1:
            last_list_start_index = end_container_indices.olist_index
        elif end_container_indices.ulist_index != -1:
            last_list_start_index = end_container_indices.ulist_index

        did_process_blank_line = False
        if not parser_state.token_stack[-1].is_fenced_code_block:
            new_position_marker = PositionMarker(
                position_marker.line_number, start_index, line_to_parse
            )
            # POGGER.debug("this_bq_count>>$", this_bq_count)
            # POGGER.debug("stack_bq_count>>$", stack_bq_count)
            # POGGER.debug("was_container_start>>$", was_container_start)
            (
                line_to_parse,
                leaf_tokens,
                container_level_tokens,
                this_bq_count,
                did_process_blank_line,
            ) = ContainerBlockProcessor.__handle_nested_container_blocks(
                parser_state,
                container_depth,
                this_bq_count,
                stack_bq_count,
                new_position_marker,
                parser_properties,
                end_container_indices,
                leaf_tokens,
                container_level_tokens,
                was_container_start,
                avoid_block_starts,
                start_index,
                removed_chars_at_start,
                text_removed_by_container,
            )
            # POGGER.debug_with_visible_whitespace("text>>$>>", line_to_parse)
            # POGGER.debug("this_bq_count>>$", this_bq_count)
            # POGGER.debug("stack_bq_count>>$", stack_bq_count)

        # POGGER.debug("olist->container_level_tokens->$", container_level_tokens)
        # POGGER.debug("removed_chars_at_start>>>$", removed_chars_at_start)
        return (
            not (container_depth or did_process_blank_line),
            line_to_parse,
            leaf_tokens,
            container_level_tokens,
            this_bq_count,
            last_list_start_index,
        )

    # pylint: enable=too-many-arguments, too-many-locals

    # pylint: disable=too-many-arguments, too-many-locals
    @staticmethod
    def __handle_leaf_tokens(
        parser_state,
        position_marker,
        line_to_parse,
        used_indent,
        text_removed_by_container,
        start_index,
        container_level_tokens,
        leaf_tokens,
        this_bq_count,
        removed_chars_at_start,
        ignore_link_definition_start,
        last_block_quote_index,
        last_list_start_index,
    ):

        # POGGER.debug_with_visible_whitespace("text>>$>>", line_to_parse)
        # POGGER.debug("container_level_tokens>>$>>", container_level_tokens)

        calculated_indent, force_it = (
            len(parser_state.original_line_to_parse) - len(line_to_parse),
            False,
        )
        # POGGER.debug(">>indent>>$", calculated_indent)

        if (
            used_indent
            and parser_state.token_stack[-1].is_paragraph
            and parser_state.token_stack[-2].is_block_quote
        ):
            assert text_removed_by_container is None
            text_removed_by_container, force_it = used_indent, True

        newer_position_marker = PositionMarker(
            position_marker.line_number,
            start_index,
            line_to_parse,
            index_indent=calculated_indent,
        )
        parser_state.mark_for_leaf_processing(container_level_tokens)
        leaf_tokens, requeue_line_info = ContainerBlockProcessor.__process_leaf_tokens(
            parser_state,
            leaf_tokens,
            newer_position_marker,
            this_bq_count,
            removed_chars_at_start,
            ignore_link_definition_start,
            last_block_quote_index,
            last_list_start_index,
            text_removed_by_container,
            force_it,
        )
        parser_state.clear_after_leaf_processing()

        container_level_tokens.extend(leaf_tokens)
        return requeue_line_info

    # pylint: enable=too-many-arguments, too-many-locals

    @staticmethod
    # pylint: disable=too-many-locals, too-many-arguments
    def __get_block_start_index(
        position_marker,
        parser_state,
        extracted_whitespace,
        adj_ws,
        this_bq_count,
        stack_bq_count,
        start_index,
        container_start_bq_count,
    ):
        new_position_marker = PositionMarker(
            position_marker.line_number, start_index, position_marker.text_to_parse
        )
        (
            did_process,
            was_container_start,
            block_index,
            this_bq_count,
            stack_bq_count,
            line_to_parse,
            start_index,
            leaf_tokens,
            container_level_tokens,
            removed_chars_at_start,
            did_blank,
            last_block_quote_index,
            text_removed_by_container,
            avoid_block_starts,
            requeue_line_info,
        ) = BlockQuoteProcessor.handle_block_quote_block(
            parser_state,
            new_position_marker,
            extracted_whitespace,
            adj_ws,
            this_bq_count,
            stack_bq_count,
            container_start_bq_count,
        )
        # POGGER.debug("container_start_bq_count>>:$", container_start_bq_count)
        # POGGER.debug("this_bq_count>>:$", this_bq_count)
        # POGGER.debug("stack_bq_count>>$", stack_bq_count)
        # POGGER.debug("did_process>>$", did_process)
        POGGER.debug("text>>:$:>>", line_to_parse)
        # POGGER.debug(">>container_level_tokens>>$", container_level_tokens)
        # POGGER.debug(">>leaf_tokens>>$", leaf_tokens)

        if requeue_line_info:
            POGGER.debug(">>requeuing lines after looking for block start. returning.")

        if did_blank:
            POGGER.debug(">>already handled blank line. returning.")
            container_level_tokens.extend(leaf_tokens)

        return (
            not requeue_line_info and not did_blank,
            did_process,
            was_container_start,
            block_index,
            this_bq_count,
            stack_bq_count,
            line_to_parse,
            start_index,
            leaf_tokens,
            container_level_tokens,
            removed_chars_at_start,
            did_blank,
            last_block_quote_index,
            text_removed_by_container,
            avoid_block_starts,
            requeue_line_info,
        )

    # pylint: enable=too-many-locals, too-many-arguments

    # pylint: disable=too-many-locals, too-many-arguments
    @staticmethod
    def __get_list_start_index(
        position_marker,
        line_to_parse,
        start_index,
        is_ulist,
        parser_state,
        did_process,
        was_container_start,
        extracted_whitespace,
        adj_ws,
        stack_bq_count,
        this_bq_count,
        removed_chars_at_start,
        current_container_blocks,
        container_level_tokens,
    ):
        """
        Note: This is one of the more heavily traffic functions in the
        parser.  Debugging should be uncommented only if needed.
        """
        new_position_marker = PositionMarker(
            position_marker.line_number, start_index, line_to_parse
        )

        POGGER.debug(
            "pre-list>>#$#$#$#",
            position_marker.index_number,
            position_marker.index_indent,
            position_marker.text_to_parse,
        )
        POGGER.debug(
            "pre-list>>#$#$#$#",
            new_position_marker.index_number,
            new_position_marker.index_indent,
            new_position_marker.text_to_parse,
        )
        new_list_index = -1
        if not did_process:
            (
                did_process,
                was_container_start,
                new_list_index,
                line_to_parse,
                resultant_tokens,
                removed_chars_at_start,
                requeue_line_info,
            ) = ListBlockProcessor.handle_list_block(
                is_ulist,
                parser_state,
                was_container_start,
                new_position_marker,
                extracted_whitespace,
                adj_ws,
                stack_bq_count,
                this_bq_count,
                removed_chars_at_start,
                current_container_blocks,
            )
            if requeue_line_info:
                return (
                    None,
                    None,
                    None,
                    None,
                    None,
                    requeue_line_info,
                )
            container_level_tokens.extend(resultant_tokens)
        POGGER.debug(
            "post-ulist>>#$#$#$#",
            position_marker.index_number,
            position_marker.index_indent,
            position_marker.text_to_parse,
        )
        POGGER.debug(
            "post-ulist>>#$#$#$#",
            new_position_marker.index_number,
            new_position_marker.index_indent,
            new_position_marker.text_to_parse,
        )
        POGGER.debug("text>>$>>", line_to_parse)

        return (
            did_process,
            was_container_start,
            new_list_index,
            line_to_parse,
            removed_chars_at_start,
            None,
        )

    # pylint: enable=too-many-locals, too-many-arguments

    @staticmethod
    def __calculate_for_container_blocks(
        parser_state,
        line_to_parse,
        extracted_whitespace,
        foobar,
        init_bq,
    ):
        """
        Perform some calculations that will be needed for parsing the container blocks.
        """
        current_container_blocks = [
            ind for ind in parser_state.token_stack if ind.is_list
        ]

        adj_ws = ContainerBlockProcessor.__calculate_adjusted_whitespace(
            parser_state,
            current_container_blocks,
            line_to_parse,
            extracted_whitespace,
            foobar=foobar,
        )

        return (
            current_container_blocks,
            adj_ws,
            parser_state.count_of_block_quotes_on_stack(),
            0 if init_bq is None else init_bq,
        )

    # pylint: disable=too-many-arguments
    @staticmethod
    def __calculate_adjusted_whitespace(
        parser_state,
        current_container_blocks,
        line_to_parse,
        extracted_whitespace,
        foobar=None,
        previous_ws_len=0,
    ):
        """
        Based on the last container on the stack, determine what the adjusted whitespace is.
        """

        adj_ws, stack_index = (
            extracted_whitespace,
            parser_state.find_last_list_block_on_stack(),
        )
        if stack_index <= 0:
            POGGER.debug("PLFCB>>No Started lists")
            assert not current_container_blocks
            if foobar is None:
                POGGER.debug("PLFCB>>No Started Block Quote")
            else:
                POGGER.debug("PLFCB>>Started Block Quote")
                adj_ws = extracted_whitespace[foobar:]
        else:
            assert current_container_blocks
            POGGER.debug(
                "PLFCB>>Started list-last stack>>$",
                parser_state.token_stack,
            )
            POGGER.debug(
                "PLFCB>>Started list-last stack>>$",
                parser_state.token_stack[stack_index],
            )
            token_index = len(parser_state.token_document) - 1

            while token_index >= 0 and not (
                parser_state.token_document[token_index].is_any_list_token
            ):
                token_index -= 1
            POGGER.debug(
                "PLFCB>>Started list-last token>>$",
                parser_state.token_document[token_index],
            )
            assert token_index >= 0

            ws_len, old_start_index = (
                ParserHelper.calculate_length(extracted_whitespace) + previous_ws_len
            ), parser_state.token_document[token_index].indent_level

            POGGER.debug("old_start_index>>$>>ws_len>>$", old_start_index, ws_len)
            if ws_len >= old_start_index:
                POGGER.debug("RELINE:$:", line_to_parse)
                adj_ws = extracted_whitespace[old_start_index:]
        return adj_ws

    # pylint: enable=too-many-arguments

    # pylint: disable=too-many-arguments, too-many-locals
    @staticmethod
    def __handle_nested_container_blocks(
        parser_state,
        container_depth,
        this_bq_count,
        stack_bq_count,
        position_marker,
        parser_properties,
        end_container_indices,
        leaf_tokens,
        container_level_tokens,
        was_container_start,
        avoid_block_starts,
        start_index,
        removed_chars_at_start,
        text_removed_by_container,
    ):
        """
        Handle the processing of nested container blocks, as they can contain
        themselves and get somewhat messy.
        """
        did_process_blank_line, adjusted_text_to_parse = (
            False,
            position_marker.text_to_parse,
        )

        POGGER.debug("adjusted_text_to_parse>$<", adjusted_text_to_parse)
        POGGER.debug("index_number>$<", position_marker.index_number)
        POGGER.debug("index_indent>$<", position_marker.index_indent)
        POGGER.debug("start_index>$<", start_index)
        POGGER.debug("parser_state.nested_list_start>$", parser_state.nested_list_start)
        POGGER.debug("was_container_start>$", was_container_start)

        if was_container_start and position_marker.text_to_parse:
            assert container_depth < 10
            nested_container_starts = (
                ContainerBlockProcessor.__get_nested_container_starts(
                    parser_state,
                    position_marker.text_to_parse,
                    end_container_indices,
                    avoid_block_starts,
                    start_index,
                    removed_chars_at_start,
                    text_removed_by_container,
                )
            )
            POGGER.debug(
                "__handle_nested_container_blocks>nested_container_starts>>:$:<<",
                nested_container_starts,
            )
            POGGER.debug("check next container_start>leaf_tokens>>$", leaf_tokens)
            POGGER.debug(
                "check next container_start>container_level_tokens>>$",
                container_level_tokens,
            )

            adj_line_to_parse = position_marker.text_to_parse
            POGGER.debug("check next container_start>pre>>$<<", adj_line_to_parse)

            (
                start_index,
                delta,
                adj_line_to_parse,
                already_adjusted,
                active_container_index,
            ) = ContainerBlockProcessor.__check_for_nested_list_start(
                parser_state,
                end_container_indices,
                nested_container_starts,
                adj_line_to_parse,
                this_bq_count,
                stack_bq_count,
                start_index,
            )

            POGGER.debug("leaf_tokens>>$", leaf_tokens)
            assert not leaf_tokens
            (
                container_level_tokens,
                adj_line_to_parse,
                adjusted_text_to_parse,
            ) = ContainerBlockProcessor.__do_nested_cleanup(
                parser_state,
                stack_bq_count,
                this_bq_count,
                delta,
                already_adjusted,
                adj_line_to_parse,
                container_level_tokens,
                active_container_index,
                adjusted_text_to_parse,
            )

            (
                did_process_blank_line,
                this_bq_count,
                adjusted_text_to_parse,
            ) = ContainerBlockProcessor.__check_for_next_container(
                parser_state,
                nested_container_starts,
                this_bq_count,
                adjusted_text_to_parse,
                adj_line_to_parse,
                end_container_indices,
                position_marker,
                container_depth,
                parser_properties,
            )
        return (
            adjusted_text_to_parse,
            leaf_tokens,
            container_level_tokens,
            this_bq_count,
            did_process_blank_line,
        )

    # pylint: enable=too-many-arguments, too-many-locals

    # pylint: disable=too-many-arguments
    @staticmethod
    def __check_for_nested_list_start(
        parser_state,
        end_container_indices,
        nested_container_starts,
        adj_line_to_parse,
        this_bq_count,
        stack_bq_count,
        start_index,
    ):

        active_container_index = max(
            end_container_indices.ulist_index,
            end_container_indices.olist_index,
            end_container_indices.block_index,
        )
        POGGER.debug(
            "check next container_start>max>>$>>bq>>$",
            active_container_index,
            end_container_indices.block_index,
        )
        delta, already_adjusted = 0, False
        if (
            end_container_indices.block_index != -1
            and not nested_container_starts.ulist_index
            and not nested_container_starts.olist_index
        ):
            assert active_container_index == end_container_indices.block_index
            POGGER.debug(
                "parser_state.nested_list_start>>$<<",
                parser_state.nested_list_start,
            )
            POGGER.debug("adj_line_to_parse>>$<<", adj_line_to_parse)
            POGGER.debug(
                "parser_state.token_document>>$<<", parser_state.token_document
            )
            if parser_state.nested_list_start and adj_line_to_parse.strip():

                (
                    start_index,
                    indent_level,
                    indent_was_adjusted,
                    delta,
                ) = ContainerBlockProcessor.__calculate_initial_list_adjustments(
                    parser_state, adj_line_to_parse, end_container_indices
                )

                (
                    adj_line_to_parse,
                    already_adjusted,
                ) = ContainerBlockProcessor.__adjust_line_2(
                    parser_state,
                    end_container_indices,
                    start_index,
                    indent_level,
                    nested_container_starts,
                    adj_line_to_parse,
                    indent_was_adjusted,
                    this_bq_count,
                    stack_bq_count,
                )
        return (
            start_index,
            delta,
            adj_line_to_parse,
            already_adjusted,
            active_container_index,
        )

    # pylint: enable=too-many-arguments

    @staticmethod
    def __calculate_initial_list_adjustments(
        parser_state, adj_line_to_parse, end_container_indices
    ):

        delta, indent_level = 0, parser_state.nested_list_start.indent_level
        start_index, _ = ParserHelper.extract_whitespace(adj_line_to_parse, 0)
        POGGER.debug(
            "end_container_indices.block_index>>$<<",
            end_container_indices.block_index,
        )
        POGGER.debug("start_index>>$<<", start_index)
        POGGER.debug(
            "indent_level>>$<<",
            indent_level,
        )

        POGGER.debug(
            "parser_state.nested_list_start.matching_markdown_token>>$<<",
            parser_state.nested_list_start.matching_markdown_token,
        )
        list_start_token_index = parser_state.token_document.index(
            parser_state.nested_list_start.matching_markdown_token
        )
        POGGER.debug(
            "list_start_token_index>>$<<",
            list_start_token_index,
        )
        token_after_list_start = parser_state.token_document[list_start_token_index + 1]
        POGGER.debug(
            "token_after_list_start>>$<<",
            token_after_list_start,
        )
        assert (
            parser_state.nested_list_start.matching_markdown_token.line_number
            == token_after_list_start.line_number
        )
        column_number_delta = (
            token_after_list_start.column_number
            - parser_state.nested_list_start.matching_markdown_token.column_number
        )
        POGGER.debug(
            "column_number_delta>>$<<",
            column_number_delta,
        )
        adjusted_indent_level = column_number_delta + end_container_indices.block_index
        POGGER.debug(
            "adjusted_indent_level>>$<<  indent_level>$",
            adjusted_indent_level,
            indent_level,
        )
        indent_was_adjusted = indent_level != adjusted_indent_level
        if indent_level > adjusted_indent_level:
            delta = indent_level - adjusted_indent_level
        indent_level = column_number_delta + end_container_indices.block_index

        return start_index, indent_level, indent_was_adjusted, delta

    # pylint: disable=too-many-arguments
    @staticmethod
    def __adjust_line_2(
        parser_state,
        end_container_indices,
        start_index,
        indent_level,
        nested_container_starts,
        adj_line_to_parse,
        indent_was_adjusted,
        this_bq_count,
        stack_bq_count,
    ):

        already_adjusted = False
        if (
            parser_state.token_document[-1].is_blank_line
            and (end_container_indices.block_index + start_index) < indent_level
        ):
            POGGER.debug("\n\nBOOM\n\n")

            y_tokens = []
            while parser_state.token_document[-1].is_blank_line:
                y_tokens.append(parser_state.token_document[-1])
                del parser_state.token_document[-1]

            x_tokens, _ = parser_state.close_open_blocks_fn(
                parser_state,
                include_lists=True,
            )
            # assert False
            parser_state.token_document.extend(x_tokens)
            parser_state.token_document.extend(y_tokens)
        elif (
            not nested_container_starts.block_index
            and adj_line_to_parse
            and adj_line_to_parse[0] == " "
            and indent_was_adjusted
            and parser_state.nested_list_start
        ):

            POGGER.debug("adj_line_to_parse>:$:<", adj_line_to_parse)
            POGGER.debug(
                "parser_state.nested_list_start>:$:<",
                parser_state.nested_list_start.matching_markdown_token.extracted_whitespace,
            )

            POGGER.debug(
                "this_bq_count:$, stack_bq_count:$",
                this_bq_count,
                stack_bq_count,
            )

            (
                already_adjusted,
                adj_line_to_parse,
            ) = True, ContainerBlockProcessor.__adjust_line_1(
                parser_state, adj_line_to_parse
            )
        return adj_line_to_parse, already_adjusted

    # pylint: enable=too-many-arguments

    @staticmethod
    def __adjust_line_1(parser_state, adj_line_to_parse):
        POGGER.debug(
            "original_line_to_parse:>:$:<",
            parser_state.original_line_to_parse,
        )

        POGGER.debug("BOOM")
        if adj_line_to_parse.startswith(
            parser_state.nested_list_start.matching_markdown_token.extracted_whitespace
        ):
            adj_line_to_parse = adj_line_to_parse[
                len(
                    parser_state.nested_list_start.matching_markdown_token.extracted_whitespace
                ) :
            ]
        else:
            assert parser_state.original_line_to_parse.endswith(adj_line_to_parse)
            orig_parse, curr_parse = len(parser_state.original_line_to_parse), len(
                adj_line_to_parse
            )
            delta_parse = orig_parse - curr_parse
            POGGER.debug(
                "delta_parse($) = curr_parse($) - orig_parse($)",
                delta_parse,
                curr_parse,
                orig_parse,
            )
            whitespace_to_remove = parser_state.nested_list_start.matching_markdown_token.extracted_whitespace[
                delta_parse:
            ]
            POGGER.debug("whitespace_to_remove>:$:<", whitespace_to_remove)
            assert adj_line_to_parse.startswith(whitespace_to_remove)
            adj_line_to_parse = adj_line_to_parse[len(whitespace_to_remove) :]
        return adj_line_to_parse

    # pylint: disable=too-many-arguments
    @staticmethod
    def __do_nested_cleanup(
        parser_state,
        stack_bq_count,
        this_bq_count,
        delta,
        already_adjusted,
        adj_line_to_parse,
        container_level_tokens,
        active_container_index,
        adjusted_text_to_parse,
    ):
        POGGER.debug(
            "check next container_start>mid>>stack_bq_count>>$<<this_bq_count<<$",
            stack_bq_count,
            this_bq_count,
        )
        if delta or already_adjusted:
            POGGER.debug(
                "check next container_start>already adjusted<<$<<",
                adj_line_to_parse,
            )
            adjusted_text_to_parse = adj_line_to_parse
        else:
            POGGER.debug("check next container_start>post<<$<<", adj_line_to_parse)
            adjustment_filler = ParserHelper.repeat_string(
                ParserHelper.space_character, active_container_index
            )
            adj_line_to_parse = f"{adjustment_filler}{adj_line_to_parse}"
            POGGER.debug("check next container_start>post<<$<<", adj_line_to_parse)

        if container_level_tokens:
            parser_state.token_document.extend(container_level_tokens)
            container_level_tokens = []

        return container_level_tokens, adj_line_to_parse, adjusted_text_to_parse

    # pylint: enable=too-many-arguments

    # pylint: disable=too-many-arguments
    @staticmethod
    def __check_for_next_container(
        parser_state,
        nested_container_starts,
        this_bq_count,
        adjusted_text_to_parse,
        adj_line_to_parse,
        end_container_indices,
        position_marker,
        container_depth,
        parser_properties,
    ):

        POGGER.debug("check next container_start>stack>>$", parser_state.token_stack)
        POGGER.debug(
            "check next container_start>tokenized_document>>$",
            parser_state.token_document,
        )

        did_process_blank_line = False
        if (
            nested_container_starts.ulist_index
            or nested_container_starts.olist_index
            or nested_container_starts.block_index
        ):
            POGGER.debug(
                "check next container_start>nested_container",
            )
            (
                adjusted_text_to_parse,
                this_bq_count,
                did_process_blank_line,
            ) = ContainerBlockProcessor.__look_for_container_blocks(
                parser_state,
                adj_line_to_parse,
                end_container_indices.block_index,
                container_depth,
                this_bq_count,
                position_marker,
                parser_properties,
            )
        parser_state.set_no_para_start_if_empty()

        return did_process_blank_line, this_bq_count, adjusted_text_to_parse

    # pylint: enable=too-many-arguments

    # pylint: disable=too-many-arguments, too-many-locals
    @staticmethod
    def __get_nested_container_starts(
        parser_state,
        line_to_parse,
        end_container_indices,
        avoid_block_starts,
        start_index,
        removed_chars_at_start,
        text_removed_by_container,
    ):
        POGGER.debug(
            "__handle_nested_container_blocks>stack>>:$:<<",
            line_to_parse,
        )
        POGGER.debug(
            "__handle_nested_container_blocks>end_container_indices>>:$:<<",
            end_container_indices,
        )

        POGGER.debug("check next container_start>")
        POGGER.debug("check next container_start>start_index>$", start_index)
        POGGER.debug(
            "check next container_start>removed_chars_at_start:$:",
            removed_chars_at_start,
        )
        POGGER.debug(
            "check next container_start>text_removed_by_container:$:",
            text_removed_by_container,
        )
        POGGER.debug("check next container_start>stack>>$", parser_state.token_stack)

        _, ex_ws_test = ParserHelper.extract_whitespace(line_to_parse, 0)

        whitespace_scan_start_index = 0
        for token_stack_index in parser_state.token_stack:
            if token_stack_index.is_block_quote:
                # if text_removed_by_container:
                #     if text_removed_by_container.startswith("> "):
                #         text_removed_by_container = text_removed_by_container[2:]
                #     elif text_removed_by_container.startswith(">"):
                #         text_removed_by_container = text_removed_by_container[1:]
                #     else:
                #         POGGER.info("check next container_start> out of block quote data")
                pass
            elif token_stack_index.is_list:
                if token_stack_index.ws_before_marker <= len(ex_ws_test):
                    whitespace_scan_start_index = token_stack_index.ws_before_marker

        after_ws_index, ex_whitespace = ParserHelper.extract_whitespace(
            line_to_parse, whitespace_scan_start_index
        )
        if not ex_whitespace:
            ex_whitespace = ""
            after_ws_index = whitespace_scan_start_index

        nested_ulist_start, _, _, _ = ListBlockProcessor.is_ulist_start(
            parser_state, line_to_parse, after_ws_index, ex_whitespace, False
        )
        nested_olist_start, _, _, _ = ListBlockProcessor.is_olist_start(
            parser_state, line_to_parse, after_ws_index, ex_whitespace, False
        )
        nested_block_start = (
            False
            if avoid_block_starts
            else BlockQuoteProcessor.is_block_quote_start(
                line_to_parse, after_ws_index, ex_whitespace
            )
        )
        POGGER.debug(
            "check next container_start>ulist>$>index>$",
            nested_ulist_start,
            end_container_indices.ulist_index,
        )
        POGGER.debug(
            "check next container_start>olist>$>index>$",
            nested_olist_start,
            end_container_indices.olist_index,
        )
        POGGER.debug(
            "check next container_start>bquote>$>index>$",
            nested_block_start,
            end_container_indices.block_index,
        )

        POGGER.debug(
            "__handle_nested_container_blocks>end_container_indices>>:$:<<",
            end_container_indices,
        )

        POGGER.debug("check next container_start>stack>>$", parser_state.token_stack)

        return ContainerIndices(
            nested_ulist_start, nested_olist_start, nested_block_start
        )

    # pylint: enable=too-many-arguments, too-many-locals

    # pylint: disable=too-many-arguments
    @staticmethod
    def __look_for_container_blocks(
        parser_state,
        adj_line_to_parse,
        end_of_bquote_start_index,
        container_depth,
        this_bq_count,
        position_marker,
        parser_properties,
    ):
        """
        Look for container blocks that we can use.
        """
        POGGER.debug("check next container_start>recursing")
        POGGER.debug("check next container_start>>$\n", adj_line_to_parse)
        POGGER.debug("this_bq_count>$", this_bq_count)
        container_start_bq_count, adj_block, position_marker = (
            this_bq_count,
            None if end_of_bquote_start_index == -1 else end_of_bquote_start_index,
            PositionMarker(position_marker.line_number, -1, adj_line_to_parse),
        )

        (
            produced_inner_tokens,
            line_to_parse,
            proposed_this_bq_count,
            requeue_line_info,
            did_process_blank_line,
        ) = ContainerBlockProcessor.parse_line_for_container_blocks(
            parser_state,
            position_marker,
            False,
            parser_properties,
            container_start_bq_count,
            container_depth=container_depth + 1,
            foobar=adj_block,
            init_bq=this_bq_count,
        )
        assert not requeue_line_info or not requeue_line_info.lines_to_requeue

        POGGER.debug("\ncheck next container_start>recursed")
        POGGER.debug("check next container_start>stack>>$", parser_state.token_stack)
        POGGER.debug(
            "check next container_start>tokenized_document>>$",
            parser_state.token_document,
        )
        POGGER.debug("check next container_start>line_parse>>$", line_to_parse)
        POGGER.debug("this_bq_count>$", this_bq_count)
        if proposed_this_bq_count:
            this_bq_count += proposed_this_bq_count
        POGGER.debug("this_bq_count>$", this_bq_count)

        POGGER.debug("parser_state.token_document>$", parser_state.token_document)
        parser_state.token_document.extend(produced_inner_tokens)
        POGGER.debug("parser_state.token_document>$", parser_state.token_document)
        POGGER.debug("did_process_blank_line>$", did_process_blank_line)
        return line_to_parse, this_bq_count, did_process_blank_line

    # pylint: enable=too-many-arguments

    @staticmethod
    def __process_list_in_progress(
        parser_state,
        line_to_parse,
        start_index,
        container_level_tokens,
        extracted_whitespace,
    ):
        did_process, used_indent, requeue_line_info = False, None, None
        did_process, ind = LeafBlockProcessor.check_for_list_in_process(parser_state)
        if did_process:
            assert not container_level_tokens
            POGGER.debug("clt>>list-in-progress")
            POGGER.debug("clt>>line_to_parse>>:$:>>", line_to_parse)
            (
                container_level_tokens,
                line_to_parse,
                used_indent,
                requeue_line_info,
            ) = ListBlockProcessor.list_in_process(
                parser_state,
                line_to_parse,
                start_index,
                extracted_whitespace,
                ind,
            )
            POGGER.debug("clt>>line_to_parse>>:$:>>", line_to_parse)
            POGGER.debug("clt>>used_indent>>:$:>>", used_indent)
            POGGER.debug("clt>>requeue_line_info>>:$:>>", requeue_line_info)

        return (
            did_process,
            line_to_parse,
            container_level_tokens,
            used_indent,
            requeue_line_info,
        )

    # pylint: disable=too-many-arguments
    @staticmethod
    def __process_lazy_lines(
        parser_state,
        leaf_tokens,
        this_bq_count,
        stack_bq_count,
        line_to_parse,
        container_level_tokens,
        container_start_bq_count,
    ):

        POGGER.debug("LINE-lazy>$", line_to_parse)
        assert not leaf_tokens
        POGGER.debug("clt>>lazy-check")

        POGGER.debug("__process_lazy_lines>>ltp>$", line_to_parse)
        after_ws_index, ex_whitespace = ParserHelper.extract_whitespace(
            line_to_parse, 0
        )
        remaining_line = line_to_parse[after_ws_index:]
        POGGER.debug("container_start_bq_count>>:$", container_start_bq_count)
        POGGER.debug("__process_lazy_lines>>this_bq_count>$<", this_bq_count)
        POGGER.debug("__process_lazy_lines>>stack_bq_count>$<", stack_bq_count)
        POGGER.debug("__process_lazy_lines>>mod->ltp>$<", remaining_line)
        POGGER.debug("__process_lazy_lines>>mod->ews>$<", ex_whitespace)

        lazy_tokens = BlockQuoteProcessor.check_for_lazy_handling(
            parser_state,
            this_bq_count,
            stack_bq_count,
            remaining_line,
            ex_whitespace,
        )
        if lazy_tokens:
            POGGER.debug("clt>>lazy-found")
            container_level_tokens.extend(lazy_tokens)

    # pylint: enable=too-many-arguments

    # pylint: disable=too-many-arguments
    @staticmethod
    def __process_leaf_tokens(
        parser_state,
        leaf_tokens,
        xposition_marker,
        this_bq_count,
        removed_chars_at_start,
        ignore_link_definition_start,
        last_block_quote_index,
        last_list_start_index,
        text_removed_by_container,
        force_it,
    ):
        assert not leaf_tokens
        POGGER.debug("parsing leaf>>")
        position_marker = PositionMarker(
            xposition_marker.line_number,
            0,
            xposition_marker.text_to_parse,
            index_indent=xposition_marker.index_indent,
        )
        (
            leaf_tokens,
            requeue_line_info,
        ) = ContainerBlockProcessor.__parse_line_for_leaf_blocks(
            parser_state,
            position_marker,
            this_bq_count,
            removed_chars_at_start,
            ignore_link_definition_start,
            last_block_quote_index,
            last_list_start_index,
            text_removed_by_container,
            force_it,
        )
        POGGER.debug("parsed leaf>>$", leaf_tokens)
        return leaf_tokens, requeue_line_info

    # pylint: enable=too-many-arguments

    @staticmethod
    def __close_indented_block_if_indent_not_there(parser_state, extracted_whitespace):

        POGGER.debug(
            "__close_indented_block_if_indent_not_there>>$>",
            parser_state.token_stack[-1],
        )
        POGGER.debug(
            "__close_indented_block_if_indent_not_there>>$>", extracted_whitespace
        )
        pre_tokens = []
        if parser_state.token_stack[
            -1
        ].is_indented_code_block and ParserHelper.is_length_less_than_or_equal_to(
            extracted_whitespace, 3
        ):
            pre_tokens.append(
                parser_state.token_stack[
                    -1
                ].generate_close_markdown_token_from_stack_token()
            )
            del parser_state.token_stack[-1]

            extracted_blank_line_tokens = (
                ContainerBlockProcessor.extract_markdown_tokens_back_to_blank_line(
                    parser_state, False
                )
            )
            extracted_blank_line_tokens.reverse()
            pre_tokens.extend(extracted_blank_line_tokens)
        POGGER.debug(
            "__close_indented_block_if_indent_not_there>>pre_tokens>$>", pre_tokens
        )
        return pre_tokens

    @staticmethod
    def __handle_fenced_code_block(
        parser_state,
        outer_processed,
        position_marker,
        extracted_whitespace,
        new_tokens,
    ):
        """
        Take care of the processing for fenced code blocks.
        """
        if not parser_state.token_stack[-1].was_link_definition_started:
            (
                fenced_tokens,
                extracted_whitespace,
            ) = LeafBlockProcessor.parse_fenced_code_block(
                parser_state,
                position_marker,
                extracted_whitespace,
            )
            outer_processed = False
            if fenced_tokens:
                new_tokens.extend(fenced_tokens)
                outer_processed = True
            elif parser_state.token_stack[-1].is_fenced_code_block:
                new_tokens.append(
                    TextMarkdownToken(
                        position_marker.text_to_parse[position_marker.index_number :],
                        extracted_whitespace,
                        position_marker=position_marker,
                    )
                )
                outer_processed = True
        return outer_processed

    @staticmethod
    def __handle_html_block(
        parser_state,
        outer_processed,
        position_marker,
        extracted_whitespace,
        new_tokens,
    ):
        """
        Take care of the processing for html blocks.
        """

        POGGER.debug(">>position_marker>>ttp>>$>>", position_marker.text_to_parse)
        POGGER.debug(">>position_marker>>in>>$>>", position_marker.index_number)
        POGGER.debug(">>position_marker>>ln>>$>>", position_marker.line_number)
        if not outer_processed and not parser_state.token_stack[-1].is_html_block:
            POGGER.debug(">>html started?>>")
            old_top_of_stack = parser_state.token_stack[-1]
            html_tokens = HtmlHelper.parse_html_block(
                parser_state,
                position_marker,
                extracted_whitespace,
            )
            if html_tokens:
                POGGER.debug(">>html started>>")
                LeafBlockProcessor.correct_for_leaf_block_start_in_list(
                    parser_state,
                    position_marker.index_indent,
                    old_top_of_stack,
                    html_tokens,
                )
            else:
                POGGER.debug(">>html not started>>")
            new_tokens.extend(html_tokens)
        if parser_state.token_stack[-1].is_html_block:
            POGGER.debug(">>html continued>>")
            html_tokens = HtmlHelper.check_normal_html_block_end(
                parser_state,
                position_marker.text_to_parse,
                position_marker.index_number,
                extracted_whitespace,
                position_marker,
            )
            assert html_tokens
            new_tokens.extend(html_tokens)
            outer_processed = True

        return outer_processed

    @staticmethod
    def __handle_block_leaf_tokens(
        parser_state,
        incoming_position_marker,
        new_tokens,
        ignore_link_definition_start,
    ):
        remaining_line_to_parse = incoming_position_marker.text_to_parse[
            incoming_position_marker.index_number :
        ]
        (new_index_number, extracted_whitespace,) = ParserHelper.extract_whitespace(
            incoming_position_marker.text_to_parse,
            incoming_position_marker.index_number,
        )
        position_marker = PositionMarker(
            incoming_position_marker.line_number,
            new_index_number,
            incoming_position_marker.text_to_parse,
            index_indent=incoming_position_marker.index_indent,
        )

        pre_tokens = ContainerBlockProcessor.__close_indented_block_if_indent_not_there(
            parser_state, extracted_whitespace
        )

        outer_processed = ContainerBlockProcessor.__handle_fenced_code_block(
            parser_state,
            False,
            position_marker,
            extracted_whitespace,
            new_tokens,
        )

        ignore_lrd_start = (
            ignore_link_definition_start or parser_state.token_stack[-1].is_html_block
        )

        (
            outer_processed,
            requeue_line_info,
        ) = LinkReferenceDefinitionHelper.handle_link_reference_definition_leaf_block(
            parser_state,
            outer_processed,
            position_marker,
            extracted_whitespace,
            remaining_line_to_parse,
            ignore_lrd_start,
            pre_tokens,
        )

        outer_processed = ContainerBlockProcessor.__handle_html_block(
            parser_state,
            outer_processed,
            position_marker,
            extracted_whitespace,
            new_tokens,
        )
        return (
            pre_tokens,
            outer_processed,
            requeue_line_info,
            position_marker,
            extracted_whitespace,
        )

    # pylint: disable=too-many-arguments,too-many-locals
    @staticmethod
    def __parse_line_for_leaf_blocks(
        parser_state,
        position_marker,
        this_bq_count,
        removed_chars_at_start,
        ignore_link_definition_start,
        last_block_quote_index,
        last_list_start_index,
        text_removed_by_container,
        force_it,
    ):
        """
        Parse the contents of a line for a leaf block.

        Note: This is one of the more heavily traffic functions in the
        parser.  Debugging should be uncommented only if needed.
        """
        POGGER.debug("Leaf Line:$:", position_marker.text_to_parse)
        # POGGER.debug("this_bq_count:$:", this_bq_count)
        new_tokens = []

        (
            pre_tokens,
            outer_processed,
            requeue_line_info,
            leaf_block_position_marker,
            extracted_whitespace,
        ) = ContainerBlockProcessor.__handle_block_leaf_tokens(
            parser_state,
            position_marker,
            new_tokens,
            ignore_link_definition_start,
        )

        if not outer_processed:
            assert not new_tokens
            new_tokens = LeafBlockProcessor.parse_atx_headings(
                parser_state, leaf_block_position_marker, extracted_whitespace
            )
            if not new_tokens:
                new_tokens = LeafBlockProcessor.parse_indented_code_block(
                    parser_state,
                    leaf_block_position_marker,
                    extracted_whitespace,
                    removed_chars_at_start,
                    last_block_quote_index,
                    last_list_start_index,
                )
            if not new_tokens:
                stack_bq_count = parser_state.count_of_block_quotes_on_stack()
                new_tokens = LeafBlockProcessor.parse_setext_headings(
                    parser_state,
                    leaf_block_position_marker,
                    extracted_whitespace,
                    this_bq_count,
                    stack_bq_count,
                )
            if not new_tokens:
                new_tokens = LeafBlockProcessor.parse_thematic_break(
                    parser_state,
                    leaf_block_position_marker,
                    extracted_whitespace,
                    this_bq_count,
                    stack_bq_count,
                )
            if not new_tokens:
                new_tokens = LeafBlockProcessor.parse_paragraph(
                    parser_state,
                    leaf_block_position_marker,
                    extracted_whitespace,
                    this_bq_count,
                    stack_bq_count,
                    text_removed_by_container,
                    force_it,
                )

        POGGER.debug(">>leaf--adding>>$", new_tokens)
        pre_tokens.extend(new_tokens)
        POGGER.debug(">>leaf--added>>$", pre_tokens)
        return pre_tokens, requeue_line_info

    @staticmethod
    def extract_markdown_tokens_back_to_blank_line(parser_state, was_forced):
        """
        Extract tokens going back to the last blank line token.
        """

        pre_tokens = []
        while parser_state.token_document[-1].is_blank_line:
            last_element = parser_state.token_document[-1]
            if was_forced:
                pre_tokens.insert(0, last_element)
            else:
                pre_tokens.append(last_element)
            del parser_state.token_document[-1]
        return pre_tokens

    # pylint: enable=too-many-arguments, too-many-locals

    @staticmethod
    def __look_for_pragmas(
        position_marker,
        line_to_parse,
        container_depth,
        extracted_whitespace,
        parser_properties,
    ):

        return (
            PragmaExtension.look_for_pragmas(
                position_marker,
                line_to_parse,
                container_depth,
                extracted_whitespace,
                parser_properties,
            )
            if parser_properties.is_pragmas_enabled
            else False
        )
