from collections.abc import Collection, Iterable, Sized, Container, Sequence

from NicksIntervals.iInterval import iInterval
from NicksIntervals.iMulti_iInterval import iMulti_iInterval


def test_iInterval_abstract_base_classes():
	assert issubclass(iInterval, Iterable) is True
	assert issubclass(iInterval, Sized) is True
	assert issubclass(iInterval, Container) is True
	assert issubclass(iInterval, Collection) is True
	assert issubclass(iInterval, Sequence) is False


def test_iMulti_iInterval_abstract_base_classes():
	assert issubclass(iMulti_iInterval, Iterable) is True
	assert issubclass(iMulti_iInterval, Sized) is True
	assert issubclass(iMulti_iInterval, Container) is True
	assert issubclass(iMulti_iInterval, Collection) is True
	assert issubclass(iMulti_iInterval, Sequence) is False