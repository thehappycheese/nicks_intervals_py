from ..iInterval import iBound


def test_iBound():
	a = iBound(0.2)
	assert(a == 0.2)