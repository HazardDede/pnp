import pytest

from pnp.plugins.push import PushBase


class Foo(PushBase):
    def __init__(self):
        super().__init__(name='foo')
        self.a = 1
        self._b = 2
        self.__c = 3

    def _parse_b(self, value):
        return int(value)

    def __parse_c(self, value):
        raise ValueError()

    def custom_parser(self, value):
        return "__" + str(value) + "__"

    def test_from_envelope(self):
        assert self._parse_envelope_value('a', dict(a='a')) == 'a'  # a from envelope (None parser -> as is)

    def test_from_envelope_with_parser(self):
        assert self._parse_envelope_value('b', dict(b='99')) == 99  # b from envelope with parsing

    def test_from_envelope_with_custom_parser(self):
        assert self._parse_envelope_value('b', dict(b='99'), parse_fun=self.custom_parser) == '__99__'

    def test_from_envelope_with_errorneous_parser_fallback_to_instance(self):
        assert self._parse_envelope_value('c', dict(c='abc')) == 3

    def test_from_instance_with_instance_var(self):
        assert self._parse_envelope_value('a', dict(b=98, c=99)) == 1

    def test_from_instance_with_private_instance_var(self):
        assert self._parse_envelope_value('c', None) == 3

    def test_not_in_instance_not_in_envelope(self):
        assert self._parse_envelope_value('d', {}) is None  # Not existent either in envelope nor instance


@pytest.mark.parametrize("name,test_fun", [
    (name, getattr(Foo(), name))
    for name in dir(Foo())
    if name.startswith('test')
])
def test_parse_envelope(name, test_fun):
    test_fun()
