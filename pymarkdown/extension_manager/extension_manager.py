"""
Module to provide classes to deal with extensions.
"""
import argparse
import logging
import re
import sys
from typing import Dict, List, Optional, Tuple

from application_properties import ApplicationProperties, ApplicationPropertiesFacade
from columnar import columnar

from pymarkdown.extension_manager.extension_impl import ExtensionDetails
from pymarkdown.extension_manager.extension_manager_constants import (
    ExtensionManagerConstants,
)
from pymarkdown.extension_manager.parser_extension import ParserExtension
from pymarkdown.extensions.disallowed_raw_html import MarkdownDisallowRawHtmlExtension
from pymarkdown.extensions.extended_autolinks import MarkdownExtendedAutolinksExtension
from pymarkdown.extensions.extension_one import DebugExtension
from pymarkdown.extensions.front_matter_extension import FrontMatterExtension
from pymarkdown.extensions.markdown_strikethrough import MarkdownStrikeThroughExtension
from pymarkdown.extensions.markdown_tables import MarkdownTablesExtension
from pymarkdown.extensions.pragma_token import PragmaExtension
from pymarkdown.extensions.task_list_items import MarkdownTaskListItemsExtension
from pymarkdown.parser_helper import ParserHelper

LOGGER = logging.getLogger(__name__)


