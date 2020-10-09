class iBound(float):
	"""This class extends python's built in float but adds an 'open' property. Intended to be used with iInterval.
	"""
	def __init__(self, value: float, closed: bool = True):
		if not isinstance(closed, bool):
			raise TypeError("iBound(open_bound=...) must be bool")
		self.__closed: bool = closed
	
	def __new__(cls, *args, **kwargs):
		return super().__new__(cls, args[0])
	
	@property
	def open(self) -> bool:
		return not self.__closed
	
	@property
	def closed(self) -> bool:
		return self.__closed