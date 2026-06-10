# SymPy Performance Optimization

## Overview

SymPy is powerful for symbolic computation but can be slow for numerical evaluation. Use these strategies to optimize performance.

## Optimization Strategies

### 1. Use lambdify for Numerical Evaluation

**Problem:** `.subs().evalf()` is extremely slow for repeated evaluations.

**Solution:** Convert to numerical function once, reuse many times.

```python
import sympy as sp
import numpy as np

x = sp.Symbol('x')
expr = sp.sin(x) / x

# Slow (tens of microseconds per call)
result_slow = expr.subs(x, 3.14).evalf()

# Fast (hundreds of nanoseconds per call)
f = sp.lambdify(x, expr, 'numpy')
result_fast = f(3.14)

# Even better for arrays
x_vals = np.linspace(-10, 10, 1000)
y_vals = f(x_vals)  # Vectorized, very fast
```

**Performance gain:** 100-1000x speedup

### 2. Common Subexpression Elimination (CSE)

Eliminate redundant calculations in complex expressions:

```python
from sympy.simplify.cse_main import cse

# Complex expressions with repeated terms
expr1 = sp.sin(x)**2 + sp.cos(x) + sp.sin(x)**2 * sp.cos(x)
expr2 = sp.sin(x)**2 - sp.cos(x)

# Find common subexpressions
replacements, reduced = cse([expr1, expr2])
# replacements: [(x0, sin(x)**2), (x1, cos(x))]
# reduced: [x0 + x1 + x0*x1, x0 - x1]

# Use for code generation
from sympy.utilities.codegen import codegen
codegen(('optimized', reduced), 'C')
```

### 3. Choose Appropriate Backends

Different numerical backends for different use cases:

```python
# Standard library math (single values)
f_math = sp.lambdify(x, expr, 'math')

# NumPy (arrays, CPU)
f_numpy = sp.lambdify(x, expr, 'numpy')

# CuPy (GPU acceleration)
f_cupy = sp.lambdify(x, expr, 'cupy')

# JAX (JIT compilation, GPU/TPU)
f_jax = sp.lambdify(x, expr, 'jax')
```

### 4. Avoid Creating Large Symbolic Matrices

**Problem:** Symbolic matrix operations are very slow.

```python
# Bad: Large symbolic matrix
import numpy as np
T = np.random.rand(100, 1000)
X = sp.Matrix([sp.Symbol(f'x{i}') for i in range(1000)])
W = sp.Matrix(T)
V = W * X  # Extremely slow!
```

**Solution:** Keep matrices numerical, use SymPy only for small symbolic matrices.

```python
# Good: Numerical matrices
import numpy as np
T = np.random.rand(100, 1000)
x_numeric = np.random.rand(1000)
V = T @ x_numeric  # Fast!
```

### 5. Use Rational Instead of Float

For exact arithmetic, use `sp.Rational`:

```python
# Floating point (loses precision)
result = (1/10 + 1/10 + 1/10) * 3
# 0.9000000000000001

# Rational (exact)
r = sp.Rational
result = (r(1,10) + r(1,10) + r(1,10)) * 3
# 9/10
```

### 6. Cache Expensive Operations

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def compute_derivative(expr_str, var_str):
    expr = sp.sympify(expr_str)
    var = sp.Symbol(var_str)
    return sp.diff(expr, var)

# First call: slow (computes)
result1 = compute_derivative('x**2 + sin(x)', 'x')

# Subsequent identical calls: instant (cached)
result2 = compute_derivative('x**2 + sin(x)', 'x')
```

### 7. Compile to C/Fortran with autowrap/ufuncify

For maximum performance, generate compiled code:

```python
from sympy.utilities.autowrap import ufuncify

x = sp.Symbol('x')
expr = sp.sin(x)**2 + sp.cos(x)**2

# Generate and compile C code
f_compiled = ufuncify(x, expr)

# Use like a normal function (but much faster)
import numpy as np
x_vals = np.linspace(0, 10, 1000)
result = f_compiled(x_vals)
```

**Note:** Requires f2py or Cython installed.

## Performance Benchmarks

Typical performance for evaluating `sin(x)/x` at 1000 points:

| Method | Time | Relative Speed |
|--------|------|----------------|
| `.subs().evalf()` loop | ~10 seconds | 1x |
| `lambdify` + loop | ~10 ms | 1000x |
| `lambdify` + NumPy array | ~100 μs | 100,000x |
| `ufuncify` (compiled) | ~10 μs | 1,000,000x |

## When to Use Each Method

**`.subs().evalf()`**: Quick prototyping, one-off calculations
**`lambdify`**: Repeated evaluations, production code
**CSE**: Complex expressions with redundancy
**`autowrap/ufuncify`**: Maximum performance needed, worth compilation overhead

## Common Pitfalls

### Pitfall 1: Using math.pi instead of sp.pi

```python
import math

# Wrong: numerical approximation
expr = sp.sin(math.pi)  # 1.22e-16 (not exactly 0)

# Right: symbolic constant
expr = sp.sin(sp.pi)  # 0 (exact)
```

### Pitfall 2: Forgetting to Simplify Before Evaluation

```python
# Slow: complex unsimplified expression
expr = sp.expand((x + 1)**100)
f = sp.lambdify(x, expr, 'numpy')

# Faster: simplify first if possible
expr_simple = sp.simplify(expr)  # May reduce complexity
f = sp.lambdify(x, expr_simple, 'numpy')
```

### Pitfall 3: Not Reusing Lambdified Functions

```python
# Bad: recreating function each time
for i in range(1000):
    f = sp.lambdify(x, expr, 'numpy')  # Slow!
    result = f(i)

# Good: create once, reuse
f = sp.lambdify(x, expr, 'numpy')
for i in range(1000):
    result = f(i)  # Fast!
```

## Memory Optimization

Large symbolic expressions can consume lots of memory:

```python
# Clear internal caches periodically
sp.clear_cache()

# Use gc.collect() for large computations
import gc
gc.collect()
```

## Profiling SymPy Code

Use line_profiler to identify bottlenecks:

```python
%load_ext line_profiler

def my_sympy_function():
    # Your SymPy code here
    pass

%lprun -f my_sympy_function my_sympy_function()
```
