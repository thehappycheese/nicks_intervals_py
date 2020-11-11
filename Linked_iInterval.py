from typing import Any

from NicksIntervals.iInterval import iInterval


class Linked_iInterval(iInterval):
	def __init__(self, interval: iInterval, linked_object: Any):
		super().__init__(
			interval.lower_bound.get_Linked_iBound(interval, is_lower_bound=True),
			interval.upper_bound.get_Linked_iBound(interval, is_lower_bound=False)
		)
		self.__linked_object = linked_object
		self.__original_iInterval = interval
	
	@property
	def linked_object(self):
		return self.__linked_object
	
	@property
	def original_interval(self):
		return self.__original_iInterval