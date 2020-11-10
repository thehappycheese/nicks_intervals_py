import itertools
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
	from NicksIntervals.iInterval import iInterval
	from NicksIntervals.iMulti_iInterval import iMulti_iInterval


def subtract(a: Iterable[iInterval], b: Iterable[iInterval]) -> Iterable[iInterval]:
	result: Iterable[iInterval] = a
	for interval_b in b:
		# List constructor is called here to cause immediate evaluation of the generator.
		# Otherwise the reassignment to 'result' may trigger weird issues with closures on the next iteration of the for loop
		# This makes the execution eager, but we cant have our entire software consist of a giant lazy nested generator like in haskell I suppose.
		result = list(itertools.chain.from_iterable(subtract_atomic(interval_a, interval_b) for interval_a in result))
	# conversion to tuple is  unnecessary but promotes immutable patterns in usercode
	return tuple(result)


def subtract_atomic_iterable(a: iInterval, b: Iterable[iInterval]):
	raise Exception("dead code?")
	result = [a]
	for interval_b in b:
		# List constructor is called here to cause immediate evaluation of the generator.
		# Otherwise the reassignment to 'result' may trigger weird issues with closures on the next iteration of the for loop
		# This makes the execution eager, but we cant have our entire software consist of a giant lazy nested generator like in haskell I suppose.
		result = list(
			itertools.chain.from_iterable(
				subtract_atomic(result_sub_interval, interval_b) for result_sub_interval in result
			)
		)
	return tuple(result)  # conversion to tuple is  unnecessary but promotes immutable patterns in usercode


def subtract_atomic(a: iInterval, b: iInterval) -> Iterable[iInterval]:

	other_contains_self_lower_bound = b.contains_lower_bound(a.lower_bound)
	other_contains_self_upper_bound = b.contains_upper_bound(a.upper_bound)
	
	#   self:        ╠════╣
	#  other:  ╠════════════╣
	# result:
	if other_contains_self_lower_bound and other_contains_self_upper_bound:
		return tuple()
	
	self_contains_other_lower_bound = a.contains_lower_bound(b.lower_bound)
	self_contains_other_upper_bound = a.contains_upper_bound(b.upper_bound)
	
	#   self:  ╠════════════╣
	#  other:        ╠════╣
	# result:  ╠═════╡    ╞═╣
	if self_contains_other_lower_bound and self_contains_other_upper_bound:
		interim_result = []
		if a.lower_bound != b.lower_bound:
			interim_result.append(iInterval(a.lower_bound, b.lower_bound))
		if b.upper_bound != a.upper_bound:
			interim_result.append(iInterval(b.upper_bound, a.upper_bound))
		return tuple(interim_result)
	
	#   self:        ╠══════════╣
	#  other:  ╠════════════╣
	# result:               ╞═══╣
	if other_contains_self_lower_bound:
		if b.upper_bound != a.upper_bound:
			return tuple(iInterval(b.upper_bound, a.upper_bound))
	
	#   self:        ╠════╣
	#  other:  ╠════════════╣
	# result:
	# if other_contains_self_lower_bound and other_contains_self_upper_bound:
	# 	pass
	#   continue
	
	#   self:    ╠══════════╣
	#  other:        ╠════════════╣
	# result:    ╠═══╡
	if other_contains_self_upper_bound:
		if a.lower_bound != b.lower_bound:
			return tuple(iInterval(a.lower_bound, b.lower_bound))
	
	# if execution makes it past all above continues, the only remaining possibility is that the intervals are disjoint
	# in this case the entire self interval is output
	
	return tuple(a)


def intersects_atomic(a: iInterval, b: iInterval) -> bool:
	return (a.contains_lower_bound(b.lower_bound) or
			a.contains_upper_bound(b.upper_bound) or
			b.contains_lower_bound(a.lower_bound) or
			b.contains_upper_bound(a.upper_bound))