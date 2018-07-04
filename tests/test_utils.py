import re
import pytest
import trafaret as t

from trafaret_schema.utils import (
    Pattern,
    all_strings_unique,
)


RE_TYPE = type(re.compile('__stub__'))


def test_pattern():
    pt = Pattern()
    assert pt('ab+') == 'ab+'

    with pytest.raises(t.DataError):
        pt('(ab')


def test_all_strings_uniq():
    assert all_strings_unique(['a', 'b']) == ['a', 'b']

    with pytest.raises(t.DataError):
        all_strings_unique(['a', 'a', 'a'])