class ExtensionManager:
    """
    Manager object to take care of loading and accessing extension modules.
    """

    __extensions_prefix = "extensions"
    __argparse_subparser: Optional[argparse.ArgumentParser] = None
    __root_subparser_name = "em_subcommand"
    __id_regex = re.compile("^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$")

    __DEBUG_EXTENSION = DebugExtension()

    def __init__(self) -> None:
        self.__extension_objects: Dict[str, ParserExtension] = {}
        self.__extension_details: Dict[str, ExtensionDetails] = {}
        self.__enabled_extensions: List[str] = []
        self.__properties: Optional[ApplicationProperties] = None
        self.__is_front_matter_enabled: bool = False
        self.__is_linter_pragmas_enabled: bool = False

    def initialize(
        self,
        args: argparse.Namespace,
        properties: ApplicationProperties,
    ) -> None:
        """
        Initializes the manager by adding extensions and registering them.
        """

        self.__properties = properties
        _ = args

        all_extensions: List[ParserExtension] = [
            FrontMatterExtension(),
            PragmaExtension(),
            MarkdownTablesExtension(),
            MarkdownTaskListItemsExtension(),
            MarkdownStrikeThroughExtension(),
            MarkdownExtendedAutolinksExtension(),
            MarkdownDisallowRawHtmlExtension(),
            ExtensionManager.__DEBUG_EXTENSION,
        ]

        for next_extension_object in all_extensions:
            next_extension = next_extension_object.get_details()

            assert (
                next_extension.extension_interface_version
                == ExtensionManagerConstants.EXTENSION_INTERFACE_VERSION_BASIC
            )
            self.__extension_details[next_extension.extension_id] = next_extension
            self.__extension_objects[
                next_extension.extension_id
            ] = next_extension_object
            _ = next_extension.extension_interface_version
            _ = next_extension.extension_configuration

    def apply_configuration(self) -> None:
        """
        Apply any supplied configuration to each of the enabled extensions.
        """
        for (
            next_extension_id,
            next_extension_detail,
        ) in self.__extension_details.items():
            (
                is_enabled,
                extension_specific_facade,
            ) = self.__determine_if_extension_enabled(next_extension_detail)
            LOGGER.info("extension %s: enabled=%s", next_extension_id, is_enabled)
            if is_enabled:
                self.__enabled_extensions.append(next_extension_id)

                next_extension_object = self.__extension_objects[next_extension_id]
                next_extension_object.apply_configuration(extension_specific_facade)

        self.__is_front_matter_enabled = (
            FrontMatterExtension().get_identifier() in self.__enabled_extensions
        )
        self.__is_linter_pragmas_enabled = (
            PragmaExtension().get_identifier() in self.__enabled_extensions
        )

    @property
    def is_front_matter_enabled(self) -> bool:
        """
        Check to see if front-matter support is enabled.
        """
        return self.__is_front_matter_enabled

    @property
    def is_linter_pragmas_enabled(self) -> bool:
        """
        Check to see if linter-pragmas support is enabled.
        """
        return self.__is_linter_pragmas_enabled

    @staticmethod
    def argparse_subparser_name() -> str:
        """
        Gets the name of the subparser used to handle these extensions.
        """
        return "extensions"

    def handle_argparse_subparser(self, args: argparse.Namespace) -> int:
        """
        Handle the parsing for this subparser.
        """
        return_code, subparser_value = 0, getattr(
            args, ExtensionManager.__root_subparser_name
        )
        if subparser_value == "list":
            self.__handle_argparse_subparser_list(args)
        elif subparser_value == "info":
            return_code = self.__handle_argparse_subparser_info(args)
        else:
            assert ExtensionManager.__argparse_subparser
            ExtensionManager.__argparse_subparser.print_help()
            sys.exit(2)
        return return_code

    def __handle_argparse_subparser_list(self, args: argparse.Namespace) -> None:
        list_re = None
        if args.list_filter:
            list_re = re.compile(
                "^" + args.list_filter.replace("*", ".*").replace("?", ".") + "$"
            )

        names, show_rows = list(self.__extension_details.keys()), []
        names.sort()
        for next_extension_name in names:
            next_extension = self.__extension_details[next_extension_name]

            if (
                next_extension.extension_id
                == ExtensionManager.__DEBUG_EXTENSION.get_identifier()
                or (
                    next_extension.extension_version
                    == ExtensionManagerConstants.EXTENSION_VERSION_NOT_IMPLEMENTED
                    and not args.show_all
                )
            ):
                continue

            if list_re.match(next_extension_name) if list_re else True:
                is_enabled_now = next_extension_name in self.__enabled_extensions
                display_row = [
                    next_extension.extension_id,
                    next_extension.extension_name,
                    str(next_extension.extension_enabled_by_default),
                    str(is_enabled_now),
                    next_extension.extension_version,
                ]
                show_rows.append(display_row)

        if show_rows:
            headers = [
                "id",
                "name",
                "enabled\n(default)",
                "enabled\n(current)",
                "version",
            ]
            ExtensionManager.__print_column_output(headers, show_rows)
        else:
            print(f"No extension identifier matches the pattern '{args.list_filter}'.")

    def __handle_argparse_subparser_info(self, args: argparse.Namespace) -> int:
        if args.info_filter not in self.__extension_details:
            print(f"Unable to find an extension with an id of '{args.info_filter}'.")
            return 1

        found_extension = self.__extension_details[args.info_filter]
        show_rows: List[List[str]] = [
            ["Id", found_extension.extension_id],
            ["Name", found_extension.extension_name],
            ["Short Description", found_extension.extension_description],
            ["Description Url", str(found_extension.extension_url)],
        ]

        headers = ["Item", "Description"]
        ExtensionManager.__print_column_output(headers, show_rows)
        return 0

    @staticmethod
    def __print_column_output(headers: List[str], show_rows: List[List[str]]) -> None:
        table = columnar(show_rows, headers, no_borders=True)
        split_rows = table.split(ParserHelper.newline_character)
        new_rows = [next_row.rstrip() for next_row in split_rows]
        print(ParserHelper.newline_character.join(new_rows))

    @staticmethod
    def __list_filter_type(argument: str) -> str:
        test_argument = argument.replace("*", "").replace("?", "")
        if ExtensionManager.__id_regex.match(test_argument):
            return argument
        raise argparse.ArgumentTypeError(
            f"Value '{argument}' is not a valid pattern for an id."
        )

    @staticmethod
    def __info_filter_type(argument: str) -> str:
        if ExtensionManager.__id_regex.match(argument):
            return argument
        raise argparse.ArgumentTypeError(f"Value '{argument}' is not a valid id.")

    @staticmethod
    def add_argparse_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore
        """
        Populate the argparse tree to allow for plugin support.
        """
        new_sub_parser = subparsers.add_parser(
            ExtensionManager.argparse_subparser_name(), help="extension commands"
        )
        ExtensionManager.__argparse_subparser = new_sub_parser
        plugin_subparsers = new_sub_parser.add_subparsers(
            dest=ExtensionManager.__root_subparser_name
        )

        sub_sub_parser = plugin_subparsers.add_parser(
            "list", help="list the available extensions"
        )
        sub_sub_parser.add_argument(
            "--all",
            dest="show_all",
            action="store_true",
            default=False,
            help="show all loaded extensions (default is False)",
        )
        sub_sub_parser.add_argument(
            dest="list_filter",
            default=None,
            help="filter",
            nargs="?",
            type=ExtensionManager.__list_filter_type,
        )
        sub_sub_parser = plugin_subparsers.add_parser(
            "info", help="information on a specific extension"
        )
        sub_sub_parser.add_argument(
            dest="info_filter",
            default=None,
            type=ExtensionManager.__info_filter_type,
            help="an id",
        )

    def __determine_if_extension_enabled(
        self, extension_object: ExtensionDetails
    ) -> Tuple[bool, ApplicationPropertiesFacade]:
        """
        Given the enable and disable rule values, evaluate the enabled or disabled
        state of the extension in proper order.
        """

        new_value = None
        LOGGER.debug(
            "Extension '%s'",
            extension_object.extension_id,
        )

        assert self.__properties
        plugin_section_title = (
            f"{ExtensionManager.__extensions_prefix}{self.__properties.separator}"
            + f"{extension_object.extension_id}{self.__properties.separator}"
        )
        extension_specific_facade = ApplicationPropertiesFacade(
            self.__properties, plugin_section_title
        )
        new_value = extension_specific_facade.get_boolean_property(
            "enabled", default_value=None
        )
        if new_value is None:
            LOGGER.debug(
                "No other enable state found, setting to default of '%s'.",
                str(extension_object.extension_enabled_by_default),
            )
        else:
            LOGGER.debug(
                "Extension specific key 'enabled' found, value is '%s'.",
                str(new_value),
            )

        return (
            extension_object.extension_enabled_by_default
            if new_value is None
            else new_value
        ), extension_specific_facade
