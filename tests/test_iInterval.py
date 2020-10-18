import os
import sys

import pytest

from NicksIntervals.iBound import iBound
from NicksIntervals.iInterval import iInterval


def test_iInterval_init_argtype():
	with pytest.raises(TypeError):
		iInterval(1, 'a')
	with pytest.raises(TypeError):
		iInterval(1, 'a')
	with pytest.raises(TypeError):
		iInterval(1.0, 2)
	
	iInterval(iBound(0, False), iBound(1, True))


def test_iInterval_init_reversed_not_permitted():
	# reversed intervals are not permitted
	with pytest.raises(Exception):
		iInterval(2, 1)
	
	
def test_iInterval_init_degenerate_must_be_closed():
	# degenerate intervals may not have any open bounds
	with pytest.raises(Exception):
		iInterval(iBound(0, True), iBound(0, True))
	with pytest.raises(Exception):
		iInterval(iBound(0, True), iBound(0, False))
	with pytest.raises(Exception):
		iInterval(iBound(0, False), iBound(0, False))
	iInterval(iBound(0, False), iBound(0, True))


def test_iInterval_init_infinitesimal():
	with pytest.raises(Exception):
		assert iInterval.closed(1, 1.000000000000000001).is_infinitesimal

