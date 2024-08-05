import pytest

from madr.schemas import sanitize_name

cases = [
    ('Machado de Assis', 'machado de assis'),
    ('Manuel        Bandeira', 'manuel bandeira'),
    ('Edgar Alan Poe         ', 'edgar alan poe'),
    (
        'Androides Sonham Com Ovelhas Elétricas?',
        'androides sonham com ovelhas elétricas',
    ),
    ('  breve  história  do tempo ', 'breve história do tempo'),
    ('O mundo assombrado pelos demônios', 'o mundo assombrado pelos demônios'),
]


@pytest.mark.parametrize(('value', 'expected'), cases)
def test_sanitize_name_should_return_sanitazed_name(value, expected):
    result = sanitize_name(value)

    assert result == expected
