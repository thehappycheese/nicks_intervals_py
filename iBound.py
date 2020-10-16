import math


class iBound(float):
	
	def __init__(self, value: float, included_in_left: bool = False):
		"""
		:param included_in_left: This bound is included in interval to the left
		"""
		self.__closed_left = included_in_left
		if self == float("-inf") and self.included_in_left:
			raise Exception("Bounds at -inf must be closed_right")
		elif self == float("inf") and self.included_in_right:
			raise Exception("Bounds at inf must be closed_left")
	
	def __new__(cls, *args, **kwargs):
		return super().__new__(cls, args[0])
	
	@property
	def included_in_left(self) -> bool:
		"""included in interval to the left"""
		return self.__closed_left
	
	@property
	def included_in_right(self) -> bool:
		"""included in interval to the right"""
		return not self.__closed_left
	
	def inverted(self):
		return iBound(float(self), not self.__closed_left)
	
	def contains(self, value: float):
		"""math.isclose"""
		return math.isclose(self, value)
