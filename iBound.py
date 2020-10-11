class iBound(float):
	"""inherits from float; adds an 'open' property. closed property is also provided.
	Closed means that the value at the bound is included in the interval
	Open means the value at the bound is not part of the interval.
	
	This is similar to the concept of A is 'less than or equal to' B  compared with A is 'less than' B
	
	In the case of intervals things are difficult because when we approach from one side things are included, but when we approach from the other, they may or may not be excluded.
	When a bound is closed, it should be safe to use math.isclose() in place of == (all this nonsense has to be handled in the iInterval class)
	
	Since the bound class may be reused by multiple intervals it is immutable.
	This also means that it has no relationship with it's parent interval class; this bound cannot know if it is an upper bound or a lower bound.
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