from __future__ import annotations

from typing import Union, Tuple, Iterator

from . import _operators as ops
from .Interval import Interval


class Interval_Map:
	
	@classmethod
	def closed_open(cls, a: float, b: float, x: float, y: float):
		return Interval_Map(
			Interval.closed_open(a, b) if a != b else Interval.degenerate(a),
			Interval.closed_open(x, y) if x != y else Interval.degenerate(x)
		)
	
	def __init__(self, interval_in_dimension_a: Interval, interval_in_dimension_b: Interval):
		"""Links one interval with another interval: Used to form an Interval_Mapping.
		Interval arguments must be atomic."""
		# TODO: this class is kind of like a multi_interval and could almost extend it;
		#  but we cant because in an IntervalMap sub-intervals are treated as being on separate dimensions rather than an un-ordered set.
		#  Therefore if we want to know if an Interval_Map is touching another Interval_Map, we would use all(sub-intervals-touching) rather than any(sub-intervals-touching)
		self.__interval_a = interval_in_dimension_a
		self.__interval_b = interval_in_dimension_b
	
	def __len__(self):
		return 2
	
	def __getitem__(self, item: int) -> Interval:
		if item == 0 or item == -2:
			return self.__interval_a
		elif item == 1 or item == -1:
			return self.__interval_b
		raise IndexError(f"{self.__class__.__qualname__} has only 2 index-able items, [0], and [1]. Negative indices are not supported")
	
	def __iter__(self) -> Iterator[Interval]:
		return iter((self.__interval_a, self.__interval_b))
	
	def __reversed__(self):
		return Interval_Map(self.__interval_b, self.__interval_a)
	
	def __contains__(self, item):
		return (item is self.__interval_a) or (item is self.__interval_b)
	
	def __format__(self, format_spec):
		return f"Map({format(self.from_interval, format_spec)} to {format(self.to_interval, format_spec)})"
	
	def __repr__(self):
		return format(self, ".2f")
	
	def contains(self, interval_link: Interval_Map):
		return ops.contains_interval_atomic(self.__interval_a, interval_link.__interval_a) and ops.contains_interval_atomic(self.__interval_b, interval_link.__interval_b)
	
	def touches(self, interval_link: Interval_Map):
		return ops.touches_atomic(self.__interval_a, interval_link.__interval_a) and ops.touches_atomic(self.__interval_b, interval_link.__interval_b)
	
	def intersects(self, interval_link: Interval_Map):
		return ops.intersects_atomic(self.__interval_a, interval_link.__interval_a) and ops.intersects_atomic(self.__interval_b, interval_link.__interval_b)
	
	def merge_by_hull(self, interval_link: Union[Interval_Map, Tuple[Interval, Interval]]):
		a_other, b_other = interval_link
		a = ops.coerce_collection_to_Interval_or_None(self.__interval_a.hull(a_other))
		b = ops.coerce_collection_to_Interval_or_None(self.__interval_b.hull(b_other))
		if a is not None and b is not None:
			return Interval_Map(a, b)
		return None
	
	@property
	def from_interval(self) -> Interval:
		return self.__interval_a
	
	@property
	def to_interval(self) -> Interval:
		return self.__interval_b
