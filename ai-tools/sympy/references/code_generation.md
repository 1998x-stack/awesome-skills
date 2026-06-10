# SymPy Code Generation

## Overview

SymPy can generate optimized code in C, Fortran, Python, JavaScript, Julia, and other languages from symbolic expressions.

## lambdify - Python/NumPy Code

Convert symbolic expressions to fast numerical functions:

```python
import sympy as sp
import numpy as np

x, y = sp.symbols('x y')
expr = sp.sin(x) * sp.exp(-y)

# Generate Python function using NumPy
f = sp.lambdify((x, y), expr, 'numpy')

# Use with scalars or arrays
result_scalar = f(0.5, 1.0)
result_array = f(np.array([0.1, 0.2, 0.3]), 1.0)
```

### Available Modules

```python
# Standard library math
f = sp.lambdify(x, expr, 'math')

# NumPy (default, best for arrays)
f = sp.lambdify(x, expr, 'numpy')

# SciPy
f = sp.lambdify(x, expr, 'scipy')

# SymPy (symbolic evaluation)
f = sp.lambdify(x, expr, 'sympy')

# CuPy (GPU acceleration)
f = sp.lambdify(x, expr, 'cupy')

# JAX (JIT compilation)
f = sp.lambdify(x, expr, 'jax')
```

### Custom Function Mapping

```python
# Map SymPy functions to custom implementations
def my_sin(x):
    """Custom sine implementation."""
    return np.sin(x) * 1.1  # 10% error

f = sp.lambdify(x, sp.sin(x), {'sin': my_sin})
```

## codegen - C/Fortran Code Generation

Generate source code files for compiled languages:

```python
from sympy.utilities.codegen import codegen

x, y = sp.symbols('x y')
expr = x**2 + sp.sin(y)

# Generate C code
[(c_name, c_code), (h_name, h_header)] = codegen(
    ('my_func', expr),
    'C',
    header=False,
    empty=False
)

print(c_name)  # my_func.c
print(c_code)  # C source code
```

### C Code Example

```python
expr = x**2 + sp.sin(x)
[(c_name, c_code), (h_name, h_header)] = codegen(
    ('f', expr),
    'C'
)
```

Output:
```c
double f(double x) {
    double f_result;
    f_result = pow(x, 2) + sin(x);
    return f_result;
}
```

### Fortran Code Generation

```python
# Generate Fortran 95 code
[(f_name, f_code), (h_name, h_header)] = codegen(
    ('my_func', expr),
    'F95'
)
```

Output:
```fortran
REAL*8 function my_func(x, y)
    implicit none
    REAL*8, intent(in) :: x
    REAL*8, intent(in) :: y
    my_func = x**2 + sin(y)
end function
```

## autowrap - Compile and Import

Automatically compile and import generated code:

```python
from sympy.utilities.autowrap import autowrap

x = sp.Symbol('x')
expr = sp.sin(x) / x

# Generate, compile, and import as Python function
f = autowrap(expr, backend='f2py')  # or backend='cython'

# Use like any Python function
import numpy as np
result = f(np.linspace(0.1, 10, 100))
```

### Backend Options

```python
# f2py (Fortran → Python)
f = autowrap(expr, backend='f2py')

# Cython (C → Python)
f = autowrap(expr, backend='cython')

# dummy (for testing, doesn't compile)
f = autowrap(expr, backend='dummy')
```

## ufuncify - NumPy Universal Functions

Create NumPy ufuncs from SymPy expressions:

```python
from sympy.utilities.autowrap import ufuncify
import numpy as np

x = sp.Symbol('x')
expr = sp.sin(x)**2 + sp.cos(x)**2

# Create numpy ufunc
f = ufuncify(x, expr)

# Works with arrays element-wise
x_vals = np.linspace(0, 10, 1000)
result = f(x_vals)
```

## Common Subexpression Elimination

Optimize code by eliminating redundant calculations:

```python
from sympy.simplify.cse_main import cse

x = sp.Symbol('x')

# Expression with repeated subexpressions
expr1 = sp.sin(x)**2 + sp.cos(x)
expr2 = sp.sin(x)**2 - sp.cos(x)
expr3 = sp.sin(x)**2 * sp.cos(x)

# Find common subexpressions
replacements, reduced = cse([expr1, expr2, expr3])

# replacements: [(x0, sin(x)**2), (x1, cos(x))]
# reduced: [x0 + x1, x0 - x1, x0*x1]

# Generate optimized C code
from sympy.utilities.codegen import codegen
code = codegen(
    [('expr1', reduced[0]),
     ('expr2', reduced[1]),
     ('expr3', reduced[2])],
    'C',
    header=False
)
```

## Optimization for Code Generation

### FLOPs Optimization

