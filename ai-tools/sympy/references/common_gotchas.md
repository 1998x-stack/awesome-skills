# SymPy Common Gotchas

## Automatic Simplification

SymPy does NOT automatically simplify everything - only obvious simplifications.

### What IS Simplified

```python
x - x  # → 0
sqrt(8)  # → 2*sqrt(2)
x + x  # → 2*x
```

### What is NOT Simplified

```python
sin(x)**2 + cos(x)**2  # Stays as-is, not simplified to 1
(x**2 - 1)/(x - 1)  # Stays as-is, not simplified to x + 1

# Must explicitly call simplify
sp.simplify(sin(x)**2 + cos(x)**2)  # → 1
sp.simplify((x**2 - 1)/(x - 1))  # → x + 1
```

**Why?** "Simplest form" is subjective. SymPy leaves it to you to decide.

## Equality Testing

### Structural Equality vs Mathematical Equality

```python
a = cos(x)**2 + sin(x)**2
b = 1

# Structural equality (are they the same object?)
a == b  # False - different structure

# Mathematical equality (are they mathematically equal?)
sp.simplify(a - b) == 0  # True
```

**Key principle:** `==` tests if objects are identical, not mathematically equal.

### Comparing Expressions

```python
# These are different objects
expr1 = x + 1
expr2 = 1 + x

expr1 == expr2  # May be True or False depending on order

# Better: check mathematical equality
sp.simplify(expr1 - expr2) == 0  # Always True
```

## Integer Division

### Python Division vs SymPy Division

```python
# Python division (float)
1/2  # → 0.5 (float)

# SymPy needs symbolic input
sp.Rational(1, 2)  # → 1/2 (exact)
```

**Best practice:** Use `sp.Rational(a, b)` or `sp.S(1)/2`

```python
# Mixed division
x/2  # If x is symbolic: x/2 (exact)
x/2.0  # x/2.0 (introduces float)

# Always prefer:
x / sp.Rational(1, 2)  # x/(1/2) = 2*x
x / sp.S(2)  # x/2 (exact)
```

## Assumptions

### Inconsistent Assumptions

```python
# These are DIFFERENT symbols
x1 = sp.Symbol('x')
x2 = sp.Symbol('x', positive=True)

x1 == x2  # False!
x1 + x2  # x + x (treated as different variables)
```

**Best practice:** Use same assumptions for same symbol name throughout code.

### Assumption Limitations

```python
x = sp.Symbol('x', real=True)

# This works
sp.sqrt(x**2)  # x (assumes x can be negative)

x = sp.Symbol('x', positive=True)

# This simplifies correctly
sp.sqrt(x**2)  # x (knows x > 0)
```

## Power Identities

### Common Power Mistakes

```python
# These identities are NOT always true in SymPy
sqrt(x) * sqrt(y) != sqrt(x*y)  # Not always!
sqrt(x**2) != x  # Not always! (could be |x|)
(x**a)**b != x**(a*b)  # Not always!
```

**Example:**

```python
x = sp.Symbol('x', real=True)
# sqrt(x**2) → sqrt(x**2) (not simplified)

x = sp.Symbol('x', positive=True)
# sqrt(x**2) → x (simplified because x > 0)
```

## String Input

### Never Use eval()

```python
# NEVER do this - security risk
x = sp.Symbol('x')
eval("x**2 + 1")  # DANGEROUS!

# Use sympify or parse_expr instead
sp.sympify("x**2 + 1")  # Safe
from sympy.parsing.sympy_parser import parse_expr
parse_expr("x**2 + 1")  # Safe
```

## Numerical Precision

### Using math.pi vs sp.pi

```python
import math

# Wrong - numerical approximation
sin(math.pi)  # 1.22e-16 (not exactly 0)

# Right - symbolic constant
sin(sp.pi)  # 0 (exact)
```

### evalf() Precision

```python
# Default precision
sp.pi.evalf()  # 3.14159265358979

# Higher precision
sp.pi.evalf(50)  # 50 digits
sp.pi.evalf(100)  # 100 digits
```

## Function Definitions

