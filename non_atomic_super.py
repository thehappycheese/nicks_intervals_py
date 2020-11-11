from typing import Iterable
import NicksIntervals._operators as ops
import NicksIntervals.iBound


iBound = NicksIntervals.iBound.iBound

class non_atomic_super:
	def contains_value(self, value: float) -> bool:
		return ops.contains_value_atomic(self, value)
	
	def contains_upper_bound(self, bound: iBound) -> bool:
		return ops.contains_upper_bound_atomic(self, bound)
	
	def contains_lower_bound(self, bound: iBound) -> bool:
		return ops.contains_lower_bound_atomic(self, bound)
	
	def contains_interval(self, other: Iterable[iInterval]) -> bool:
		return ops.contains_interval(self, other)
	
	@property
	def exterior(self) -> Iterable[iInterval]:
		return NicksIntervals.iMulti_iInterval.iMulti_iInterval(ops.exterior_atomic(self))
	
	def touches(self, other: Iterable[iInterval]) -> bool:
		return ops.touches(self, other)
	
	def intersects(self, other: Iterable[iInterval]) -> bool:
		return ops.intersects(self, other)
	
	def disjoint(self, other: Iterable[iInterval]):
		return not ops.intersects(self, other)
	
	def intersect(self, other: Iterable[iInterval]) -> Iterable[iInterval]:
		return ops.intersect(self, other)
	
	def subtract(self, other: Iterable[iInterval]) -> NicksIntervals.iMulti_iInterval.iMulti_iInterval:
		return NicksIntervals.iMulti_iInterval.iMulti_iInterval(ops.subtract(self, other))
	
	def hull(self, other: Iterable[iInterval]) -> Iterable[iInterval]:
		return ops.hull(itertools.chain(self, other))
	
	def union(self, other: Iterable[iInterval]) -> Iterable[iInterval]:
		return NicksIntervals.iMulti_iInterval.iMulti_iInterval(itertools.chain(self, other))