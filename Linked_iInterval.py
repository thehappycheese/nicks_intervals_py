from typing import Any

from NicksIntervals.iInterval import iInterval


class Linked_iInterval(iInterval):
	def __init__(self, original_iInterval: iInterval, linked_object: Any):
		self.original_iInterval = original_iInterval
		self.linked_object = linked_object
		super().__init__(original_iInterval.lower_bound, original_iInterval.upper_bound)