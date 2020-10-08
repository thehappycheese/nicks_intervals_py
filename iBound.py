import math

class iBound(float):
	"""This class extends python's built in float but adds an 'open' property. Intended to be used with iInterval.
	TODO: I have not used it yet though as it is not yet clear if the extra complexity of the implementation is worth the bother.
	"""
	def __init__(self, value: float, open_bound: bool = False):
		if not isinstance(value, float):
			raise TypeError("iBound(value=...) must be float")
		if not isinstance(open_bound, bool):
			raise TypeError("iBound(open_bound=...) must be bool")
		self.__open = open_bound
	
	def __new__(cls, *args, **kwargs):
		return super().__new__(cls, args[0])
	
	@property
	def open(self):
		return self.__open
	
	def __eq__(self, other):
		return math.isclose(self, other)