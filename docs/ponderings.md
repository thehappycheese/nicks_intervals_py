# Ponderings

## 1.0 - Anatomy of an Interval Object

An interval consists of exactly two 'Bounds'

```python
from NicksIntervals.iInterval import iInterval
from NicksIntervals.iBound import iBound, PART_OF_LEFT, PART_OF_RIGHT

my_first_interval = iInterval(
	iBound(
		0.5,
		PART_OF_RIGHT
	),
	iBound(
		1.0,
		PART_OF_LEFT
	)
)
```

iBounds represent a floating point value, augmented with a direction; left, or right. iBounds support coersion to float and all comparrison opperators. Internally this is implemented as a single boolean value which is the second parameter to the constructor. To improve the readability of usercode it is reccomended that you import the following constants from the iBound module:
```python
# Signifies that a bound is part of the interval to the left of it's value:
PART_OF_LEFT = False

# Signifies that a bound is part of the interval to the right of it's value:
PART_OF_RIGHT = True
```

Alternatively, use the iInterval constructors iInterval.open, iInterval.closed, iInterval.open_closed or iInterval.closed_open which simply take the two bound values and internally set the direction of the bounds relative to the interval.

Any pair of bounds can completly define an Interval object. An ordered list of bounds defines a segmentation of the real number line into interval objects. The bounds at -infinity and +infinity are used to define the 'left exterior' and 'right exterior' region of an interval or list of bounds. The tuple of the left exterior and the right exterior is simply called the 'exterior'.
- If the first bound of an interval is at -infinity, its 'left exterior' is an empty tuple
- If the second bound of an interval is at +infinity, its 'right exterior' is an empty tuple.

The Real Number line can be divided into Non-Overlapping  intervals as shown below:

![Image](/img/01_hero.svg)

This a 'map' from any given real number to an interval:

![Image](/img/02_numbered_hero.svg)


### Multi-Intervals

Overlapping Multi Intervals

### Floating Point wierdness
Floating point number wierdness is handled using python math.isclose()


In building this model to represent intervals, the following properties are desireable
 1. When dealing with a collection of intervals there must be two modes:
    - A complete two way mapping is enforced. There are no real number values  which do not have a corresponding interval in the output space.
 2. 


Bounds are directed; they denote which interval the value AT the bound is treated.



## Contains Value

To determine if a given python floating point number, X,
is contained by an interval, the following process is followed:

First the value of two bounds are obtained; lowerBound and upperBound
the python math.isclose(...) function is used to test for 'equality' to X
math.isclose(X, lowerBound) or math.isclose(X, upperBound)
If X is 'isclose' to the bound and the bound is closed, X is part of the interval.
otherwise the result is determined by the expression
'lower_bound<X<upper_bound'

## Test if an Interval Interval Contains Interval


```python
int_a = iInterval(...)
int_b = iInterval(...)
int_a.contains_interval(int_b) = ??
```

When the bound of one interval `math.isclose()` to the bound of another interval, there the truth table below is consulted to see if the bound is contained within the interval. Otherwise the if `int_a.start<the_bound<int_a.end` then the bound is contained within the interval. Otherwise the bound is not contained. Finally, if both bounds of an_interval are contained within another_interval, then `another_interval.contains(an_interval)==True`

Truth Table
|Interval|🡆	|Upper|	|Lower|	|
|---|---|---|---|---|---|
|Contains|🡇	|open	|closed	|open	|closed	|
|Upper	|open	|T		|T		|F		|F		|
|		|closed	|F		|T		|F		|T		|
|Lower	|open	|F		|F		|T		|T		|
|		|closed	|F		|T		|F		|T		|


Visualised:

![bla](/img/03_contains_lower_upper_bounds.svg)