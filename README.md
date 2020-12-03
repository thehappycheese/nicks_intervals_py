# NicksIntervals

This is a (**Work in progress**) pure python (3.7+) library for manipulating Intervals and Multi-Intervals.
Many other libraries are out there but:
 - many do not support modern type hints,
 - some are overcomplicated (for my purposes),
 - some have over-abbreviated and unreadable API
 - some are dependent on numpy and other libraries
 (id like a complete solution that can be understood by reading one set of documentation)
 - or were harder to learn, and less fun, than it was to write this library ;)

This one  https://github.com/kvesteri/intervals looks really popular but I have not tried it. You might want to take a look at that first as it appears to have more features and is properly tested.
It does not seem to proved a Multi_Interval class...?


In this library, three primary classes are provided:
```python
from NicksIntervals.Bound import Bound, PART_OF_LEFT, PART_OF_RIGHT
from NicksIntervals.Interval import Interval
from NicksIntervals.Multi_Interval import Multi_Interval
```

## iInterval() and iBound()

It is recommended that the iInterval class is constructed using the
following factory methods which are easy to read and understand:
```python
from NicksIntervals.Interval import Interval
my_interval = Interval.closed(0.0, 1.0)
my_interval = Interval.closed_open(0.0, 1.0)
my_interval = Interval.open_closed(0.0, 1.0)
my_interval = Interval.open(0.0, 1.0)
```

If required an `iInterval` can be directly constructed by providing the internal `iBound` objects:
```python
from NicksIntervals.Bound import Bound
from NicksIntervals.Bound import PART_OF_LEFT  # == True
from NicksIntervals.Bound import PART_OF_RIGHT  # == False
from NicksIntervals.Interval import Interval
# construct an interval from 0.0 to 1.0 where the exact value of both bounds are
# considered to be 'part of' this interval. (ie both bounds are closed)
my_interval = iInterval(iBound(0.0, PART_OF_RIGHT), iBound(0.0, PART_OF_LEFT))
```
Observe that since iIntervals and iBounds are both immutable, iBounds may be safely shared between iInterval instances.

in the current implementation it may be slightly annoying to access the interval bound values,
but this encapsulation of the value makes sense internally (I may find a way to improve this in the future): 
```python
print(my_interval.lower_bound.value) # >> 0.0
print(my_interval.upper_bound.value) # >> 1.0
```
## iMulti_iInterval()
This is the type for any arbitrary collection of `iIntervals`.
The collection is stored as an immutable tuple.
```python
from NicksIntervals.Interval import Interval
from NicksIntervals.Multi_Interval import Multi_Interval
my_multi_interval = iMulti_iInterval(
    (
        Interval.closed(1.0, 3.0),
        Interval.open(2.5, 3.1),
        ...
    )
)
```
# work in progress
the remainder of this readme needs to be updated to reflect the new immutable types

### iInterval Union
```python
from Interval import Interval
a = Interval(5, 15)
b = Interval(9, 11)
print(a.union(b))
# >>> Interval(5.00, 15.00)
```

### Interval Subtraction
Subtraction may return either an interval OR a multiinterval.
```python
from Interval import Interval, Multi_Interval
a = Interval(5, 15)
b = Interval(9, 11)
print(a.subtract(b))
# >>> Multi_Interval([Interval(5.00, 9.00), Interval(11.00, 15.00)])

c = Interval(5, 15)
d = Interval(10, 20)
print(c.subtract(d))
# >>> Interval(5.00, 10.00)
```

### Intersection
```python
from Interval import Interval
a = Interval(5, 15)
b = Interval(10, 20)
a.intersect(b)
# >>> Interval(10.00, 15.00)
```

### Intersection Test
```python
from Interval import Interval
a = Interval(5, 15)
b = Interval(10, 20)
print(a.intersects(b))
# >>> True
```
TODO: Internally this calls the .intersect() function and tests if the result is None.
In the future this could be optimised for improved performance since only a boolean result is required.

### Test if intervals are touching (and not overlapping)
The user may (or may not) consider values that are infinitesimally close to the end
of the interval to be included in the interval depending on the application.
this library tries to help a little bit with that sort of problem with the `Interval().touches()` function.

Note that .touches() returns False when .intersects() returns True
```python
from Interval import Interval
a = Interval(5,10)
b = Interval(10,20)
print(a.touches(b))

# >>> True
```
Note there is some basic handling of floating point weirdness:
```python
from Interval import Interval
a = Interval(5,9.99999999999)
b = Interval(10.00000000000001,20)
print(a.touches(b))  # internally uses the math.isclose() function
# >>> True
```

### Etc
Further documentation to come.

# Not Yet Implemented functions:
Many functions are still missing:
 - `Interval.xor()`
 - `Multi_Interval(...).subtract(Multi_Interval(...))`
 - etc
 
 