```python
from sympy.codegen.rewriting import optimize, optims_c99

x = sp.Symbol('x')

# Original expression
expr = sp.exp(x) - 1

# Optimize for C99 (uses expm1 for better precision)
optimized = optimize(expr, optims_c99)
# Result: expm1(x)

# Generate code
f = sp.lambdify(x, optimized, 'numpy')
```

### Matrix Expression Optimization

```python
from sympy.codegen.rewriting import optimize
from sympy import MatrixSymbol, Q, assuming

n = sp.symbols('n', integer=True)
A = MatrixSymbol('A', n, n)
x = MatrixSymbol('x', n, 1)

# Original: inverse multiplication
expr = A**(-1) * x

# Optimize: convert to solve
with assuming(Q.fullrank(A)):
    optimized = optimize(expr)
# Result: MatrixSolve(A, x) instead of A^(-1) * x
```

## Language-Specific Generation

### JavaScript

```python
from sympy.printing.jscode import jscode

x = sp.Symbol('x')
expr = sp.sin(x) + sp.exp(x)

code = jscode(expr)
print(code)  # Math.sin(x) + Math.exp(x)
```

### Julia

```python
from sympy.printing.julia import julia_code

x, y = sp.symbols('x y')
expr = x**2 + sp.sqrt(y)

code = julia_code(expr)
print(code)  # x.^2 + sqrt(y)
```

### Rust

```python
from sympy.printing.rust import rust_code

x = sp.Symbol('x')
expr = sp.sin(x) * sp.cos(x)

code = rust_code(expr)
print(code)  # x.sin()*x.cos()
```

### Octave/MATLAB

```python
from sympy.printing.octave import octave_code

x, y = sp.symbols('x y')
expr = x**2 + sp.sin(y)

code = octave_code(expr)
print(code)  # x.^2 + sin(y)
```

## Code Generation Workflow

### Complete Example: Optimize and Generate

```python
import sympy as sp
from sympy.simplify.cse_main import cse
from sympy.utilities.codegen import codegen

# 1. Define symbolic problem
x, y, z = sp.symbols('x y z')

# Complex expression with redundancy
expr = sp.sin(x)**2 * sp.cos(y) + sp.sin(x)**2 * sp.sin(y) + sp.cos(z)

# 2. Apply CSE optimization
replacements, reduced = cse([expr])

# 3. Generate optimized C code
code_blocks = []
for i, (sym, subexpr) in enumerate(replacements):
    code_blocks.append((f'temp_{i}', subexpr))
code_blocks.append(('result', reduced[0]))

[(c_name, c_code), (h_name, h_header)] = codegen(
    code_blocks,
    'C',
    header=False
)

print(c_code)
```

## Best Practices

### 1. Profile Before Optimizing

```python
import timeit

# Time symbolic evaluation
symbolic_time = timeit.timeit(
    lambda: expr.subs(x, 0.5),
    number=1000
)

# Time lambdified function
f = sp.lambdify(x, expr, 'numpy')
lambdify_time = timeit.timeit(
    lambda: f(0.5),
    number=1000
)

print(f"Speedup: {symbolic_time / lambdify_time:.1f}x")
```

### 2. Choose Appropriate Method

- **lambdify**: Quick, 100-1000x faster than symbolic
- **autowrap/ufuncify**: Maximum performance, requires compilation
- **codegen**: When integrating with existing C/Fortran projects

### 3. Verify Generated Code

Always test generated code matches symbolic results:

```python
# Symbolic result
symbolic_result = expr.subs(x, 0.5).evalf()

# Generated code result
f = sp.lambdify(x, expr, 'numpy')
generated_result = f(0.5)

# Verify match
assert abs(symbolic_result - generated_result) < 1e-10
```

### 4. Handle Special Cases

```python
# Some SymPy functions may not have equivalents
expr = sp.ceiling(x)  # May not translate well

# Check generated code behavior
f = sp.lambdify(x, expr, 'numpy')
try:
    result = f(1.5)
except:
    print("Function not supported in target language")
```

## Advanced: Custom Code Printers

Create custom code generators for specialized needs:

```python
from sympy.printing.c import C99CodePrinter

class MyCodePrinter(C99CodePrinter):
    def _print_sin(self, expr):
        # Custom sine implementation
        return f"my_sin({self._print(expr.args[0])})"

printer = MyCodePrinter()
x = sp.Symbol('x')
code = printer.doprint(sp.sin(x))
print(code)  # my_sin(x)
```

## Summary

**Quick Reference:**
- `lambdify`: Fast Python functions (100x speedup)
- `codegen`: Generate C/Fortran source files
- `autowrap`: Compile and import automatically
- `ufuncify`: NumPy universal functions
- `cse`: Eliminate common subexpressions
- Print to specific languages: `jscode`, `julia_code`, `rust_code`, etc.

**When to use what:**
- Prototyping: `lambdify` with 'numpy'
- Production Python: `lambdify` or `ufuncify`
- Integration with C/Fortran: `codegen`
- Maximum performance: `autowrap` with CSE optimization
