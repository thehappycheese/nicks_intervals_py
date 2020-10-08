import os
import sys

import pytest

print(os.path.join(os.getcwd(), "..\\"))
sys.path.insert(len(sys.path), os.path.join(os.getcwd(), "..\\"))
if False:
	from interval.iInterval import iInterval
from iInterval import iInterval


def test_iInterval_init_argtype():
	with pytest.raises(TypeError):
		iInterval(1, 'a')
	with pytest.raises(TypeError):
		iInterval(1, 2, 'a')
	with pytest.raises(TypeError):
		iInterval(1, 2, False, 'a')


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
	assert iInterval(1, 1.00000000000001).is_infinitesimal

