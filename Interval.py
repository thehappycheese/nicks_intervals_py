 """
Nicholas Archer
2020/06/09

Roads are made of segments, and I nearly exploded with frustration writing code to work with overlapping or touching intervals.
"""

from __future__ import annotations

import itertools
import math
from typing import Iterable, Union, List, Any


class Interval:
	def __init__(self, start: Any, end: Any):
		"""To initialise self.start & self.end with a type other than float, make a subclass of Interval().
		This will give the best auto-completion and type ch  ecking results in pycharm.
		The subclass of interval only needs to provide a replacement for this __init__()

		Custom types used for self.start and self.end must:
		 - define __float__ AND
		 - define __lt__, __gt__, __le__, __ge__, __eq__, __ne__ AND
		 - these dunder methods must accept any argument type that has a __float__ method

		Optionally, the subclass must
			 - override @classmethod Interval.make_infinite_full(), and Interval.make_infinite_empty() otherwise a float('inf') value will be used
		"""
		self.start: Any = start
		self.end: Any = end
		
	@classmethod
	def make_infinite_full(cls) -> Interval:
		"""
		:return: full Interval, starting at negative infinity and ending at infinity
		"""
		# not using cls to construct; if cls using something SupportsFloat instead of float, there is no way for us to get the maximum and minimum value
		return Interval(-float('inf'), float('inf'))
	
	@classmethod
	def make_infinite_empty(cls) -> Interval:
		"""
		:return: empty Interval, starting at infinity and ending at negative infinity
		"""
		# not using cls to construct; if cls using something SupportsFloat instead of float, there is no way for us to get the maximum and minimum value
		return Interval(float('inf'), float('-inf'))

	def print(self):
		"""
		prints intervals and multi intervals like this for debugging (only works for integer intervals):
		  ├─────┤
			├──────┤    ├────┤
		"""
		out = f"{self.start: 5.0f} {self.end: 5.0f} :"
		for i in range(int(self.end) + 1):
			if i < self.start:
				out += " "
			elif self.start == i == self.end:
				out += "│"
			elif i == self.start:
				out += "├"
			elif i == self.end:
				out += "┤"
			else:
				out += "─"
		print(out)
		
	def __format__(self, format_spec):
		return f"{self.__class__.__name__}({format(self.start, format_spec)}, {format(self.end, format_spec)})"
	
	def __repr__(self):
		return self.__format__(".2f")
	
	def __getitem__(self, item):
		if item == 0:
			return self.start
		elif item == 1:
			return self.end
		else:
			raise IndexError(f"Interval has only index [0] and [1]. tried to access {item}")
	
	def copy(self):
		return type(self)(self.start, self.end)
	
	def interpolate(self, ratio: float) -> Any:
		return (self.end - self.start) * ratio + self.start
	
	@property
	def is_ordered(self) -> bool:
		"""
		:return: True, if interval start <= end, False otherwise
		"""
		return self.start <= self.end
	
	@property
	def is_infinitesimal(self) -> bool:
		"""
		:return: True, if interval start isclose to end, False otherwise
		"""
		return math.isclose(self.start, self.end)
	
	@property
	def length(self) -> Any:
		return self.end - self.start
	
	def point_is_within(self, point: Any) -> bool:
		return self.start < point < self.end
	
	def point_touches(self, point: Any) -> bool:
		return not self.point_is_within(point) and (math.isclose(self.start, point) or math.isclose(self.end, point))
	
	def get_ordered(self) -> Interval:
		return Interval(
			min(self.start, self.end),
			max(self.start, self.end)
		)
	
	def intersect(self, other: Union[Interval, Multi_Interval]) -> Union[Interval, Multi_Interval, None]:
		"""
		No floating point weirdness is accounted for. Will return zero-length and 'infinitesimal' intersections
		if a multi_interval is passed in, the structure of the original multi interval is preserved;
		 we will simply return a new multi_interval where every sub_interval is the result of intersecting the old sub_intervals with this interval
		:param other:
		:return:
		"""
		if isinstance(other, Multi_Interval):
			result = Multi_Interval([])
			for sub_interval in other.intervals:
				f = self.intersect(sub_interval)
				if f is not None:
					result.add_overlapping(f)
			if not result.intervals:
				return None
			else:
				return result
		elif isinstance(other, Interval):
	
			#  |---|
			#        |---|
			if self.end < other.start:  # less than but not equal; zero length intersection will pass over
				return None
			
			#        |---|
			#  |---|
			if self.start > other.end:  # greater than but not equal; zero length intersection will pass over
				return None
			
			if self.start <= other.start:  # accepts equality; in the case of zero length intersections both return statements below are equivalent
				#  |---|
				#    |---|
				if self.end < other.end:
					return type(self)(other.start, self.end)
				
				#  |-------|
				#    |---|
				return type(self)(other.start, other.end)
			
			if self.start <= other.end:
				#    |---|
				#  |-------|
				if self.end < other.end:
					return type(self)(self.start, self.end)
				
				#    |---|
				#  |---|
				return type(self)(self.start, other.end)
		else:
			raise Exception("Interval.intersect() has failed to find a valid branch. Has there been a type error?")
	
	def intersects(self, other: Interval) -> bool:
		if isinstance(other, Multi_Interval):
			result = Multi_Interval([])
			for sub_interval in other.intervals:
				if self.intersects(sub_interval):
					return True
			return False
		elif isinstance(other, Interval):
			
			#  |---|
			#        |---|
			if self.end < other.start:  # less than but not equal; zero length intersection will pass over
				return False
			
			#        |---|
			#  |---|
			if self.start > other.end:  # greater than but not equal; zero length intersection will pass over
				return False
			
			if self.start <= other.start:  # accepts equality; in the case of zero length intersections both return statements below are equivalent
				#  |---|
				#    |---|
				if self.end < other.end:
					return True
				
				#  |-------|
				#    |---|
				return True
			
			if self.start <= other.end:
				#    |---|
				#  |-------|
				if self.end < other.end:
					return True
				
				#    |---|
				#  |---|
				return True
		else:
			raise Exception("Interval.intersects() failed to find a valid branch. Has there been a type error?")
	
	def contains(self, other: Interval, allow_inside_touching: bool = False) -> bool:
		if isinstance(other, Multi_Interval):
			return self.contains(other.hull())
		elif isinstance(other, Interval):
			# self:     |---|
			# other:  |-------|
			if allow_inside_touching:
				return (other.end <= self.end or math.isclose(other.end, self.end)) and (other.start >= self.start or math.isclose(other.start, self.start))
			else:
				return other.end < self.end and other.start > self.start
		else:
			try:
				return self.end > float(other) > self.start
			except Exception as e:
				raise Exception("Interval.intersects() failed to find a valid branch. Has there been a type error?") from e
				
	def relate_DE_9IM(self, other: Interval):
		# 			Interior Boundary Exterior
		# Interior  T/F      T/F      T/F
		# Boundary  T/F      T/F      T/F
		# Exterior  T/F      T/F      T/F
		#
		# represented as [9]
		raise Exception("not implemented: very hard with floating points.")
		pass
		
	def union(self, other: Interval) -> Union[Interval, Multi_Interval]:
		if self.intersect(other) is not None:
			return self.hull(other)
		else:
			return Multi_Interval((self, other))
	
	def hull(self, other: Interval) -> Interval:
		return type(self)(min(self.start, other.start), max(self.end, other.end))
	
	def touches(self, other: Interval):
		"""
		:return: True if touching but not intersecting; ie self.start>=other.end and self.start isclose to other.end
		touches will return True if two adjacent intervals should be merged, but intersects() has returned False.
		"""
		if self.start >= other.end and math.isclose(self.start, other.end):
			return True
		if self.end <= other.start and math.isclose(self.end, other.start):
			return True
		return False
	
	def subtract(self, other: Union[Interval, Multi_Interval]) -> Union[Interval, Multi_Interval, None]:
		if isinstance(other, Multi_Interval):
			result = self.copy()
			for sub_interval in other.intervals:
				result = result.subtract(sub_interval)
			return result
		elif isinstance(other, Interval):
			
			#  |---|
			#        |---|
			if self.end <= other.start:
				return self.copy()
			
			#        |---|
			#  |---|
			if self.start >= other.end:
				return self.copy()
			
			if self.start <= other.start:
				#  |---|
				#    |---|
				if self.end < other.end:
					return type(self)(self.start, other.start)
				
				#  |-------|
				#    |---|
				return Multi_Interval((type(self)(self.start, other.start), type(self)(other.end, self.end)))
			
			if self.start < other.end:
				#    |---|
				#  |-------|
				if self.end < other.end:
					return None
				
				#    |---|
				#  |---|
				return type(self)(other.end, self.end)
			
			raise ValueError("Interval.subtract() had some kind of malfunction and did not find a result")
		else:
			raise NotImplementedError("Cannot subtract unknown type")
	

