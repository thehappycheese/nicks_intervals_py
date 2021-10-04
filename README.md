# NicksIntervals

Pure python library for manipulating Intervals and Multi-Intervals.
(With Python 3.7 type hints)

## Install, Upgrade, Uninstall

To install:

```powershell
pip install "https://github.com/thehappycheese/nicks_intervals_py/zipball/main/"
```

To Upgrade:

```powershell
pip install --upgrade "https://github.com/thehappycheese/nicks_intervals_py/zipball/main/"
```

To show installed version:

```powershell
pip show dtimsprep
```

To remove:

```powershell
pip uninstall dtimsprep
```

## Introduction

Other libraries are out there, but I wanted something that
 - Supports modern type hints,
 - Has readable API, with minimum abbreviation of function names
 - No dependency on numpy and other libraries
   - to have a stand-alone solution that can be understood by reading one set of code / documentation
 - Can handle collections of intervals
   - Manipulation of interval collections (`Multi_Interval`) including subtraction intersection etc. is missing from many other libraries.

In this library, several classes are provided:
```python
from NicksIntervals.Bound import Bound, PART_OF_LEFT, PART_OF_RIGHT
from NicksIntervals.Interval import Interval
from NicksIntervals.Multi_Interval import Multi_Interval
from NicksIntervals.Interval_Multi_Map import Interval_Multi_Map
```

Most operations are implemented in a 'functional style' and can be accessed either through the `Interval` class, or:
```python
import NicksIntervals._operators as ops
``` 


## 1.0 - Anatomy of an Interval

### 1.1 Definitions 

An `Interval` is an ordered pair of `Bound` objects; a `lower_bound` and an `upper_bound`.

Each `Bound` object specifies 
1. The floating point (or integer) value of the endpoint of an `Interval`, and
2. If the exact value of the bound is part of the interval to its left (`PART_OF_LEFT`) to to its right (`PART_OF_RIGHT`)

Initially this may seem confusing, but there are three important properties of this definition:
1. Bound objects may be shared between Interval objects
2. Bound objects do not know or care if they are the `upper_bound` or `lower_bound` of an `Interval`, and
3. Bound objects do not know or care if they are 'closed' or 'open', since this only makes sense once they are assigned to an interval as the upper or lower bound.

The idea of "closed" and "open" bound exist at the `Interval` level, and are
not explicit in the implementation.
For any Interval object:
 - If the `lower_bound` is "open" if it is   `PART_OF_LEFT` 
   - since the exact value of the bound is part of the non-existent interval to its left
 - If the `lower_bound` is "closed" if it is `PART_OF_RIGHT`
   - since the exact value of the bound is part of the interval.
 - If the `upper_bound` is "closed" if it is `PART_OF_LEFT`
 - If the `upper_bound` is "open" if it is   `PART_OF_RIGHT`


### 1.2 Constructing a Bound

Typically user-code will not need to construct a `Bound` object.
See the factory functions on the `Interval` object, described below,
which are much easier to read and write.

However it may help to understand that `Bound` objects 
are constructed internally using a floating point number (or integer) 
and a boolean value. To improve readability, the boolean constants 
`PART_OF_LEFT` and `PART_OF_RIGHT` are imported and used.

```python
from NicksIntervals.Bound import Bound, PART_OF_LEFT, PART_OF_RIGHT
# a bound at 0.5 that is part of the (non-existent) interval to the right
my_first_bound = Bound(
    0.5,
    PART_OF_RIGHT
)
```

>Note: Infinite `Bound` objects are allowed
>(using `float('inf')` and `float('-inf')`),
>but bounds at negative infinity must always be `PART_OF_RIGHT`,
>and bounds at positive infinity must always be `PART_OF_LEFT`.
>>
>This prevents intervals that "go up to but don't include infinity"
>which is a self contradiction.
 
### 1.3 Constructing an Interval
`Interval` objects can be manually constructed using two `Bound` objects:
```python
from NicksIntervals.Interval import Interval
from NicksIntervals.Bound import Bound, PART_OF_LEFT, PART_OF_RIGHT

# both bound values are part of the interval:
my_first_interval = Interval(
	Bound(
		0.5,
		PART_OF_RIGHT
	),
	Bound(
		1.0,
		PART_OF_LEFT
	)
)
```

