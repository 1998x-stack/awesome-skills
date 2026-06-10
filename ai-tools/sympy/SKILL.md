---
name: sympy
description: "Symbolic mathematics computation in Python using SymPy. Use when the user needs to: (1) Solve mathematical equations symbolically, (2) Perform calculus operations (derivatives, integrals, limits), (3) Simplify or manipulate algebraic expressions, (4) Work with matrices symbolically, (5) Derive mathematical formulas, (6) Prove mathematical identities, (7) Generate code from symbolic expressions, or (8) Perform exact symbolic computation rather than numerical approximation."
---

# SymPy Skill

## Overview

Enable symbolic mathematics computation in Python using SymPy - perform exact symbolic calculations, solve equations, compute derivatives and integrals, manipulate expressions, and work with mathematical proofs.

## Quick Start

Import and initialize SymPy:

```python
import sympy as sp
sp.init_printing(use_unicode=True)  # Pretty printing

# Define symbols
x, y = sp.symbols('x y')

# Create and manipulate expressions
expr = x**2 + 2*x + 1
sp.factor(expr)  # (x + 1)**2
```

## Core Capabilities

### 1. Symbol Definition and Manipulation

Define symbolic variables with optional assumptions:

```python
# Basic symbols
x, y, z = sp.symbols('x y z')

# Symbols with assumptions
n = sp.Symbol('n', integer=True, positive=True)
theta = sp.Symbol('theta', real=True)

# Expression creation
expr = x**2 + sp.sin(y) + sp.exp(z)
```

### 2. Algebraic Operations

```python
# Expand expressions
sp.expand((x + 1)**3)  # x**3 + 3*x**2 + 3*x + 1

# Factor expressions
sp.factor(x**2 - 1)  # (x - 1)*(x + 1)

# Simplify expressions
sp.simplify((x**2 - 1)/(x - 1))  # x + 1

# Trigonometric simplification
sp.trigsimp(sp.sin(x)**2 + sp.cos(x)**2)  # 1

# Substitution
expr.subs(x, 2)  # Replace x with 2
expr.subs([(x, 1), (y, sp.pi)])  # Multiple substitutions
```

### 3. Calculus Operations

```python
# Differentiation
f = x**3 + 2*x**2 - x
sp.diff(f, x)  # 3*x**2 + 4*x - 1
sp.diff(f, x, 2)  # Second derivative: 6*x + 4

# Partial derivatives
g = x**2 * y + sp.sin(x*y)
sp.diff(g, x, y)  # Mixed partial derivative

# Integration
sp.integrate(x**2, x)  # x**3/3
sp.integrate(x**2, (x, 0, 1))  # Definite integral: 1/3

# Limits
sp.limit(sp.sin(x)/x, x, 0)  # 1

# Taylor series
sp.series(sp.exp(x), x, 0, 5)  # 1 + x + x**2/2 + ...
```

### 4. Equation Solving

```python
# Algebraic equations
sp.solve(x**2 - 4, x)  # [-2, 2]

# Systems of equations
eq1 = sp.Eq(2*x + y, 5)
eq2 = sp.Eq(x - y, 1)
sp.solve([eq1, eq2], [x, y])  # {x: 2, y: 1}

# Differential equations
f = sp.Function('f')
diffeq = sp.Eq(f(x).diff(x) + f(x), sp.exp(x))
sp.dsolve(diffeq, f(x))
```

### 5. Matrix Operations

```python
# Create matrices
M = sp.Matrix([[1, 2], [3, 4]])

# Matrix operations
M.det()  # Determinant: -2
M.inv()  # Inverse matrix
M.eigenvals()  # Eigenvalues
M.eigenvects()  # Eigenvectors

# Solve linear systems
A = sp.Matrix([[1, 2], [3, 4]])
b = sp.Matrix([5, 6])
A.solve(b)  # Solution vector
```

### 6. Code Generation

Convert symbolic expressions to numerical code:

```python
from sympy.utilities.lambdify import lambdify
import numpy as np

# Create symbolic expression
expr = sp.sin(x)/x

# Convert to fast numerical function
f = lambdify(x, expr, 'numpy')

# Use with NumPy arrays
x_vals = np.linspace(-10, 10, 1000)
y_vals = f(x_vals)  # 100x faster than .subs()
```

## Best Practices

### Use Rational Numbers for Exact Results

```python
# Avoid floating point
expr = sp.Rational(1, 3) + sp.Rational(1, 3)  # 2/3 (exact)

# Not: 1/3 + 1/3  # 0.6666... (approximate)
```

### Separate Symbolic and Numerical Computation

```python
# Good: Derive formula symbolically, then compute numerically
formula = sp.integrate(sp.sin(x)**2, x)  # Symbolic
f = lambdify(x, formula, 'numpy')        # Convert
result = f(np.linspace(0, np.pi, 100))   # Numerical computation
```

### Use Simplification Explicitly

```python
# SymPy doesn't auto-simplify everything
expr = sp.sin(x)**2 + sp.cos(x)**2
expr  # Not simplified automatically
sp.simplify(expr)  # 1
```

### Handle Assumptions Properly

```python
# Define assumptions upfront
x = sp.Symbol('x', real=True, positive=True)
sp.sqrt(x**2)  # Can simplify to x (not |x|)
```

## Common Patterns

### Pattern 1: Solving Physics Problems

```python
# Define physical variables
t, g, v0, h0 = sp.symbols('t g v0 h0')

# Motion equation
h = h0 + v0*t - sp.Rational(1, 2)*g*t**2

# Find velocity (derivative)
v = sp.diff(h, t)

# Find landing time (solve for t when h=0)
landing_time = sp.solve(h, t)
```

### Pattern 2: Deriving Formulas

```python
# Start with general formula
a, b, c = sp.symbols('a b c')
quadratic = a*x**2 + b*x + c

# Derive quadratic formula
solutions = sp.solve(quadratic, x)
# Returns: [(-b - sqrt(b**2 - 4*a*c))/(2*a), ...]
```

### Pattern 3: Verifying Identities

```python
# Left and right sides of identity
lhs = sp.sin(2*x)
rhs = 2*sp.sin(x)*sp.cos(x)

# Check if equal
sp.simplify(lhs - rhs) == 0  # True
```

## Performance Optimization

For numerical evaluation of symbolic expressions:

1. **Use `lambdify`** for repeated numerical evaluation (100x faster)
2. **Use CSE** (Common Subexpression Elimination) for complex expressions
3. **Convert to NumPy** for array operations
4. **Avoid large symbolic matrices** - use NumPy for numerical matrices

See `references/performance_tips.md` for detailed optimization strategies.

## Advanced Features

For specialized use cases, see:
- `references/quantum_mechanics.md` - Quantum physics calculations
- `references/code_generation.md` - Generate C/Fortran/Python code
- `references/advanced_calculus.md` - Vector calculus, differential geometry
- `references/number_theory.md` - Prime numbers, factorization, modular arithmetic

## Resources

### references/
- `performance_tips.md` - Performance optimization strategies and benchmarks
- `quantum_mechanics.md` - Using sympy.physics.quantum for quantum computations
- `code_generation.md` - Generating optimized code in various languages
- `advanced_calculus.md` - Vector calculus and differential geometry
- `number_theory.md` - Number theory functions and applications
- `common_gotchas.md` - Common pitfalls and how to avoid them