class Multi_Interval:

	def __init__(self, iter_intervals: Iterable[Interval]):
		""" Intervals provided to this initialiser are added without further processing.
		"""
		self.intervals: List[Interval] = []
		
		for interval in iter_intervals:
			self.intervals.append(interval)
	
	def __format__(self, format_spec):
		return f"Multi_Interval[{len(self.intervals)}]([{', '.join(['...'+str(len(self.intervals)) if index==4 else format(interval, format_spec) for index, interval in enumerate(self.intervals) if index<5])}])"
		
	def __repr__(self):
		return self.__format__(".2f")
		
	def print(self):
		print("Multi_Interval:")
		for sub_interval in self.intervals:
			sub_interval.print()
		print("")
	
	def __bool__(self):
		return bool(self.intervals)
	
	def copy(self) -> Multi_Interval:
		return type(self)([interval.copy() for interval in self.intervals]);
	
	@property
	def start(self):
		if self.intervals:
			min_so_far = self.intervals[0].start
			for item in self.intervals:
				min_so_far = min(min_so_far, item.start)
			return min_so_far
		else:
			return None
	
	@property
	def end(self):
		if self.intervals:
			max_so_far = self.intervals[0].end
			for item in self.intervals:
				max_so_far = max(max_so_far, item.end)
			return max_so_far
		else:
			return None
	
	@property
	def is_valid(self) -> Union[bool, None]:
		if self.intervals:
			for item in self.intervals:
				if not item.is_ordered:
					return False
			return True
		else:
			return None
	
	def subtract(self, interval_to_subtract: Interval):
		new_interval_list = []
		for interval in self.intervals:
			if interval.intersect(interval_to_subtract):
				f = interval.subtract(interval_to_subtract)
				if f is not None:
					try:
						# assume f is a Multi_Interval
						for pieces in f.__intervals:
							new_interval_list.append(pieces)
					except:
						# f is an Interval
						new_interval_list.append(f)
			else:
				new_interval_list.append(interval)
		self.intervals = new_interval_list
		return self
	
	def add_overlapping(self, interval: Union[Interval, Multi_Interval]) -> Multi_Interval:
		"""Add to multi interval without further processing. Overlapping intervals will be preserved.
		this is similar to doing: MultiInterval().intervals.append(Interval()) except it also works on Multi_Intervals
		:return: self
		"""
		if isinstance(interval, Interval):
			self.intervals.append(interval.copy())
		elif isinstance(interval, Multi_Interval):
			for sub_interval in interval.intervals:
				self.intervals.append(sub_interval.copy())
		else:
			raise ValueError()
		return self
	
	def add_hard(self, interval_to_add: Interval) -> Multi_Interval:
		"""Add to multi interval, truncating or deleting existing intervals to prevent overlaps with the new interval
		will result in touching intervals being maintained
		may result in infinitesimal interval being added
		:return: self
		"""
		# TODO: Make multi interval compatible
		self.subtract(interval_to_add)
		self.add_overlapping(interval_to_add)
		return self
	
	def add_soft(self, interval_to_add: Interval) -> Multi_Interval:
		"""Add Interval() to Multi_Interval(), truncating or ignoring the new interval to prevent overlaps with existing intervals
		will result in touching intervals being maintained
		may result in infinitesimal interval being added
		:return: self
		"""
		# TODO: Make multi interval compatible
		for interval in self.intervals:
			if interval.intersects(interval_to_add):
				interval_to_add = interval_to_add.subtract(interval)
				if interval_to_add is None:
					break
		
		if isinstance(interval_to_add, Multi_Interval):
			for sub_interval in interval_to_add.intervals:
				self.intervals.append(sub_interval.copy())
		elif isinstance(interval_to_add, Interval):
			self.add_overlapping(interval_to_add)
		elif interval_to_add is None:
			pass
		else:
			raise Exception("add soft failed")
		
		return self
		
	def add_merge(self, interval_to_add: Interval) -> Multi_Interval:
		"""Add Interval() to Multi_Interval(), merge with any overlapping or touching intervals to prevent overlaps
		preserves existing intervals that are touching, only merges existing intervals which touch or intersect with the new interval
		:return: self
		"""
		# TODO: Make multi interval compatible

		original_interval_to_add = interval_to_add
		
		must_restart = True
		while must_restart:
			must_restart = False
			for interval in self.intervals:
				if interval.intersects(original_interval_to_add) or interval.touches(original_interval_to_add):
					interval_to_add = interval_to_add.hull(interval)
					self.intervals.remove(interval)
					must_restart = True
					break
		self.intervals.append(interval_to_add)
		return self
	
	def intersection(self, arg_interval: Union[Interval, Multi_Interval]) -> Multi_Interval:
		if isinstance(arg_interval, Multi_Interval):
			result_multi_interval: Multi_Interval = type(self)([])
			for my_interval in self.intervals:
				for other_interval in arg_interval.intervals:
					result_multi_interval.add_soft(my_interval.intersect(other_interval))
			return result_multi_interval.delete_infinitesimal()
		elif isinstance(arg_interval, Interval):
			result_multi_interval: Multi_Interval = type(self)([])
			for my_interval in self.intervals:
				result_multi_interval.add_soft(my_interval.intersect(arg_interval))
			return result_multi_interval.delete_infinitesimal()
		else:
			raise Exception("Type error in MultiInterval().intersection()")
	
	def merge_touching_and_intersecting(self) -> Multi_Interval:
		"""
		:return: eliminates all touching or intersecting intervals by merging
		"""
		must_restart = True
		while must_restart:
			must_restart = False
			for a, b in itertools.combinations(self.intervals, 2):
				if a.intersects(b) or a.touches(b):
					c = a.hull(b)
					self.intervals.remove(a)
					self.intervals.remove(b)
					self.intervals.append(c)
					must_restart = True
					break
		return self
	
	def delete_infinitesimal(self) -> Multi_Interval:
		self.intervals = [item for item in self.intervals if not item.is_infinitesimal]
		return self
	
	def make_all_positive(self):
		self.intervals = [interval.get_ordered() for interval in self.intervals]
		return self
	
	def hull(self) -> Union[Interval, None]:
		if not self.intervals:
			return None
		else:
			result = None
			for sub_interval in self.intervals:
				if result is None:
					result = sub_interval.copy()
				else:
					result = result.hull(sub_interval)
			return result
