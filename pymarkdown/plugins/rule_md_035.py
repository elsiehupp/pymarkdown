"""
Module to implement a plugin that looks for inconsistent styles for thematic breaks.
"""
from typing import cast

from pymarkdown.plugin_manager.plugin_details import PluginDetails
from pymarkdown.plugin_manager.plugin_scan_context import PluginScanContext
from pymarkdown.plugin_manager.rule_plugin import RulePlugin
from pymarkdown.tokens.markdown_token import MarkdownToken
from pymarkdown.tokens.thematic_break_markdown_token import ThematicBreakMarkdownToken


class RuleMd035(RulePlugin):
    """
    Class to implement a plugin that looks for inconsistent styles for thematic breaks.
    """

    __consistent_style = "consistent"

    def __init__(self) -> None:
        super().__init__()
        self.__rule_style: str = ""
        self.__actual_style: str = ""

    def get_details(self) -> PluginDetails:
        """
        Get the details for the plugin.
        """
        return PluginDetails(
            plugin_name="hr-style",
            plugin_id="MD035",
            plugin_enabled_by_default=True,
            plugin_description="Horizontal rule style",
            plugin_version="0.5.0",
            plugin_interface_version=1,
            plugin_url="https://github.com/jackdewinter/pymarkdown/blob/main/docs/rules/rule_md035.md",
            plugin_configuration="style",
        )

    @classmethod
    def __validate_configuration_style(cls, found_value: str) -> None:
        if found_value == RuleMd035.__consistent_style:
            return
        if found_value != found_value.strip():
            raise ValueError(
                "Allowable values cannot including leading or trailing spaces."
            )
        is_valid = bool(found_value)
        if is_valid:
            for next_character in found_value:
                if next_character not in " _-*":
                    is_valid = False
                    break
        if not is_valid:
            raise ValueError(
                f"Allowable values are: {RuleMd035.__consistent_style}, "
                + "'---', '***', or any other horizontal rule text."
            )

    def initialize_from_config(self) -> None:
        """
        Event to allow the plugin to load configuration information.
        """
        self.__rule_style = self.plugin_configuration.get_string_property(
            "style",
            default_value=RuleMd035.__consistent_style,
            valid_value_fn=self.__validate_configuration_style,
        )
        if self.__rule_style != RuleMd035.__consistent_style:
            self.__actual_style = self.__rule_style

    def starting_new_file(self) -> None:
        """
        Event that the a new file to be scanned is starting.
        """
        if self.__rule_style == RuleMd035.__consistent_style:
            self.__actual_style = ""

    def next_token(self, context: PluginScanContext, token: MarkdownToken) -> None:
        """
        Event that a new token is being processed.
        """
        if token.is_thematic_break:
            break_token = cast(ThematicBreakMarkdownToken, token)
            if self.__actual_style:
                if self.__actual_style != break_token.rest_of_line:
                    extra_data = f"Expected: {self.__actual_style}, Actual: {break_token.rest_of_line}"
                    self.report_next_token_error(
                        context, token, extra_error_information=extra_data
                    )
            else:
                self.__actual_style = break_token.rest_of_line
