# Ponderings

## 1.0 - Anatomy of an Interval Object

An interval consists of exactly two 'Bounds'

```python
from NicksIntervals.iInterval import iInterval
from NicksIntervals.iBound import iBound, PART_OF_LEFT, PART_OF_RIGHT
my_first_interval - iInterval(iBound(0.5, PART_OF_RIGHT), iBound(1.0, PART_OF_LEFT))
```

Bounds are a floating point value, augmented with a direction; left, or right. This is implemented as a single boolean value. For ease of interpretation, the iBound module defines two boolean constants
```python
PART_OF_LEFT = False
PART_OF_RIGHT = True
```

If a bound is included_in_left; ie, the value of the bound is part of the interval to the right of the bound. It is reccomended that the second parameter is always provided for clarity (maybe i will make it non)

```python
my_first_bound = iBound(value=2.5, included_in_left=False)
```

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

## Interval Contains Interval


```python
int_a = iInterval(...)
int_b = iInterval(...)
int_a.contains(int_b) = ??
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