### Undefined vs Defined Functions

```python
# Undefined function (symbolic)
f = sp.Function('f')
expr = f(x)  # f(x) - undefined

# Can differentiate
sp.diff(f(x), x)  # Derivative(f(x), x)

# Defined function (actual formula)
def f(x):
    return x**2
expr = f(x)  # x**2 - defined
```

## Matrix Gotchas

### Mutable vs Immutable Matrices

```python
# Mutable matrix
M = sp.Matrix([[1, 2], [3, 4]])
M[0, 0] = 5  # Allowed

# Immutable matrix
M_immut = sp.ImmutableMatrix([[1, 2], [3, 4]])
M_immut[0, 0] = 5  # Error!
```

### Matrix Indexing

```python
M = sp.Matrix([[1, 2], [3, 4]])

# 0-indexed
M[0, 0]  # 1 (first element)
M[1, 1]  # 4 (last element)

# Not 1-indexed like some math notation
```

## Substitution Surprises

### Substitution is Not Assignment

```python
expr = x + 1
expr.subs(x, 2)  # 3
expr  # Still x + 1 (unchanged!)

# Need to assign result
new_expr = expr.subs(x, 2)  # new_expr = 3
```

### Multiple Substitutions Order Matters

```python
expr = x + y

# List of tuples - applied left to right
expr.subs([(x, y), (y, 2)])  # 2 + 2 = 4

# Dictionary - order undefined
expr.subs({x: y, y: 2})  # Could be 2 + 2 or y + 2
```

## Plotting Gotchas

### Default Plot Range

```python
# Default: x from -10 to 10
sp.plot(sin(x))

# Specify range explicitly
sp.plot(sin(x), (x, 0, 2*sp.pi))
```

## Limits and Infinity

### Infinity Symbol

```python
# Use sp.oo for infinity (not float('inf'))
sp.limit(1/x, x, sp.oo)  # 0
sp.limit(1/x, x, 0, '+')  # oo (positive infinity)
```

## Importing

### Avoid `from sympy import *`

```python
# Bad - pollutes namespace
from sympy import *

# Good - explicit imports
import sympy as sp
from sympy import symbols, sin, cos
```

## Lambdify Limitations

### Not All SymPy Functions Supported

```python
# Some SymPy functions don't have NumPy equivalents
expr = sp.ceiling(x)
f = sp.lambdify(x, expr, 'numpy')  # May fail or give unexpected results

# Check lambdify docstring for supported functions
```

### Complex Number Handling

```python
# Be careful with complex results
expr = sp.sqrt(x)
f = sp.lambdify(x, expr, 'numpy')
f(-1)  # Returns nan, not 1j

# Use complex-aware backend
f = sp.lambdify(x, expr, 'numpy')
f(-1 + 0j)  # Returns 1j correctly
```

## Checking for Equality

### Use .equals() for Mathematical Equality

```python
expr1 = sin(x)**2 + cos(x)**2
expr2 = 1

# Structural equality
expr1 == expr2  # False

# Mathematical equality
expr1.equals(expr2)  # True (but can be slow)

# Faster: check difference
sp.simplify(expr1 - expr2) == 0  # True
```

## Derivative Notation

### diff() vs Derivative()

```python
# diff() - computes derivative immediately
sp.diff(x**2, x)  # 2*x

# Derivative() - unevaluated derivative
sp.Derivative(x**2, x)  # Derivative(x**2, x)
sp.Derivative(x**2, x).doit()  # 2*x (evaluate)
```

## Summary

**Key Takeaways:**
1. SymPy doesn't auto-simplify - call `simplify()` explicitly
2. Use `==` for structural equality, `.equals()` or `simplify(a-b)==0` for mathematical equality
3. Use `sp.Rational()` for exact fractions, not Python division
4. Keep assumptions consistent for same symbol name
5. Use `sp.pi`, `sp.E`, not `math.pi`, `math.e`
6. Never use `eval()` - use `sympify()` or `parse_expr()`
7. `lambdify` for fast numerical evaluation
8. Substitution creates new expression, doesn't modify original
