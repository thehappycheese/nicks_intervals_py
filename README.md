# interval-py
pure python library for manipulating intervals and groups of intervals. An Interval is a pair of values representing a start and end on a single dimension.

Many functions are still missing, especially for Multi_Intervals(). For example it is not possible to subtract a Multi_Interval from a Multi_Interval yet.
However most useful operations are supported for the basic Interval class.

A Multi_Interval class is provided and is very complicated. Internlly it manages `self.intervals: List[Interval()]`. The intervals in this list may be overlapping depending on how they were added.

### Interval Subtraction
```python
from Interval import Interval, Multi_Interval
a = Interval(5,15)
b = Interval(9,11)
a.subtract(b)

# Multi_Interval([Interval(5.00, 9.00), Interval(11.00, 15.00)])
```
Note that in this case the result has been a Multi_Interval() but it could also have been a plain Interval()
### Intersection
```python
from Interval import Interval, Multi_Interval
a = Interval(5,15)
b = Interval(10,20)
a.intersect(b)

# Interval(10.00, 15.00)
```

### Intersection Test
Internally calls the .intersect() function and tests if the result is none.
In the future this could be optimised for improved performance if only a boolean result is required.
```python
a.intersects(b)

# True
```

### Test if intervals are touching (and not overlapping)
.touches() returns False when .intersects() returns True
```python
from Interval import Interval, Multi_Interval
a = Interval(5,10)
b = Interval(10,20)
print(a.touches(b))

# >>> True
```
Note there is some basic handeling of floating point wierdness:
```python
from Interval import Interval, Multi_Interval
a = Interval(5,9.99999999999)
b = Interval(10.00000000000001,20)
print(a.touches(b))  # internally uses the math.isclose() function
# >>> True
```

### Etc
Further documentation to come.