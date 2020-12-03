from NicksIntervals import _operators as ops
from NicksIntervals.Interval import Interval


class Interval_Map:
	
	def __init__(self, interval_in_dimension_a: Interval, interval_in_dimension_b: Interval):
		"""Links one interval with another interval: Used to form an Interval_Mapping."""
		# TODO: hold info about degenerate cases; if the from space is degenerate, then how will the to space behave?
		#  this is currently determined by the _operators.
		self.__interval_a = interval_in_dimension_a
		self.__interval_b = interval_in_dimension_b
		
	def __len__(self):
		return 2
	
	def __getitem__(self, item: int):
		if item == 0:
			return self.__interval_a
		elif item == 1:
			return self.__interval_b
		raise IndexError(f"{self.__class__.__qualname__} has only 2 index-able items, [0], and [1]. Negative indices are not supported")
	
	def __iter__(self):
		return iter((self.__interval_a, self.__interval_b))
	
	def __reversed__(self):
		return Interval_Map(self.__interval_b, self.__interval_a)
	
	def __contains__(self, item):
		return (item is self.__interval_a) or (item is self.__interval_b)
	
	def contains(self, interval_link: Interval_Map):
		return self.__interval_a.contains_interval(interval_link.__interval_a) and self.__interval_b.contains_interval(interval_link.__interval_b)
	
	def touches(self, interval_link: Interval_Map):
		return self.__interval_a.touches(interval_link.__interval_a) and self.__interval_b.touches(interval_link.__interval_b)
	
	def merge(self, interval_link: Interval_Map):
		a = ops.coerce_collection_to_Interval_or_None(self.__interval_a.hull(interval_link.__interval_a))
		b = ops.coerce_collection_to_Interval_or_None(self.__interval_b.hull(interval_link.__interval_b))
		if a and b:
			return Interval_Map(a, b)
		return None
	
	@property
	def from_dimension(self) -> Interval:
		return self.__interval_a
	
	@property
	def to_dimension(self) -> Interval:
		return self.__interval_b