However a less confusing way to construct intervals is to use the factory functions:

```python
from NicksIntervals.Interval import Interval

# both bound values are part of the interval: (Equivalent to the example above)
my_interval = Interval.closed(0.5, 1.0)

# neither of the bound values are part of the interval
my_interval = Interval.open(0.5, 1.0)

# only the right bound is part of the interval (the exact value 0.5 is excluded)
my_interval = Interval.open_closed(0.5, 1.0)

# only the left bound is part of the interval (the exact value 1.0 is excluded)
my_interval = Interval.closed_open(0.5, 1.0)

# Intervals with float('-inf') and float('inf') bounds are also possible this way.
#  Only the finite bound value needs to be specified:
my_interval = Interval.inf()
my_interval = Interval.inf_open(0.0)
my_interval = Interval.inf_closed(0.0)
my_interval = Interval.open_inf(0.0)
my_interval = Interval.closed_inf(0.0)
```

>**Tips and Tricks:**
> 
> To avoid errors caused by reversed bounds, construct your intervals like this:
> `Interval.closed(*sorted([some_value, some_other_value]))`

### 1.4 Multi_Intervals

Many operations on intervals may result in zero, one, or more intervals.
The result can be always be represented as a `Multi_Interval`.

Only when an operation results in exactly one interval,
the result can be represented as a single `Interval` object.
In all other cases a `Multi_Interval` object is returned.

The `Multi_Interval` object extends the `Interval` object
and has all the same functions (which is pretty magical really).

The `Multi_Interval` internally stores a tuple of zero or more `Interval` objects.

`Multi_Interval` objects should be considered to be **un-ordered** `Collection[Interval]` because most
unfortunately most operations do not preserve order.

>Note: For convenience `Interval` objects are also a `Collection[Interval]` where `len(Interval(...)) == 1`
>This is nice because the result of **any interval operation can iterated over** with a for loop, added to a list with the .extend() function, or added to a list using array expansion or comprehension.

`Multi_Interval` objects are constructed by supplying any `Iterable[]`
```python
from NicksIntervals.Interval import Interval
from NicksIntervals.Multi_Interval import Multi_Interval
my_multi_interval = Multi_Interval(
    (
        Interval.closed(1.0, 3.0),
        Interval.open(2.5, 3.1),
        ...
    )
)
```

### 1.5 Flat_Multi_Interval
Are a planned future feature to work with ordered, non-overlapping `Sequence[Interval]`.
Internally these would consist of a `sorted(List[Bound])` and `List[int]`. The former divides the real number line into non-overlapping 'Intervals' while the latter is a set of integer indexes/offsets into the first list which specify which of the intervals are interior.

### 1.6 Interval_Map and Interval_Mapping
TODO - write docs 

## Functions
### Subtraction
Subtraction may return either an interval OR a multiinterval.
```python
from NicksIntervals.Interval import Interval
from NicksIntervals.Multi_Interval import Multi_Interval

c = Interval.closed(5, 15)
d = Interval.closed(10, 20)
print(c.subtract(d))
# ≤5.00, 10.00>
```

Multi_Intervals have the same functions as intervals: 
```python
from NicksIntervals.Interval import Interval
from NicksIntervals.Multi_Interval import Multi_Interval

a = Interval.closed(5, 15)
b = Interval.closed(9, 11)
c = a.subtract(b)
print(c)
# Multi_Interval[2]([≤5.00, 9.00>, <11.00, 15.00≥])

d = Interval.closed(0, 20)
e = d.subtract(c)
print(e)
# Multi_Interval[3]([≤0.00, 5.00>, ≤9.00, 11.00≥, <15.00, 20.00≥])
```

### Intersection
```python
from NicksIntervals.Interval import Interval

a = Interval.closed(5, 15)
b = Interval.closed(10, 20)
print(a.intersect(b))
# ≤10.00, 15.00≥
```

### Intersection Test
```python
from NicksIntervals.Interval import Interval

a = Interval.closed(5, 15)
b = Interval.closed(10, 20)
print(a.intersects(b))
# >>> True
```

## work in progress
The remainder of this readme needs to be updated to reflect some changes:
