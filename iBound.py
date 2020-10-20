import math


PART_OF_LEFT = True
PART_OF_RIGHT = False


class iBound(float):
	
	def __init__(self, value: float, part_of_left: bool):
		"""
		:param value: The floating point value of the bound.
		:param part_of_left: The direction of the bound. If True, this bound is part of the interval to the left of this bound (ie. if used as a lower bound, it means that the value of this bound is excluded from the interval; and if used as an upper bound it is included in the interval). If false, the opposite applies. It is recommended that the PART_OF_LEFT and PART_OF_RIGHT constants are imported from this module to make your code easier to read.
		"""
		self.__part_of_left = part_of_left
		
		if not(isinstance(value, float) or isinstance(value, int)):
			raise TypeError(f"Unexpected argument type iBound(value=float,...) where value='{value}'")
		
		if not isinstance(part_of_left, bool):
			raise TypeError(f"Unexpected argument type iBound(...,part_of_left=bool) where part_of_left='{part_of_left}'")
		
		if self == float("-inf") and self.part_of_left:
			raise Exception("Bounds at -inf must be included_in_right")
		
		elif self == float("inf") and self.part_of_right:
			raise Exception("Bounds at inf must be included_in_left")
	
	def __new__(cls, *args, **kwargs):
		return super().__new__(cls, args[0])
	
	@property
	def part_of_left(self) -> bool:
		"""The value of this bound part of the interval to the left"""
		return self.__part_of_left
	
	@property
	def part_of_right(self) -> bool:
		"""The value of this bound part of the interval to the right"""
		return not self.__part_of_left
	
	def inverted(self):
		return iBound(float(self), not self.__part_of_left)
	
	def __format__(self, format_spec):
		arrow = "🡆"
		if self.part_of_left:
			arrow = "🡄"
		return "iBound("+(f"{{:{format_spec}}}").format(float(self))+","+arrow+")"
	
	def __repr__(self):
		return format(self, ".2f")
