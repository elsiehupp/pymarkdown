"""
https://github.com/jackdewinter/pymarkdown/issues/456
"""

from test.utils import act_and_assert

import pytest

## need doubles and mixes with list cases
# test_whitespaces_thematic_breaks_with_tabs_before_within_double_block_quotes_with_single


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_spaces() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """   > block quote"""
    expected_tokens = [
        "[block-quote(1,4):   :   > ]",
        "[para(1,6):]",
        "[text(1,6):block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<p>block quote</p>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_spaces_double() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """ >  > block quote"""
    expected_tokens = [
        "[block-quote(1,2): : > ]",
        "[block-quote(1,5):: >  > ]",
        "[para(1,7):]",
        "[text(1,7):block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<p>block quote</p>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """\t> block quote"""
    expected_tokens = [
        "[icode-block(1,5):\t:]",
        "[text(1,5):\a>\a&gt;\a block quote:]",
        "[end-icode-block:::True]",
    ]
    expected_gfm = """<pre><code>&gt; block quote
</code></pre>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_double_x() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """
    # also need to test remove_blead scenarios

    # Arrange
    source_markdown = """> \t> block quote"""
    expected_tokens = [
        "[block-quote(1,1)::> ]",
        '[block-quote(1,5)::>   > :{0: "> \\t> "}]',
        "[para(1,7):]",
        "[text(1,7):block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<p>block quote</p>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_double_split() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """
    # also need to test remove_blead scenarios

    # Arrange
    source_markdown = """>\t> block quote"""
    expected_tokens = [
        "[block-quote(1,1)::>]",
        '[block-quote(1,5)::>   > :{0: ">\\t> "}]',
        "[para(1,7):]",
        "[text(1,7):block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<p>block quote</p>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_triple_space_space_space_x() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """>   >   > block quote"""
    expected_tokens = [
        "[block-quote(1,1)::> ]",
        "[block-quote(1,5)::>   > ]",
        "[block-quote(1,9)::>   >   > ]",
        "[para(1,11):]",
        "[text(1,11):block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<blockquote>
<p>block quote</p>
</blockquote>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_triple_space_space_space_double() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """>   >   > block quote
 >   >   > block quote"""
    expected_tokens = [
        "[block-quote(1,1)::> ]",
        "[block-quote(1,5)::>   > ]",
        "[block-quote(1,9)::>   >   > \n >   >   > ]",
        "[para(1,11):\n]",
        "[text(1,11):block quote\nblock quote::\n]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<blockquote>
<p>block quote
block quote</p>
</blockquote>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_triple_space_space_tab_x() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """>   > \t> block quote"""
    expected_tokens = [
        "[block-quote(1,1)::> ]",
        "[block-quote(1,5)::>   > ]",
        '[block-quote(1,9)::>   >   > :{0: ">   > \\t> "}]',
        "[para(1,11):]",
        "[text(1,11):block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<blockquote>
<p>block quote</p>
</blockquote>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_triple_space_space_tab_split_x() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """>   >\t> block quote"""
    expected_tokens = [
        "[block-quote(1,1)::> ]",
        "[block-quote(1,5)::>   >]",
        '[block-quote(1,9)::>   >   > :{0: ">   >\\t> "}]',
        "[para(1,11):]",
        "[text(1,11):block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<blockquote>
<p>block quote</p>
</blockquote>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_triple_space_space_tab_double() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """>   > \t> block quote
 >   > \t> block quote"""
    expected_tokens = [
        "[block-quote(1,1)::> ]",
        "[block-quote(1,5)::>   > ]",
        '[block-quote(1,9)::>   >   > \n >   >  > :{0: ">   > \\t> ", 1: " >   > \\t> "}]',
        "[para(1,11):\n]",
        "[text(1,11):block quote\nblock quote::\n]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<blockquote>
<p>block quote
block quote</p>
</blockquote>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_triple_space_space_tab_split_double() -> (
    None
):
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """>   > \t> block quote
 >   > \t> block quote"""
    expected_tokens = [
        "[block-quote(1,1)::> ]",
        "[block-quote(1,5)::>   > ]",
        '[block-quote(1,9)::>   >   > \n >   >  > :{0: ">   > \\t> ", 1: " >   > \\t> "}]',
        "[para(1,11):\n]",
        "[text(1,11):block quote\nblock quote::\n]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<blockquote>
<p>block quote
block quote</p>
</blockquote>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_triple_space_tab_space_x() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """> \t>  > block quote"""
    expected_tokens = [
        "[block-quote(1,1)::> ]",
        '[block-quote(1,5)::>   > :{0: "> \\t> "}]',
        '[block-quote(1,8)::>   >  > :{0: "> \\t>  > "}]',
        "[para(1,10):]",
        "[text(1,10):block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<blockquote>
<p>block quote</p>
</blockquote>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_triple_space_tab_split_space_x() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """>\t>  > block quote"""
    expected_tokens = [
        "[block-quote(1,1)::>]",
        '[block-quote(1,5)::>   > :{0: ">\\t> "}]',
        '[block-quote(1,8)::>   >  > :{0: ">\\t>  > "}]',
        "[para(1,10):]",
        "[text(1,10):block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<blockquote>
<p>block quote</p>
</blockquote>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_triple_space_tab_space_double() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """> \t>  > block quote
> \t>  > block quote"""
    expected_tokens = [
        "[block-quote(1,1)::> ]",
        '[block-quote(1,5)::>   > :{0: "> \\t> "}]',
        '[block-quote(1,8)::>   >  > \n>   >  > :{0: "> \\t>  > ", 1: "> \\t>  > "}]',
        "[para(1,10):\n]",
        "[text(1,10):block quote\nblock quote::\n]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<blockquote>
<p>block quote
block quote</p>
</blockquote>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_triple_space_tab_split_space_double() -> (
    None
):
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """>\t>  > block quote
>\t>  > block quote"""
    expected_tokens = [
        "[block-quote(1,1)::>]",
        '[block-quote(1,5)::>   > :{0: ">\\t> "}]',
        '[block-quote(1,8)::>   >  > \n>   >  > :{0: ">\\t>  > ", 1: ">\\t>  > "}]',
        "[para(1,10):\n]",
        "[text(1,10):block quote\nblock quote::\n]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<blockquote>
<p>block quote
block quote</p>
</blockquote>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_triple_space_tab_tab_x() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """ > \t> \t> block quote"""
    expected_tokens = [
        "[block-quote(1,2): : > ]",
        '[block-quote(1,5):: >  > :{0: " > \\t> "}]',
        '[block-quote(1,9):: >  >   > :{0: " > \\t> \\t> "}]',
        "[para(1,11):]",
        "[text(1,11):block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<blockquote>
<p>block quote</p>
</blockquote>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_triple_space_tab_split_tab_split_x() -> (
    None
):
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """ > \t> \t> block quote"""
    expected_tokens = [
        "[block-quote(1,2): : > ]",
        '[block-quote(1,5):: >  > :{0: " > \\t> "}]',
        '[block-quote(1,9):: >  >   > :{0: " > \\t> \\t> "}]',
        "[para(1,11):]",
        "[text(1,11):block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<blockquote>
<p>block quote</p>
</blockquote>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_triple_space_tab_tab_double() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """> \t> \t> block quote
> \t> \t> block quote"""
    expected_tokens = [
        "[block-quote(1,1)::> ]",
        '[block-quote(1,5)::>   > :{0: "> \\t> "}]',
        '[block-quote(1,9)::>   >   > \n>   >   > :{0: "> \\t> \\t> ", 1: "> \\t> \\t> "}]',
        "[para(1,11):\n]",
        "[text(1,11):block quote\nblock quote::\n]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<blockquote>
<p>block quote
block quote</p>
</blockquote>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_triple_space_tab_split_tab_split_double_x() -> (
    None
):
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """>\t>\t> block quote
>\t>\t> block quote"""
    expected_tokens = [
        "[block-quote(1,1)::>]",
        "[block-quote(1,5)::>   > ]",
        '[block-quote(1,9)::>   >   > \n>   >   > :{0: ">\\t>\\t> ", 1: ">\\t>\\t> "}]',
        "[para(1,11):\n]",
        "[text(1,11):block quote\nblock quote::\n]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<blockquote>
<p>block quote
block quote</p>
</blockquote>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_triple_space_tab_split_tab_split_double_with_prefix() -> (
    None
):
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """This is just some text.
 
>\t>\t> block quote
>\t>\t> block quote"""
    expected_tokens = [
        "[para(1,1):]",
        "[text(1,1):This is just some text.:]",
        "[end-para:::True]",
        "[BLANK(2,1): ]",
        "[block-quote(3,1)::>]",
        "[block-quote(3,5)::>   > ]",
        '[block-quote(3,9)::>   >   > \n>   >   > :{0: ">\\t>\\t> ", 1: ">\\t>\\t> "}]',
        "[para(3,11):\n]",
        "[text(3,11):block quote\nblock quote::\n]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<p>This is just some text.</p>
<blockquote>
<blockquote>
<blockquote>
<p>block quote
block quote</p>
</blockquote>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_double_with_extra_space() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """>\t>  block quote"""
    expected_tokens = [
        "[block-quote(1,1)::>]",
        '[block-quote(1,5)::>   > :{0: ">\\t> "}]',
        "[para(1,8): ]",
        "[text(1,8):block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<p>block quote</p>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_split_double_with_extra_space() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """ >\t>  block quote"""
    expected_tokens = [
        "[block-quote(1,2): : >]",
        '[block-quote(1,5):: >  > :{0: " >\\t> "}]',
        "[para(1,8): ]",
        "[text(1,8):block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<p>block quote</p>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_double_with_minus_space() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """ > \t>block quote"""
    expected_tokens = [
        "[block-quote(1,2): : > ]",
        '[block-quote(1,5):: >  >:{0: " > \\t>"}]',
        "[para(1,6):]",
        "[text(1,6):block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<p>block quote</p>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_split_double_with_minus_space() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """ >\t>block quote"""
    expected_tokens = [
        "[block-quote(1,2): : >]",
        '[block-quote(1,5):: >  >:{0: " >\\t>"}]',
        "[para(1,6):]",
        "[text(1,6):block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<blockquote>
<p>block quote</p>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_formfeeds() -> None:
    """
    Test case:  Block quotes preceeded by spaces.
    """

    # Arrange
    source_markdown = """\u000C> block quote"""
    expected_tokens = [
        "[para(1,1):\u000C]",
        "[text(1,1):\a>\a&gt;\a block quote:]",
        "[end-para:::True]",
    ]
    expected_gfm = """<p>&gt; block quote</p>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_xtabs() -> None:
    """
    Test case:  Block quotes preceeded by spaces and tabs.
    """

    # Arrange
    source_markdown = """ > block quote
 >\t> another block quote"""
    expected_tokens = [
        "[block-quote(1,2): : > \n >]",
        "[para(1,4):]",
        "[text(1,4):block quote:]",
        "[end-para:::True]",
        '[block-quote(2,5):: >  > :{0: " >\\t> "}]',
        "[para(2,7):]",
        "[text(2,7):another block quote:]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<p>block quote</p>
<blockquote>
<p>another block quote</p>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_tabs_x2() -> None:
    """
    Test case:  Block quotes preceeded by spaces and tabs.
    """

    # Arrange
    source_markdown = """ > block quote
 >\t> another block quote
 >\t> same block quote"""
    expected_tokens = [
        "[block-quote(1,2): : > \n >]",
        "[para(1,4):]",
        "[text(1,4):block quote:]",
        "[end-para:::True]",
        '[block-quote(2,5):: >  > \n >  > :{0: " >\\t> ", 1: " >\\t> "}]',
        "[para(2,7):\n]",
        "[text(2,7):another block quote\nsame block quote::\n]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<p>block quote</p>
<blockquote>
<p>another block quote
same block quote</p>
</blockquote>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_block_quotes_with_form_feeds_x() -> None:
    """
    Test case:  Block quotes preceeded by spaces and form feeds (ascii whitespace).
    """

    # Arrange
    source_markdown = """ > block quote
 >\u000C> another block quote"""
    expected_tokens = [
        "[block-quote(1,2): : > \n >]",
        "[para(1,4):\n]",
        "[text(1,4):block quote\n\u000C\a>\a&gt;\a another block quote::\n]",
        "[end-para:::True]",
        "[end-block-quote:::True]",
    ]
    expected_gfm = """<blockquote>
<p>block quote
\u000C&gt; another block quote</p>
</blockquote>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_ordered_lists_with_spaces() -> None:
    """
    Test case:  Ordered lists preceeded by spaces.
    """

    # Arrange
    source_markdown = """   1. list item"""
    expected_tokens = [
        "[olist(1,4):.:1:6:   ]",
        "[para(1,7):]",
        "[text(1,7):list item:]",
        "[end-para:::True]",
        "[end-olist:::True]",
    ]
    expected_gfm = """<ol>
<li>list item</li>
</ol>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_ordered_lists_with_tabs_x() -> None:
    """
    Test case:  Ordered lists preceeded by spaces and tabs.
    """

    # Arrange
    source_markdown = """1. list item
\t1. inner list item"""
    expected_tokens = [
        "[olist(1,1):.:1:3:]",
        "[para(1,4):]",
        "[text(1,4):list item:]",
        "[end-para:::True]",
        "[olist(2,5):.:1:7:    ::\t]",
        "[para(2,8):]",
        "[text(2,8):inner list item:]",
        "[end-para:::True]",
        "[end-olist:::True]",
        "[end-olist:::True]",
    ]
    expected_gfm = """<ol>
<li>list item
<ol>
<li>inner list item</li>
</ol>
</li>
</ol>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_ordered_lists_with_space_and_tabs() -> None:
    """
    Test case:  Ordered lists preceeded by spaces and tabs.
    """

    # Arrange
    source_markdown = """1. list item
 \t1. inner list item"""
    expected_tokens = [
        "[olist(1,1):.:1:3:]",
        "[para(1,4):]",
        "[text(1,4):list item:]",
        "[end-para:::True]",
        "[olist(2,5):.:1:7:    :: \t]",
        "[para(2,8):]",
        "[text(2,8):inner list item:]",
        "[end-para:::True]",
        "[end-olist:::True]",
        "[end-olist:::True]",
    ]
    expected_gfm = """<ol>
<li>list item
<ol>
<li>inner list item</li>
</ol>
</li>
</ol>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_ordered_lists_with_spaces_and_tabs() -> None:
    """
    Test case:  Ordered lists preceeded by spaces and tabs.
    """

    # Arrange
    source_markdown = """1. list item
  \t1. inner list item"""
    expected_tokens = [
        "[olist(1,1):.:1:3:]",
        "[para(1,4):]",
        "[text(1,4):list item:]",
        "[end-para:::True]",
        "[olist(2,5):.:1:7:    ::  \t]",
        "[para(2,8):]",
        "[text(2,8):inner list item:]",
        "[end-para:::True]",
        "[end-olist:::True]",
        "[end-olist:::True]",
    ]
    expected_gfm = """<ol>
<li>list item
<ol>
<li>inner list item</li>
</ol>
</li>
</ol>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_ordered_lists_with_spaces_for_indent_and_tab_after() -> None:
    """
    Test case:  Unordered lists preceeded by spaces and tabs.
    """

    # Arrange
    source_markdown = """1. list item
    1.\tinner list item"""
    expected_tokens = [
        "[olist(1,1):.:1:3:]",
        "[para(1,4):]",
        "[text(1,4):list item:]",
        "[end-para:::True]",
        "[olist(2,5):.:1:8:    :::1]",
        "[para(2,9):]",
        "[text(2,9):inner list item:]",
        "[end-para:::True]",
        "[end-olist:::True]",
        "[end-olist:::True]",
    ]
    expected_gfm = """<ol>
<li>list item
<ol>
<li>inner list item</li>
</ol>
</li>
</ol>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_ordered_lists_with_spaces_for_indent_and_tab_after_with_space_and_paragraph() -> (
    None
):
    """
    Test case:  Unordered lists preceeded by spaces and tabs.
    """

    # Arrange
    source_markdown = """1. list item
    1.\t inner list item"""
    expected_tokens = [
        "[olist(1,1):.:1:3:]",
        "[para(1,4):]",
        "[text(1,4):list item:]",
        "[end-para:::True]",
        "[olist(2,5):.:1:9:    :::1]",
        "[para(2,10):]",
        "[text(2,10):inner list item:]",
        "[end-para:::True]",
        "[end-olist:::True]",
        "[end-olist:::True]",
    ]
    expected_gfm = """<ol>
<li>list item
<ol>
<li>inner list item</li>
</ol>
</li>
</ol>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_ordered_lists_with_form_feeds() -> None:
    """
    Test case:  Ordered lists preceeded by spaces and form feeds (ascii whitespace).
    """

    # Arrange
    source_markdown = """1. list item
 \u000C1. inner list item"""
    expected_tokens = [
        "[olist(1,1):.:1:3::]",
        "[para(1,4):\n ]",
        "[text(1,4):list item\n\u000C1. inner list item::\n]",
        "[end-para:::True]",
        "[end-olist:::True]",
    ]
    expected_gfm = """<ol>
<li>list item
\u000C1. inner list item</li>
</ol>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_unordered_lists_with_spaces() -> None:
    """
    Test case:  Unordered lists preceeded by spaces.
    """

    # Arrange
    source_markdown = """   + list item"""
    expected_tokens = [
        "[ulist(1,4):+::5:   ]",
        "[para(1,6):]",
        "[text(1,6):list item:]",
        "[end-para:::True]",
        "[end-ulist:::True]",
    ]
    expected_gfm = """<ul>
<li>list item</li>
</ul>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_unordered_lists_with_tabs_x() -> None:
    """
    Test case:  Unordered lists preceeded by spaces and tabs.
    """

    # Arrange
    source_markdown = """+ list item
\t+ inner list item"""
    expected_tokens = [
        "[ulist(1,1):+::2:]",
        "[para(1,3):]",
        "[text(1,3):list item:]",
        "[end-para:::True]",
        "[ulist(2,5):+::6:    ::\t]",
        "[para(2,7):]",
        "[text(2,7):inner list item:]",
        "[end-para:::True]",
        "[end-ulist:::True]",
        "[end-ulist:::True]",
    ]
    expected_gfm = """<ul>
<li>list item
<ul>
<li>inner list item</li>
</ul>
</li>
</ul>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_unordered_lists_with_space_and_tabs() -> None:
    """
    Test case:  Unordered lists preceeded by spaces and tabs.
    """

    # Arrange
    source_markdown = """+ list item
 \t+ inner list item"""
    expected_tokens = [
        "[ulist(1,1):+::2:]",
        "[para(1,3):]",
        "[text(1,3):list item:]",
        "[end-para:::True]",
        "[ulist(2,5):+::6:    :: \t]",
        "[para(2,7):]",
        "[text(2,7):inner list item:]",
        "[end-para:::True]",
        "[end-ulist:::True]",
        "[end-ulist:::True]",
    ]
    expected_gfm = """<ul>
<li>list item
<ul>
<li>inner list item</li>
</ul>
</li>
</ul>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_unordered_lists_with_spaces_and_tabs() -> None:
    """
    Test case:  Unordered lists preceeded by spaces and tabs.
    """

    # Arrange
    source_markdown = """+ list item
  \t+ inner list item"""
    expected_tokens = [
        "[ulist(1,1):+::2:]",
        "[para(1,3):]",
        "[text(1,3):list item:]",
        "[end-para:::True]",
        "[ulist(2,5):+::6:    ::  \t]",
        "[para(2,7):]",
        "[text(2,7):inner list item:]",
        "[end-para:::True]",
        "[end-ulist:::True]",
        "[end-ulist:::True]",
    ]
    expected_gfm = """<ul>
<li>list item
<ul>
<li>inner list item</li>
</ul>
</li>
</ul>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_unordered_lists_with_spaces_for_indent_and_tab_after() -> None:
    """
    Test case:  Unordered lists preceeded by spaces and tabs.
    """

    # Arrange
    source_markdown = """+ list item
  +\tinner list item"""
    expected_tokens = [
        "[ulist(1,1):+::2:]",
        "[para(1,3):]",
        "[text(1,3):list item:]",
        "[end-para:::True]",
        "[ulist(2,3):+::4:  :::0]",
        "[para(2,5):]",
        "[text(2,5):inner list item:]",
        "[end-para:::True]",
        "[end-ulist:::True]",
        "[end-ulist:::True]",
    ]
    expected_gfm = """<ul>
<li>list item
<ul>
<li>inner list item</li>
</ul>
</li>
</ul>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_unordered_lists_with_spaces_for_indent_and_tab_after_with_space_and_paragraph() -> (
    None
):
    """
    Test case:  Unordered lists preceeded by spaces and tabs.
    """

    # Arrange
    source_markdown = """+ list item
  +\t inner list item"""
    expected_tokens = [
        "[ulist(1,1):+::2:]",
        "[para(1,3):]",
        "[text(1,3):list item:]",
        "[end-para:::True]",
        "[ulist(2,3):+::5:  :::0]",
        "[para(2,6):]",
        "[text(2,6):inner list item:]",
        "[end-para:::True]",
        "[end-ulist:::True]",
        "[end-ulist:::True]",
    ]
    expected_gfm = """<ul>
<li>list item
<ul>
<li>inner list item</li>
</ul>
</li>
</ul>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)


@pytest.mark.gfm
def test_whitespaces_unordered_lists_with_form_feeds() -> None:
    """
    Test case:  Unordered lists preceeded by spaces and form feeds (ascii whitespace).
    """

    # Arrange
    source_markdown = """+ list item
 \u000C + inner list item"""
    expected_tokens = [
        "[ulist(1,1):+::2::]",
        "[para(1,3):\n ]",
        "[text(1,3):list item\n\u000C + inner list item::\n]",
        "[end-para:::True]",
        "[end-ulist:::True]",
    ]
    expected_gfm = """<ul>
<li>list item
\u000C + inner list item</li>
</ul>"""

    # Act & Assert
    act_and_assert(source_markdown, expected_gfm, expected_tokens)
