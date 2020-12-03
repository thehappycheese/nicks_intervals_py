from collections.abc import Collection, Iterable, Sized, Container, Sequence

from NicksIntervals.Interval import Interval
from NicksIntervals.Multi_Interval import Multi_Interval


def test_iInterval_abstract_base_classes():
	assert issubclass(Interval, Iterable) is True
	assert issubclass(Interval, Sized) is True
	assert issubclass(Interval, Container) is True
	assert issubclass(Interval, Collection) is True
	assert issubclass(Interval, Sequence) is False


def test_iMulti_iInterval_abstract_base_classes():
	assert issubclass(Multi_Interval, Iterable) is True
	assert issubclass(Multi_Interval, Sized) is True
	assert issubclass(Multi_Interval, Container) is True
	assert issubclass(Multi_Interval, Collection) is True
	assert issubclass(Multi_Interval, Sequence) is False