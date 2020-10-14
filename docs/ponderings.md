# Ponderings

The Real Number line can be divided into Non-Overlapping  intervals as shown below:

![Image](/img/01_hero.svg)

This a 'map' from any given real number to an interval. They could each have a name as follows:

![Image](/img/02_numbered_hero.svg)

In building this model to represent intervals, the following properties are desireable
 1. A complete two way mapping is enforced. There are no real number values  which do not have a corresponding interval in the output space.

In practice the desire is that this interval library serves to deal with some of the pestersome problems that floating point numbers sometimes cause. The data that I intend to process has been through some pipeline of sql server extracts, excel spreadsheets, excel formulas, csv exports, and finally interpretation by the pandas library. If we make it through all that without one value somewhere == '1.01200000001' instead of '1.012' then pigs will fly.

Bounds are directed; they denote which interval the value AT the bound is treated.

To determine if a given python floating point number, X,
is contained by an interval, the following process is followed:

First the value of two bounds are obtained; lowerBound and upperBound
the python math.isclose(...) function is used to test for 'equality' to X
math.isclose(X, lowerBound) or math.isclose(X, upperBound)
If X is 'isclose' to the bound and the bound is closed, X is part of the interval.
otherwise the result is determined by the expression
'lower_bound<X<upper_bound'
