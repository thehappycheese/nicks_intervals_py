"""
Nicholas Archer
2020-10-08

Roads are made of segments, and I nearly exploded with frustration writing code to work with overlapping or touching intervals.
Also I am using this to process midi files.
"""

from __future__ import annotations

import itertools
import math
from typing import Any, Collection, TYPE_CHECKING, Iterable, TypeVar, Generic

from .Bound import PART_OF_LEFT, Linked_Bound
from .Bound import PART_OF_RIGHT
from .Bound import Bound
from .Bound import iBound_Negative_Infinity
from .Bound import iBound_Positive_Infinity

from . import _operators as ops
if TYPE_CHECKING:
	from .Multi_Interval import Multi_Interval

T = TypeVar("T")


class Interval:
	"""Immutable Interval based on python's built in floats. Nothing fancy."""
	
	@classmethod
	def complete(cls):
		"""returns an interval spanning the complete real number line. Or at least all representable python floats."""
		return Interval(lower_bound=iBound_Negative_Infinity, upper_bound=iBound_Positive_Infinity)
	
	@classmethod
	def inf(cls):
		"""Alias of .complete()"""
		return Interval(iBound_Negative_Infinity, iBound_Positive_Infinity)

	@classmethod
	def degenerate(cls, value: float = 0.0):
		"""returns a zero-length 'degenerate' interval"""
		return Interval(Bound(value, PART_OF_RIGHT), Bound(value, PART_OF_LEFT))
	
	@classmethod
	def closed(cls, lower_bound: float, upper_bound: float):
		return Interval(Bound(lower_bound, PART_OF_RIGHT), Bound(upper_bound, PART_OF_LEFT))
	
	@classmethod
	def open(cls, lower_bound: float, upper_bound: float):
		return Interval(Bound(lower_bound, PART_OF_LEFT), Bound(upper_bound, PART_OF_RIGHT))
	
	@classmethod
	def open_closed(cls, lower_bound: float, upper_bound: float):
		return Interval(Bound(lower_bound, PART_OF_LEFT), Bound(upper_bound, PART_OF_LEFT))
	
	@classmethod
	def closed_open(cls, lower_bound: float, upper_bound: float):
		return Interval(Bound(lower_bound, PART_OF_RIGHT), Bound(upper_bound, PART_OF_RIGHT))
	
	@classmethod
	def inf_open(cls, upper_bound: float):
		return Interval(iBound_Negative_Infinity, Bound(upper_bound, PART_OF_RIGHT))
	
	@classmethod
	def open_inf(cls, lower_bound: float):
		return Interval(Bound(lower_bound, PART_OF_LEFT), iBound_Positive_Infinity)
	
	@classmethod
	def closed_inf(cls, lower_bound: float):
		return Interval(Bound(lower_bound, PART_OF_RIGHT), iBound_Positive_Infinity)
	
	@classmethod
	def inf_closed(cls, upper_bound: float):
		return Interval(iBound_Negative_Infinity, Bound(upper_bound, PART_OF_LEFT))
	
	@classmethod
	def empty(cls):
		"""returns a null or non-interval which is still of the type Collection[iInterval] but will yield no items"""
		from .Multi_Interval import Multi_Interval
		return Multi_Interval([])
	
	@classmethod
	def coerce_collection_to_Interval_or_Multi_Interval(cls, collection: Collection[Interval]):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(collection)
	
	@classmethod
	def coerce_collection_to_Interval_or_None(cls, collection: Collection[Interval]):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(collection)
	
	def __init__(self, lower_bound: Bound, upper_bound: Bound):
		if not (isinstance(lower_bound, Bound) and isinstance(upper_bound, Bound)):
			raise TypeError("Bounds must be an instance of iBound")
		
		self.__lower_bound: Bound = lower_bound
		self.__upper_bound: Bound = upper_bound
		
		self._linked_objects = tuple()
		# TODO: consider returning iInterval.empty() instead of throwing exception.
		#  I am inclined to keep the exceptions as they (may?) prevent hard to track bugs elsewhere in the library
		if lower_bound.value == upper_bound.value:
			if not(self.__lower_bound.part_of_right and self.__upper_bound.part_of_left):
				raise Exception(f"Degenerate intervals (lower_bound==upper_bound) are only permitted when both bounds are closed.")
		elif math.isclose(lower_bound.value, upper_bound.value):
			raise Exception(f"Infinitesimal intervals are not cool: {lower_bound} <= {upper_bound} == {lower_bound<=upper_bound} they must be eliminated in user code to avoid weird bugs in this interval library. use math.isclose() to test if the bounds are close. then either discard them, or make the bounds exactly equal to each other. Note that Degenerate intervals (lower_bound==upper_bound) are only permitted when both bounds are closed.")
		elif lower_bound.value > upper_bound.value:
			raise Exception(f"reversed intervals are not permitted. lower_bound.value must be less than or equal to upper_bound.value: {lower_bound} <= {upper_bound} == {lower_bound.value<=upper_bound.value}")
		
	def __format__(self, format_spec:str):
		char_left = f"{format(float(self.__lower_bound.value), format_spec)}"
		char_right = f"{format(float(self.__upper_bound.value), format_spec)}"
		
		if self.__lower_bound == iBound_Negative_Infinity:
			char_left = "-∞"
		
		if self.__upper_bound == iBound_Positive_Infinity:
			char_right = "+∞"
		
		if self.__lower_bound.part_of_right:
			char_left = "≤"+char_left  # ≤ [
		else:
			char_left = "<" + char_left  # < (
		
		if self.__upper_bound.part_of_left:
			char_right = char_right+"≥"  # ≥ ]
		else:
			char_right = char_right+">"  # > )
		return f"{char_left}, {char_right}"
		
	def __repr__(self):
		return format(self, ".2f")
	
	def __iter__(self):
		return iter((self,))
	
	def __len__(self):
		return 1
	
	def __bool__(self):
		return True
	
	def __contains__(self, item:Any):
		raise Exception("not sure this is working as expected")
		return self == item
	
	def __eq__(self, other:Collection[Interval]):
		return ops.eq(self, other)
	
	def __hash__(self):
		return hash((self.__lower_bound.__hash__(), self.__upper_bound.__hash__()))
	
	def print(self):
		"""
		prints intervals and multi intervals like this for debugging (only works for integer intervals):
		╠═════╣
			╠═════╣    ╞═══╣
		"""
		lbv = round(self.__lower_bound.value) if math.isfinite(self.__lower_bound.value) else (-999 if self.__lower_bound.value == float('-inf') else 999)
		ubv = round(self.__upper_bound.value) if math.isfinite(self.__upper_bound.value) else (-999 if self.__upper_bound.value == float('-inf') else 999)
		out = f"{self:2.0f} :"
		for i in range(0, min(50, ubv) + 1):
			if i < lbv:
				out += " "
			elif lbv == i == ubv:
				out += "║"
			elif i == lbv:
				if self.__lower_bound.part_of_right:
					out += "╠"
				else:
					out += "╞"
			elif i == ubv:
				if self.__upper_bound.part_of_left:
					out += "╣"
				else:
					out += "╡"
			else:
				out += "═"
		print(out)
		return self
	
	@property
	def lower_bound(self) -> Bound:
		return self.__lower_bound
	
	@property
	def upper_bound(self) -> Bound:
		return self.__upper_bound
	
	def get_linked_bounds(self) -> Collection[Linked_Bound]:
		return ops.get_linked_bounds(self)
	
	@property
	def has_degenerate(self) -> bool:
		return ops.has_degenerate(self)
	
	@property
	def is_complete(self) -> bool:
		return ops.is_complete(self)
	
	@ property
	def length(self) -> float:
		return self.__upper_bound.value - self.__lower_bound.value
	
	def interpolate(self, ratio: float) -> float:
		return self.__lower_bound.value + (self.__upper_bound.value - self.__lower_bound.value) * ratio
	
	def contains_value(self, value: float) -> bool:
		return ops.contains_value(self, value)
	
	def contains_interval(self, other: Collection[Interval]) -> bool:
		return ops.contains_interval(self, other)
	
	def touches(self, other: Collection[Interval]) -> bool:
		return ops.touches(self, other)
	
	def intersects(self, other: Collection[Interval]) -> bool:
		return ops.intersects(self, other)
	
	def disjoint(self, other: Collection[Interval]) -> bool:
		return not ops.intersects(self, other)
	
	@property
	def exterior(self) -> Collection[Interval]:
		return ops.coerce_collection_to_Interval_or_Multi_Interval(ops.exterior(self))
	
	@property
	def interior(self) -> Collection[Interval]:
		return ops.coerce_collection_to_Interval_or_Multi_Interval(ops.interior(self))
	
	def intersect(self, other: Collection[Interval]):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(ops.intersect(self, other))
	
	def subtract(self, other: Collection[Interval]) -> Multi_Interval:
		return ops.coerce_collection_to_Interval_or_Multi_Interval(ops.subtract(self, other))
	
	def hull(self, other: Iterable[Interval] = tuple()):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(ops.hull(itertools.chain(self, other)))
	
	def union(self, other: Iterable[Interval]) -> Collection[Interval]:
		return ops.coerce_collection_to_Interval_or_Multi_Interval([*itertools.chain(self, other)])
	
	def scaled(self, scale_factor: float):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(ops.scaled(self, scale_factor))
	
	def translated(self, translation: float):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(ops.translated(self, translation))
	
	def scaled_then_translated(self, scale_factor: float, translation: float):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(ops.scaled_then_translated(self, scale_factor, translation))
	
	def translated_then_scaled(self, translation: float, scale_factor: float):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(ops.translated_then_scaled(self, translation, scale_factor))
	
	#####################
	# UNION OPERATIONS
	#####################
	# TODO: Union of two interval sets is hard to define.
	#  the default behaviour of all functions is to maintain the structure of the input multi-interval
	#  union may imply a flattening of self and other intervals, just the other intervals, just the self or neither.
	#  the default will be neither. But t avoid confusion, union will be named 'union_keeping_overlaps'
	def union_keeping_overlaps(self, other: Iterable[Interval]):
		return ops.coerce_collection_to_Interval_or_Multi_Interval([*self, *other])
	
	def union_merge_intersecting(self, other: Iterable[Interval]):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(ops.union_merge_intersecting(self, other))
	
	def union_merge_intersecting_or_touching(self, other: Iterable[Interval]):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(ops.union_merge_intersecting_or_touching(self, other))

	def union_merge_touching(self, other: Iterable[Interval]):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(ops.union_merge_touching(self, other))
	
	def merge_intersecting(self):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(ops.union_merge_intersecting([], self))
	
	def merge_intersecting_or_touching(self):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(ops.union_merge_intersecting_or_touching([], self))
	
	def merge_touching(self):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(ops.union_merge_touching([], self))
		
	def link_merge(self, linked_objects):
		return Linked_Interval(self, (*self._linked_objects, *linked_objects))
	
	def link_replace(self, linked_objects):
		return Linked_Interval(self, linked_objects)
	
	def link_remove(self, linked_objects):
		return Linked_Interval(self, (lo for lo in linked_objects if lo not in linked_objects))
	
	def unlink(self):
		return Interval(self.__lower_bound, self.__upper_bound)
	
	@property
	def linked_objects(self):
		return self._linked_objects


# TODO: consider building this into the base class
#  then changing all _operators to merge or split the content of the linked_objects array
#  then we can dispense with the linked objects array
class Linked_Interval(Interval, Generic[T]):
	def __init__(self, original_iInterval: Interval, linked_objects: Iterable[T]):
		super().__init__(original_iInterval.lower_bound, original_iInterval.upper_bound)
		self._linked_objects = tuple(linked_objects)