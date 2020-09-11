# interval-py

This is a (**Work in progress**) pure python (3.7+) library for manipulating Intervals and Multi-Intervals.
Many other libraries are out there but, based on my search results:
 - many do not support modern type hints,
 - overcomplicated (for my purposes),
 - over-abbreviated and unreadable API
 - dependencies galore (on numpy and other libraries)
 - or were harder to learn than it was to write this library ;)

This one  https://github.com/kvesteri/intervals looks really popular but I have not tried it. You might want to take a look at that first as it appears to have more features and is properly tested.
It does not seem to proved a Multi_Interval class...


In this library, two classes are provided:

`Interval(start: float, end: float)` <br>
and <br>
`Multi_Interval([Interval(...), Interval(...)])`


## Interval(start: float, end: float)

An Interval is a pair of values representing a start and end on a single dimension.

### Ordering
An `Interval().is_ordered` when `Interval().start <= Interval().end`.

Un-ordered or 'backwards' intervals are permitted however there are no checks to ensure that functions operate correctly on them.
Backwards intervals can be useful if treated with caution; 
`Interval(float('inf'), float('-inf'))`, can be used as as if it was an 'empty set' when using the `Interval(...).hull(Interval())` function to find the outer extent of a set of intervals:
```python
from Interval import Interval
# Create and interval that extends from positive infinity backwards to negative infinity
a = Interval(float('inf'), float('-inf'))
print(a.is_ordered)
# >>> False
b = Interval(9, 11)
c = Interval(10, 15)
d = a.hull(b).hull(c)
print(d)
# >>> Interval(9.00, 15.00)
```
This example is kind of pointless however, as you could just as simply do `b.hull(c)`. Perhaps it would be useful in an Array.reduce() as the initial parameter, or when working with other intervals with infinite endpoints.

### Custom Float Class as Start and End Arguments
Interval can accept any **start** and **end** arguments which behave like floating point numbers.
For this to work they must implement all of the following functions:
 -  `.__float__()`,
 - `.__lt__(arg: SupportsFloat)`,
 - `__gt__(arg: SupportsFloat)`,
 - `__le__(arg: SupportsFloat)`,
 - `__ge__(arg: SupportsFloat)`,
 - `__eq__(arg: SupportsFloat)`, and
 - `__ne__(arg: SupportsFloat)`

If custom float values are used: the Interval class can *_optionally_* be subclassed as follows to improve type hinting and code completion: 
```python
from Interval import Interval
class Custom_Float:
    pass # ... implement as described in dot-points above. See the github wiki for practical example

class Custom_Interval(Interval):
    def __init__(self, start: Custom_Float, end: Custom_Float):
        # Do not call the super().__init__()
        # super().__init__(start, end)  # <-- don't do this
        self.start: Custom_Float = start
        self.end: Custom_Float = end
```

Note: `Custom_Interval` will still return the base `Interval()` class instance when using the factory functions `Custom_Interval.make_infinite_empty()` and `Custom_Interval.make_infinite_full()` unless the user somehow overrides the `@classmethod`s (python doesnt really seem to be designed to do this however).

## Multi_Interval()

Multi_Intervals may be returned as the result of some functions: eg.<br>
`Interval(...).subtract(Interval(...))`

They can also be constructed by passing an iterable containing Interval()s<br>
`a = Multi_Interval([Interval(1,2), Interval(4,5)])`

Multi_Intervals will eventually support a number of more advanced functions and iterators to facilitate implementation of various line sweep algorithms.  

# Implemented functions


### Interval Union
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
 
 
