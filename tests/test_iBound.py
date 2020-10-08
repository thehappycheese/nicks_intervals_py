import pytest
import sys, os
sys.path.insert(len(sys.path), os.path.join(os.getcwd()))

from iInterval import iInterval, iBound

def test_iInterval_initialisers_type():
	with pytest.raises(TypeError):
		iInterval(1,'a')