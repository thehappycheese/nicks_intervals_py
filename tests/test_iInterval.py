import os
import sys

import pytest

from Interval.iBound import iBound
from Interval.iInterval import iInterval


def test_iInterval_init_argtype():
	with pytest.raises(TypeError):
		iInterval(1, 'a')
	with pytest.raises(TypeError):
		iInterval(1, 2, 'a')
	with pytest.raises(TypeError):
		iInterval(1, 2, False, 'a')
	with pytest.raises(Exception):
		iInterval(iBound(0, False), 1, False)


def test_iInterval_init_reversed_not_permitted():
	# reversed intervals are not permitted
	with pytest.raises(Exception):
		iInterval(2, 1)
	
	
def test_iInterval_init_degenerate_must_be_closed():
	# degenerate intervals may not have any open bounds
	with pytest.raises(Exception):
		iInterval(1, 1, False, True)
	with pytest.raises(Exception):
		iInterval(1, 1, True, False)
	with pytest.raises(Exception):
		iInterval(1, 1, False, False)
	iInterval(1, 1, True, True)


def test_iInterval_init_infinitesimal():
	assert iInterval(1, 1.0000000001).is_infinitesimal

