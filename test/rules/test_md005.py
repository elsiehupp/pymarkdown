"""
Module to provide tests related to the MD005 rule.
"""

import os
from test.rules.utils import (
    build_fix_and_clash_lists,
    calculate_fix_tests,
    calculate_scan_tests,
    execute_fix_test,
    execute_query_configuration_test,
    execute_scan_test,
    id_test_plug_rule_fn,
    pluginQueryConfigTest,
    pluginRuleTest,
)

import pytest

source_path = os.path.join("test", "resources", "rules", "md005") + os.sep

__plugin_disable_md007 = "md007"
__plugin_disable_md007_md027 = "md007,md027"
__plugin_disable_md007_md029 = "md007,md029"
__plugin_disable_md029 = "md029"
__plugin_disable_md029_md030 = "md029,md030"
__plugin_disable_md033 = "md033"

scanTests = [
    pluginRuleTest(
        "good_unordered_list_single_level",
        source_file_name=f"{source_path}good_unordered_list_single_level.md",
    ),
    pluginRuleTest(
        "bad_unordered_list_single_level",
        source_file_name=f"{source_path}bad_unordered_list_single_level.md",
        disable_rules=__plugin_disable_md007,
        source_file_contents="""* Item 1
 * Item 2
""",
        scan_expected_return_code=1,
        scan_expected_output="{temp_source_path}:2:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)",
        fix_expected_file_contents="""* Item 1
* Item 2
""",
    ),
    pluginRuleTest(
        "good_unordered_list_double_level",
        source_file_name=f"{source_path}good_unordered_list_double_level.md",
    ),
    pluginRuleTest(
        "bad_unordered_list_double_level_bad_first",
        source_file_name=f"{source_path}bad_unordered_list_double_level_bad_first.md",
        disable_rules=__plugin_disable_md007,
        source_file_contents="""* Item 1
  * Item 1a
  * Item 1b
 * Item 2
   * Item 2a
   * Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output=(
            "{temp_source_path}:4:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)\n"
            + "{temp_source_path}:5:4: MD005: Inconsistent indentation for list items at the same level [Expected: 2; Actual: 3] (list-indent)\n"
            + "{temp_source_path}:6:4: MD005: Inconsistent indentation for list items at the same level [Expected: 2; Actual: 3] (list-indent)"
        ),
        fix_expected_file_contents="""* Item 1
  * Item 1a
  * Item 1b
* Item 2
  * Item 2a
  * Item 2b
""",
    ),
    pluginRuleTest(
        "bad_unordered_list_double_level_bad_second",
        source_file_name=f"{source_path}bad_unordered_list_double_level_bad_second.md",
        disable_rules=__plugin_disable_md007,
        source_file_contents="""* Item 1
  * Item 1a
  * Item 1b
* Item 2
  * Item 2a
   * Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output="{temp_source_path}:6:4: MD005: Inconsistent indentation for list items at the same level [Expected: 2; Actual: 3] (list-indent)",
        fix_expected_file_contents="""* Item 1
  * Item 1a
  * Item 1b
* Item 2
  * Item 2a
  * Item 2b
""",
    ),
    pluginRuleTest(
        "good_unordered_list_separate_lists",
        source_file_name=f"{source_path}good_unordered_list_separate_lists.md",
        disable_rules=__plugin_disable_md007,
    ),
    pluginRuleTest(
        "bad_unordered_list_single_level_twice",
        source_file_name=f"{source_path}bad_unordered_list_single_level_twice.md",
        disable_rules=__plugin_disable_md007,
        source_file_contents="""* Item 1
 * Item 2
 * Item 2
""",
        scan_expected_return_code=1,
        scan_expected_output=(
            "{temp_source_path}:2:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)\n"
            + "{temp_source_path}:3:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)"
        ),
        fix_expected_file_contents="""* Item 1
* Item 2
* Item 2
""",
    ),
    pluginRuleTest(
        "good_ordered_list_single_level",
        source_file_name=f"{source_path}good_ordered_list_single_level.md",
    ),
    pluginRuleTest(
        "bad_ordered_list_single_level_x",
        source_file_name=f"{source_path}bad_ordered_list_single_level.md",
        source_file_contents="""1. Item 1
 1. Item 2
""",
        scan_expected_return_code=1,
        scan_expected_output="{temp_source_path}:2:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)",
        fix_expected_file_contents="""1. Item 1
1. Item 2
""",
    ),
    pluginRuleTest(
        "good_ordered_list_single_level_widths",
        source_file_name=f"{source_path}good_ordered_list_single_level_widths.md",
        disable_rules=__plugin_disable_md029,
    ),
    pluginRuleTest(
        "bad_ordered_list_single_level_widths",
        source_file_name=f"{source_path}bad_ordered_list_single_level_widths.md",
        disable_rules=__plugin_disable_md029,
        source_file_contents="""1. Item 1
 100. Item 3
""",
        scan_expected_return_code=1,
        scan_expected_output="{temp_source_path}:2:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)",
        fix_expected_file_contents="""1. Item 1
100. Item 3
""",
    ),
    pluginRuleTest(
        "good_ordered_list_single_level_widths_right",
        source_file_name=f"{source_path}good_ordered_list_single_level_widths_right.md",
        disable_rules=__plugin_disable_md029,
    ),
    pluginRuleTest(
        "bad_ordered_list_single_level_widths_right",
        source_file_name=f"{source_path}bad_ordered_list_single_level_widths_right.md",
        disable_rules=__plugin_disable_md029,
        source_file_contents="""   1. Item 1
10. Item 2
""",
        scan_expected_return_code=1,
        scan_expected_output="{temp_source_path}:2:1: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 0] (list-indent)",
        fix_expected_file_contents="""   1. Item 1
   10. Item 2
""",
    ),
    pluginRuleTest(
        "good_ordered_list_single_level_short_widths_right",
        source_file_name=f"{source_path}good_ordered_list_single_level_short_widths_right.md",
        disable_rules=__plugin_disable_md029,
    ),
    pluginRuleTest(
        "good_ordered_list_separate_single_level_short_widths_right",
        source_file_name=f"{source_path}good_ordered_list_seperate_single_level_short_widths_right.md",
        disable_rules=__plugin_disable_md029,
    ),
    pluginRuleTest(
        "good_ordered_list_separate_single_level_short_widths",
        source_file_name=f"{source_path}good_ordered_list_seperate_single_level_short_widths.md",
        disable_rules=__plugin_disable_md029_md030,
    ),
    pluginRuleTest(
        "good_ordered_list_double_level",
        source_file_name=f"{source_path}good_ordered_list_double_level.md",
        disable_rules=__plugin_disable_md029,
    ),
    pluginRuleTest(
        "good_ordered_list_double_level_right",
        source_file_name=f"{source_path}good_ordered_list_double_level_right.md",
        disable_rules=__plugin_disable_md029,
    ),
    pluginRuleTest(
        "bad_ordered_list_double_level_weirdx",
        source_file_name=f"{source_path}bad_ordered_list_double_level_weird.md",
        disable_rules=__plugin_disable_md029,
        source_file_contents="""1. Item 1
   1. Item 1a
    100. Item 1b
""",
        scan_expected_return_code=1,
        scan_expected_output="{temp_source_path}:3:5: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 4] (list-indent)",
        fix_expected_file_contents="""1. Item 1
   1. Item 1a
   100. Item 1b
""",
    ),
    pluginRuleTest(
        "bad_ordered_list_double_level_weirder",
        source_file_name=f"{source_path}bad_ordered_list_double_level_weirder.md",
        disable_rules=__plugin_disable_md029,
        source_file_contents="""1. Item 1
   1. Item 1a
  100. Item 1b
""",
        scan_expected_return_code=1,
        scan_expected_output="{temp_source_path}:3:3: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 2] (list-indent)",
        fix_expected_file_contents="""1. Item 1
   1. Item 1a
100. Item 1b
""",
    ),
    pluginRuleTest(
        "good_unordered_list_double_level_in_block_quote",
        source_file_name=f"{source_path}good_unordered_list_double_level_in_block_quote.md",
    ),
    pluginRuleTest(
        "bad_unordered_list_double_level_in_block_quote_first",
        source_file_name=f"{source_path}bad_unordered_list_double_level_in_block_quote_first.md",
        disable_rules=__plugin_disable_md007_md027,
        source_file_contents="""> * Item 1
>    * Item 1a
>    * Item 1b
>  * Item 2
>    * Item 2a
>    * Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output="{temp_source_path}:4:4: MD005: Inconsistent indentation for list items at the same level [Expected: 2; Actual: 3] (list-indent)",
        fix_expected_file_contents="""> * Item 1
>    * Item 1a
>    * Item 1b
> * Item 2
>    * Item 2a
>    * Item 2b
""",
    ),
    pluginRuleTest(
        "bad_unordered_list_double_level_in_block_quote_second",
        source_file_name=f"{source_path}bad_unordered_list_double_level_in_block_quote_second.md",
        disable_rules=__plugin_disable_md007,
        source_file_contents="""> * Item 1
>   * Item 1a
>   * Item 1b
> * Item 2
>    * Item 2a
>    * Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output="{temp_source_path}:5:6: MD005: Inconsistent indentation for list items at the same level [Expected: 4; Actual: 5] (list-indent)\n"
        + "{temp_source_path}:6:6: MD005: Inconsistent indentation for list items at the same level [Expected: 4; Actual: 5] (list-indent)",
        fix_expected_file_contents="""> * Item 1
>   * Item 1a
>   * Item 1b
> * Item 2
>   * Item 2a
>   * Item 2b
""",
    ),
    pluginRuleTest(
        "bad_ordered_list_double_level_left",
        source_file_name=f"{source_path}bad_ordered_list_double_level_left.md",
        disable_rules=__plugin_disable_md029,
        source_file_contents="""1. Item 1
   1. Item 1a
   10. Item 1b
2. Item 2
    1. Item 2a
    10. Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output=(
            "{temp_source_path}:5:5: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 4] (list-indent)\n"
            + "{temp_source_path}:6:5: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 4] (list-indent)"
        ),
        fix_expected_file_contents="""1. Item 1
   1. Item 1a
   10. Item 1b
2. Item 2
   1. Item 2a
   10. Item 2b
""",
    ),
    pluginRuleTest(
        "bad_ordered_list_double_level_right_x",
        source_file_name=f"{source_path}bad_ordered_list_double_level_right.md",
        disable_rules=__plugin_disable_md029,
        source_file_contents="""1. Item 1
    1. Item 1a
   10. Item 1b
2. Item 2
     1. Item 2a
    10. Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output=(
            "{temp_source_path}:5:6: MD005: Inconsistent indentation for list items at the same level [Expected: 4; Actual: 5] (list-indent)\n"
            + "{temp_source_path}:6:5: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 4] (list-indent)"
        ),
        fix_expected_file_contents="""1. Item 1
    1. Item 1a
   10. Item 1b
2. Item 2
    1. Item 2a
   10. Item 2b
""",
    ),
    pluginRuleTest(
        "bad_ordered_list_double_level_left_then_right",
        source_file_name=f"{source_path}bad_ordered_list_double_level_left_then_right.md",
        disable_rules=__plugin_disable_md029,
        source_file_contents="""1. Item 1
   1. Item 1a
   10. Item 1b
2. Item 2
    1. Item 2a
   10. Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output="{temp_source_path}:5:5: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 4] (list-indent)",
        fix_expected_file_contents="""1. Item 1
   1. Item 1a
   10. Item 1b
2. Item 2
   1. Item 2a
   10. Item 2b
""",
    ),
    pluginRuleTest(
        "bad_ordered_list_double_level_right_then_left",
        source_file_name=f"{source_path}bad_ordered_list_double_level_right_then_left.md",
        disable_rules=__plugin_disable_md029,
        source_file_contents="""1. Item 1
    1. Item 1a
   10. Item 1b
2. Item 2
   1. Item 2a
   10. Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output="{temp_source_path}:5:4: MD005: Inconsistent indentation for list items at the same level [Expected: 4; Actual: 3] (list-indent)",
        fix_expected_file_contents="""1. Item 1
    1. Item 1a
   10. Item 1b
2. Item 2
    1. Item 2a
   10. Item 2b
""",
    ),
    pluginRuleTest(
        "bad_ordered_list_single_level_left_then_right",
        source_file_name=f"{source_path}bad_ordered_list_single_level_left_then_right.md",
        disable_rules=__plugin_disable_md029,
        source_file_contents="""1. Item 1
10. Item 2
 2. Item 3
""",
        scan_expected_return_code=1,
        scan_expected_output="{temp_source_path}:3:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)",
        fix_expected_file_contents="""1. Item 1
10. Item 2
2. Item 3
""",
    ),
    pluginRuleTest(
        "bad_ordered_list_single_level_right_then_left",
        source_file_name=f"{source_path}bad_ordered_list_single_level_right_then_left.md",
        disable_rules=__plugin_disable_md029,
        source_file_contents=""" 1. Item 1
10. Item 2
2. Item 3
""",
        scan_expected_return_code=1,
        scan_expected_output="{temp_source_path}:3:1: MD005: Inconsistent indentation for list items at the same level [Expected: 1; Actual: 0] (list-indent)",
        fix_expected_file_contents=""" 1. Item 1
10. Item 2
 2. Item 3
""",
    ),
    pluginRuleTest(
        "bad_ordered_left_unordered_x",
        disable_rules=__plugin_disable_md007_md029,
        source_file_contents="""1. Item 1
   + Item 1a
   + Item 1b
 10. Item 2
     + Item 2a
     + Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:4:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)
{temp_source_path}:5:6: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 5] (list-indent)
{temp_source_path}:6:6: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 5] (list-indent)
""",
        fix_expected_file_contents="""1. Item 1
   + Item 1a
   + Item 1b
10. Item 2
    + Item 2a
    + Item 2b
""",
    ),
    pluginRuleTest(
        "bad_ordered_right_unordered_x_0",
        disable_rules=__plugin_disable_md007_md029,
        source_file_contents=""" 1. Item 1
    + Item 1a
    + Item 1b
 9. Item 2
    + Item 2a
    + Item 2b
""",
        scan_expected_return_code=0,
        scan_expected_output="",
    ),
    pluginRuleTest(
        "bad_ordered_right_unordered_x_1",
        disable_rules=__plugin_disable_md007_md029,
        source_file_contents=""" 1. Item 1
    + Item 1a
    + Item 1b
 9. Item 2
     + Item 2a
     + Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:5:6: MD005: Inconsistent indentation for list items at the same level [Expected: 4; Actual: 5] (list-indent)
{temp_source_path}:6:6: MD005: Inconsistent indentation for list items at the same level [Expected: 4; Actual: 5] (list-indent)
""",
        fix_expected_file_contents=""" 1. Item 1
    + Item 1a
    + Item 1b
 9. Item 2
    + Item 2a
    + Item 2b
""",
        mark_fix_as_skipped=True,
    ),
    pluginRuleTest(
        "bad_ordered_right_unordered_x_2",
        disable_rules=__plugin_disable_md007_md029,
        source_file_contents=""" 1. Item 1
    + Item 1a
    + Item 1b
 10. Item 2
     + Item 2a
     + Item 2b
""",
        scan_expected_return_code=0,
        scan_expected_output="",
    ),
    pluginRuleTest(
        "bad_unordered_ordered_left_x",
        disable_rules=__plugin_disable_md007_md029,
        source_file_contents="""+ Item 1
   1. Item 1a
   10. Item 1b
 + Item 2
    1. Item 2a
    10. Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:4:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)
{temp_source_path}:5:5: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 4] (list-indent)
{temp_source_path}:6:5: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 4] (list-indent)
""",
        fix_expected_file_contents="""+ Item 1
   1. Item 1a
   10. Item 1b
+ Item 2
   1. Item 2a
   10. Item 2b
""",
    ),
    pluginRuleTest(
        "bad_unordered_ordered_right_x",
        disable_rules=__plugin_disable_md007_md029,
        source_file_contents="""+ Item 1
   1. Item 1a
   10. Item 1b
 + Item 2
     1. Item 2a
    10. Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:4:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)
{temp_source_path}:5:6: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 5] (list-indent)
{temp_source_path}:6:5: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 4] (list-indent)
""",
        #         fix_expected_file_contents="""+ Item 1
        #    1. Item 1a
        #    10. Item 1b
        # + Item 2
        #    1. Item 2a
        #    10. Item 2b
        # """,
    ),
    pluginRuleTest(
        "bad_unordered_lt_with_text_fix",
        disable_rules=__plugin_disable_md007,
        source_file_contents="""+ Item 1
  more Item 1
 + Item 2
   more Item 2
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:3:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)""",
        fix_expected_file_contents="""+ Item 1
  more Item 1
+ Item 2
  more Item 2
""",
    ),
    pluginRuleTest(
        "bad_unordered_lt_with_double_text_fix",
        disable_rules=__plugin_disable_md007,
        source_file_contents="""+ Item 1
  more Item 1
 + Item 2
   more Item 2
 + Item 3
   more Item 3
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:3:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)
{temp_source_path}:5:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)""",
        fix_expected_file_contents="""+ Item 1
  more Item 1
+ Item 2
  more Item 2
+ Item 3
  more Item 3
""",
    ),
    pluginRuleTest(
        "bad_unordered_lt_with_text_nested_fix",
        disable_rules=__plugin_disable_md007,
        source_file_contents="""+ Item 1
  more Item 1
   + Item 1a
     more Item 1a
   + Item 1b
     more Item 1b
 + Item 2
   more Item 2
    + Item 2a
      more Item 2a
    + Item 2b
      more Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:7:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)
{temp_source_path}:9:5: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 4] (list-indent)
{temp_source_path}:11:5: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 4] (list-indent)""",
        fix_expected_file_contents="""+ Item 1
  more Item 1
   + Item 1a
     more Item 1a
   + Item 1b
     more Item 1b
+ Item 2
  more Item 2
   + Item 2a
     more Item 2a
   + Item 2b
     more Item 2b
""",
    ),
    pluginRuleTest(
        "test_md005_bad_unordered_gt_with_text_fix",
        disable_rules=__plugin_disable_md007,
        source_file_contents="""  + Item 1
    more Item 1
 + Item 2
   more Item 2
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:3:2: MD005: Inconsistent indentation for list items at the same level [Expected: 2; Actual: 1] (list-indent)""",
        fix_expected_file_contents="""  + Item 1
    more Item 1
  + Item 2
    more Item 2
""",
    ),
    pluginRuleTest(
        "bad_unordered_gt_with_double_text_fix",
        disable_rules=__plugin_disable_md007,
        source_file_contents="""  + Item 1
    more Item 1
 + Item 2
   more Item 2
 + Item 3
   more Item 3
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:3:2: MD005: Inconsistent indentation for list items at the same level [Expected: 2; Actual: 1] (list-indent)
{temp_source_path}:5:2: MD005: Inconsistent indentation for list items at the same level [Expected: 2; Actual: 1] (list-indent)""",
        fix_expected_file_contents="""  + Item 1
    more Item 1
  + Item 2
    more Item 2
  + Item 3
    more Item 3
""",
    ),
    pluginRuleTest(
        "bad_unordered_gt_with_text_nested_fix",
        disable_rules=__plugin_disable_md007,
        source_file_contents="""+ Item 1
  more Item 1
    + Item 1a
      more Item 1a
    + Item 1b
      more Item 1b
 + Item 2
   more Item 2
   + Item 2a
     more Item 2a
   + Item 2b
     more Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:7:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)
{temp_source_path}:9:4: MD005: Inconsistent indentation for list items at the same level [Expected: 4; Actual: 3] (list-indent)
{temp_source_path}:11:4: MD005: Inconsistent indentation for list items at the same level [Expected: 4; Actual: 3] (list-indent)""",
        fix_expected_file_contents="""+ Item 1
  more Item 1
    + Item 1a
      more Item 1a
    + Item 1b
      more Item 1b
+ Item 2
  more Item 2
    + Item 2a
      more Item 2a
    + Item 2b
      more Item 2b
""",
    ),
    pluginRuleTest(
        "bad_ordered_lt_with_text_fix",
        source_file_contents="""1. Item 1
   more Item 1
 1. Item 2
    more Item 2
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:3:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)""",
        fix_expected_file_contents="""1. Item 1
   more Item 1
1. Item 2
   more Item 2
""",
    ),
    pluginRuleTest(
        "bad_ordered_lt_with_double_text_fix",
        source_file_contents="""1. Item 1
   more Item 1
 2. Item 2
    more Item 2
 3. Item 3
    more Item 3
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:3:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)
{temp_source_path}:5:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)""",
        fix_expected_file_contents="""1. Item 1
   more Item 1
2. Item 2
   more Item 2
3. Item 3
   more Item 3
""",
    ),
    pluginRuleTest(
        "bad_ordered_lt_with_double_text_with_raw_html_fix",
        disable_rules=__plugin_disable_md033,
        source_file_contents="""1. Item 1
   more Item 1
 2. Item 2 <b2
    data="foo" > and inline HTML
 3. Item 3
    more Item 3
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:3:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)
{temp_source_path}:5:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)""",
        fix_expected_file_contents="""1. Item 1
   more Item 1
2. Item 2 <b2
   data="foo" > and inline HTML
3. Item 3
   more Item 3
""",
    ),
    pluginRuleTest(
        "bad_ordered_lt_with_text_nested_fix",
        source_file_contents="""1. Item 1
   more Item 1
    1. Item 1a
       more Item 1a
    2. Item 1b
       more Item 1b
 2. Item 2
    more Item 2
     1. Item 2a
        more Item 2a
     2. Item 2b
        more Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:7:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)
{temp_source_path}:9:6: MD005: Inconsistent indentation for list items at the same level [Expected: 4; Actual: 5] (list-indent)
{temp_source_path}:11:6: MD005: Inconsistent indentation for list items at the same level [Expected: 4; Actual: 5] (list-indent)""",
        fix_expected_file_contents="""1. Item 1
   more Item 1
    1. Item 1a
       more Item 1a
    2. Item 1b
       more Item 1b
2. Item 2
   more Item 2
    1. Item 2a
       more Item 2a
    2. Item 2b
       more Item 2b
""",
    ),
    pluginRuleTest(
        "bad_ordered_gt_with_text_fix",
        source_file_contents="""  1. Item 1
     more Item 1
 2. Item 2
    more Item 2
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:3:2: MD005: Inconsistent indentation for list items at the same level [Expected: 2; Actual: 1] (list-indent)""",
        fix_expected_file_contents="""  1. Item 1
     more Item 1
  2. Item 2
     more Item 2
""",
    ),
    pluginRuleTest(
        "bad_ordered_gt_with_double_text_fix",
        disable_rules=__plugin_disable_md029,
        source_file_contents="""  1. Item 1
     more Item 1
 2. Item 2
    more Item 2
 2. Item 3
    more Item 3
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:3:2: MD005: Inconsistent indentation for list items at the same level [Expected: 2; Actual: 1] (list-indent)
{temp_source_path}:5:2: MD005: Inconsistent indentation for list items at the same level [Expected: 2; Actual: 1] (list-indent)""",
        fix_expected_file_contents="""  1. Item 1
     more Item 1
  2. Item 2
     more Item 2
  2. Item 3
     more Item 3
""",
    ),
    pluginRuleTest(
        "bad_ordered_gt_with_text_nested_fix",
        source_file_contents="""1. Item 1
   more Item 1
     1. Item 1a
        more Item 1a
     2. Item 1b
        more Item 1b
 2. Item 2
    more Item 2
    1. Item 2a
       more Item 2a
    2. Item 2b
       more Item 2b
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:7:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)
{temp_source_path}:9:5: MD005: Inconsistent indentation for list items at the same level [Expected: 5; Actual: 4] (list-indent)
{temp_source_path}:11:5: MD005: Inconsistent indentation for list items at the same level [Expected: 5; Actual: 4] (list-indent)""",
        fix_expected_file_contents="""1. Item 1
   more Item 1
     1. Item 1a
        more Item 1a
     2. Item 1b
        more Item 1b
2. Item 2
   more Item 2
     1. Item 2a
        more Item 2a
     2. Item 2b
        more Item 2b
""",
    ),
    pluginRuleTest(
        "issue-1357",
        source_file_contents="""1. numbered list
2. numbered list
3. numbered list
4. numbered list
5. numbered list
6. numbered list
7. numbered list
8. numbered list
   - sub lite item at double digit text level
9. numbered list
   - sub lite item at double digit text level
10. numbered list
    - sub lite item at double digit text level
11. numbered list
""",
        scan_expected_return_code=0,
    ),
    pluginRuleTest(
        "issue-1387-a",
        source_file_contents="""1. numbered list
2. numbered list
3. numbered list
4. numbered list
5. numbered list
6. numbered list
7. numbered list
8. numbered list
9. numbered list

   - sub list item at double digit text level

10. numbered list

    - sub lite item at double digit text level

11. numbered list
""",
        scan_expected_return_code=0,
    ),
    pluginRuleTest(
        "issue-1387-b",
        source_file_contents="""1. numbered list
2. numbered list
3. numbered list
4. numbered list
5. numbered list
6. numbered list
7. numbered list
8. numbered list
9. numbered list
10. numbered list

    - sub list item at double digit text level
    - sub lite item at double digit text level

11. numbered list
""",
        scan_expected_return_code=0,
    ),
    pluginRuleTest(
        "issue-1387-c",
        source_file_contents="""1. numbered list
2. numbered list
3. numbered list
4. numbered list
5. numbered list
6. numbered list
7. numbered list
8. numbered list
9. numbered list
   - sub list item at double digit text level
   - sub lite item at double digit text level
10. numbered list
    - sub list item at double digit text level
    - sub lite item at double digit text level
11. numbered list
""",
        scan_expected_return_code=0,
    ),
    pluginRuleTest(
        "issue-1387-d",
        source_file_contents="""1. numbered list
2. numbered list
3. numbered list
4. numbered list
5. numbered list
6. numbered list
7. numbered list
8. numbered list
   - sub list item at double digit text level
   - sub lite item at double digit text level
9. numbered list
   - sub list item at double digit text level
   - sub lite item at double digit text level
10. numbered list
    - sub list item at double digit text level
    - sub lite item at double digit text level
11. numbered list
""",
        scan_expected_return_code=0,
    ),
    pluginRuleTest(
        "issue-1387-e",
        source_file_contents="""1. numbered list
2. numbered list
3. numbered list
4. numbered list
5. numbered list
6. numbered list
7. numbered list
8. numbered list
   - sub list item at double digit text level
9. numbered list
   - sub list item at double digit text level
10. numbered list
    - sub list item at double digit text level
    - sub lite item at double digit text level
11. numbered list
""",
        scan_expected_return_code=0,
    ),
    pluginRuleTest(
        "issue-1387-f",
        source_file_contents="""1. numbered list
2. numbered list
3. numbered list
4. numbered list
5. numbered list
6. numbered list
7. numbered list
8. numbered list
9. numbered list
10. numbered list

    - sub list item at double digit text level
    - sub lite item at double digit text level
    - sub lite item at double digit text level

11. numbered list
""",
        scan_expected_return_code=0,
    ),
    pluginRuleTest(
        "issue-1387-g",
        disable_rules=__plugin_disable_md007,
        source_file_contents="""1. numbered list
2. numbered list
3. numbered list
4. numbered list
5. numbered list
6. numbered list
7. numbered list
8. numbered list
9. numbered list
10. numbered list
     - sub list item at double digit text level
     - sub lite item at double digit text level
11. numbered list
""",
        scan_expected_return_code=0,
    ),
    pluginRuleTest(
        "issue-1387-h",
        disable_rules=__plugin_disable_md007,
        source_file_contents="""1. numbered list
2. numbered list
3. numbered list
4. numbered list
5. numbered list
6. numbered list
7. numbered list
8. numbered list
9. numbered list
   - sub list item at double digit text level
   - sub lite item at double digit text level
10. numbered list
     - sub list item at double digit text level
     - sub lite item at double digit text level
11. numbered list
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:13:6: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 5] (list-indent)
{temp_source_path}:14:6: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 5] (list-indent)""",
        fix_expected_file_contents="""1. numbered list
2. numbered list
3. numbered list
4. numbered list
5. numbered list
6. numbered list
7. numbered list
8. numbered list
9. numbered list
   - sub list item at double digit text level
   - sub lite item at double digit text level
10. numbered list
    - sub list item at double digit text level
    - sub lite item at double digit text level
11. numbered list
""",
    ),
    pluginRuleTest(
        "issue-1387-i",
        source_file_contents="""1. elt 1
    * unordered lvl 1 elt
    * unordered lvl 1 elt
        * unordered lvl 2 elt
2. elt 2
3. elt 3
4. elt 4
5. elt 5
6. elt 6
7. elt 7
8. elt 8
9. elt 9
10. elt 10
    * unordered lvl 1 elt
""",
        scan_expected_return_code=0,
        disable_rules=__plugin_disable_md007,
    ),
    pluginRuleTest(
        "issue-1387-j",
        source_file_contents="""1. elt 1
2. elt 2
3. elt 3
4. elt 4
5. elt 5
6. elt 6
7. elt 7
8. elt 8
9. elt 9
    * unordered lvl 1 elt
    * unordered lvl 1 elt
        * unordered lvl 2 elt
10. elt 10
    * unordered lvl 1 elt
""",
        scan_expected_return_code=0,
        disable_rules=__plugin_disable_md007,
    ),
    pluginRuleTest(
        "mix_md005_md007_only_md005_1",
        disable_rules=__plugin_disable_md007,
        source_file_contents=""" + first
   + second
     + third
+ first
  + second
    + third
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:4:1: MD005: Inconsistent indentation for list items at the same level [Expected: 1; Actual: 0] (list-indent)
{temp_source_path}:5:3: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 2] (list-indent)
{temp_source_path}:6:5: MD005: Inconsistent indentation for list items at the same level [Expected: 5; Actual: 4] (list-indent)
""",
        fix_expected_file_contents=""" + first
   + second
     + third
 + first
   + second
     + third
""",
    ),
    pluginRuleTest(
        "mix_md005_md007_only_md005_2",
        disable_rules=__plugin_disable_md007,
        source_file_contents=""" + first
    + second
       + third
+ first
  + second
    + third
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:4:1: MD005: Inconsistent indentation for list items at the same level [Expected: 1; Actual: 0] (list-indent)
{temp_source_path}:5:3: MD005: Inconsistent indentation for list items at the same level [Expected: 4; Actual: 2] (list-indent)
{temp_source_path}:6:5: MD005: Inconsistent indentation for list items at the same level [Expected: 7; Actual: 4] (list-indent)
""",
        fix_expected_file_contents=""" + first
    + second
       + third
 + first
    + second
       + third
""",
    ),
    pluginRuleTest(
        "mix_md005_md007",
        source_file_contents=""" + first
   + second
     + third
+ first
  + second
    + third
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:1:2: MD007: Unordered list indentation [Expected: 0, Actual=1] (ul-indent)
{temp_source_path}:2:4: MD007: Unordered list indentation [Expected: 2, Actual=3] (ul-indent)
{temp_source_path}:3:6: MD007: Unordered list indentation [Expected: 4, Actual=5] (ul-indent)
{temp_source_path}:4:1: MD005: Inconsistent indentation for list items at the same level [Expected: 1; Actual: 0] (list-indent)
{temp_source_path}:5:3: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 2] (list-indent)
{temp_source_path}:6:5: MD005: Inconsistent indentation for list items at the same level [Expected: 5; Actual: 4] (list-indent)
""",
        fix_expected_file_contents="""+ first
  + second
    + third
+ first
  + second
    + third
""",
    ),
    pluginRuleTest(
        "mix_md005_md027",
        source_file_contents=""">  * Heading 1
>   * Heading 2
""",
        disable_rules=__plugin_disable_md007,
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:1:3: MD027: Multiple spaces after blockquote symbol (no-multiple-space-blockquote)
{temp_source_path}:2:3: MD027: Multiple spaces after blockquote symbol (no-multiple-space-blockquote)
{temp_source_path}:2:5: MD005: Inconsistent indentation for list items at the same level [Expected: 3; Actual: 4] (list-indent)
""",
        fix_expected_file_contents="""> * Heading 1
> * Heading 2
""",
    ),
    pluginRuleTest(
        "mix_md005_md029",
        source_file_contents="""1. Heading 1
 9. Heading 2
    1. Heading 2
     9. Heading 2
""",
        disable_rules=__plugin_disable_md007,
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:2:2: MD005: Inconsistent indentation for list items at the same level [Expected: 0; Actual: 1] (list-indent)
{temp_source_path}:2:2: MD029: Ordered list item prefix [Expected: 2; Actual: 9; Style: 1/2/3] (ol-prefix)
{temp_source_path}:4:6: MD005: Inconsistent indentation for list items at the same level [Expected: 4; Actual: 5] (list-indent)
{temp_source_path}:4:6: MD029: Ordered list item prefix [Expected: 2; Actual: 9; Style: 1/2/3] (ol-prefix)
""",
        fix_expected_file_contents="""1. Heading 1
2. Heading 2
    1. Heading 2
    2. Heading 2
""",
    ),
    pluginRuleTest(
        "mix_md005_md030",
        source_file_contents="""+  Heading 1
 +  Heading 2
    +  Heading 3
     +  Heading 4
""",
        disable_rules=__plugin_disable_md007,
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:1:1: MD030: Spaces after list markers [Expected: 1; Actual: 2] (list-marker-space)
{temp_source_path}:2:2: MD005: Inconsistent indentation for list items at the same level [Expected: 1; Actual: 1] (list-indent)
{temp_source_path}:2:2: MD030: Spaces after list markers [Expected: 1; Actual: 2] (list-marker-space)
{temp_source_path}:3:5: MD030: Spaces after list markers [Expected: 1; Actual: 2] (list-marker-space)
{temp_source_path}:4:6: MD005: Inconsistent indentation for list items at the same level [Expected: 5; Actual: 5] (list-indent)
{temp_source_path}:4:6: MD030: Spaces after list markers [Expected: 1; Actual: 2] (list-marker-space)
""",
        fix_expected_file_contents="""+ Heading 1
+ Heading 2
    + Heading 3
    + Heading 4
""",
    ),
    pluginRuleTest(
        "mix_md005_md007_md030",
        source_file_contents="""+  Heading 1
 +  Heading 2
    +  Heading 3
     +  Heading 4
""",
        scan_expected_return_code=1,
        scan_expected_output="""{temp_source_path}:1:1: MD030: Spaces after list markers [Expected: 1; Actual: 2] (list-marker-space)
{temp_source_path}:2:2: MD005: Inconsistent indentation for list items at the same level [Expected: 1; Actual: 1] (list-indent)
{temp_source_path}:2:2: MD007: Unordered list indentation [Expected: 0, Actual=1] (ul-indent)
{temp_source_path}:2:2: MD030: Spaces after list markers [Expected: 1; Actual: 2] (list-marker-space)
{temp_source_path}:3:5: MD007: Unordered list indentation [Expected: 2, Actual=4] (ul-indent)
{temp_source_path}:3:5: MD030: Spaces after list markers [Expected: 1; Actual: 2] (list-marker-space)
{temp_source_path}:4:6: MD005: Inconsistent indentation for list items at the same level [Expected: 5; Actual: 5] (list-indent)
{temp_source_path}:4:6: MD007: Unordered list indentation [Expected: 2, Actual=5] (ul-indent)
{temp_source_path}:4:6: MD030: Spaces after list markers [Expected: 1; Actual: 2] (list-marker-space)
""",
        fix_expected_file_contents="""+ Heading 1
+ Heading 2
  + Heading 3
  + Heading 4
""",
    ),
]
fixTests, clashTests = build_fix_and_clash_lists(scanTests)


@pytest.mark.parametrize(
    "test", calculate_scan_tests(scanTests), ids=id_test_plug_rule_fn
)
def test_md005_scan(test: pluginRuleTest) -> None:
    """
    Execute a parameterized scan test for plugin md001.
    """
    execute_scan_test(test, "md005")


@pytest.mark.parametrize(
    "test", calculate_fix_tests(scanTests), ids=id_test_plug_rule_fn
)
def test_md005_fix(test: pluginRuleTest) -> None:
    """
    Execute a parameterized fix test for plugin md001.
    """
    execute_fix_test(test)


def test_md005_query_config() -> None:
    config_test = pluginQueryConfigTest(
        "md005",
        """
  ITEM               DESCRIPTION

  Id                 md005
  Name(s)            list-indent
  Short Description  Inconsistent indentation for list items at the same level
  Description Url    https://pymarkdown.readthedocs.io/en/latest/plugins/rule_
                     md005.md

""",
    )
    execute_query_configuration_test(config_test)
