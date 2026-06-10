# SymPy Quantum Mechanics

## Overview

SymPy's `sympy.physics.quantum` module provides symbolic quantum mechanics capabilities for bras, kets, operators, and quantum systems.

## Basic Quantum Objects

### Quantum States (Kets and Bras)

```python
from sympy.physics.quantum import Ket, Bra, Dagger

# Create a ket
psi = Ket('psi')
print(psi)  # |psi>

# Create corresponding bra (Hermitian conjugate)
psi_bra = Dagger(psi)
print(psi_bra)  # <psi|

# Or create bra directly
phi_bra = Bra('phi')
```

### Operators

```python
from sympy.physics.quantum import Operator

# Create operators
A = Operator('A')
B = Operator('B')

# Operator algebra
A * B  # A*B (matrix multiplication)
A + B  # A + B (addition)
```

### Commutators and Anticommutators

```python
from sympy.physics.quantum import Commutator, AntiCommutator

# Commutator [A, B] = AB - BA
comm = Commutator(A, B)
comm.doit()  # A*B - B*A

# Anticommutator {A, B} = AB + BA
anticomm = AntiCommutator(A, B)
anticomm.doit()  # A*B + B*A
```

### Inner Products

```python
from sympy.physics.quantum import InnerProduct

# <phi|psi>
inner = InnerProduct(Bra('phi'), Ket('psi'))
```

### Tensor Products

```python
from sympy.physics.quantum import TensorProduct

# |psi> ⊗ |phi>
tensor = TensorProduct(Ket('psi'), Ket('phi'))
```

## Quantum Computing

### Qubits

```python
from sympy.physics.quantum.qubit import Qubit, IntQubit

# Create qubit in computational basis
q = Qubit('01')  # |01>
print(q.nqubits)  # 2

# Integer representation
q_int = IntQubit(5, nqubits=3)  # |101> (5 in binary)
print(q_int.qubit_values)  # (1, 0, 1)
```

### Quantum Gates

```python
from sympy.physics.quantum.gate import H, X, Y, Z, CNOT, SWAP

# Hadamard gate
H(0)  # Apply to qubit 0

# Pauli gates
X(1)  # Pauli-X (NOT) on qubit 1
Y(0)  # Pauli-Y
Z(2)  # Pauli-Z

# Two-qubit gates
CNOT(0, 1)  # Control=0, Target=1
SWAP(0, 1)  # Swap qubits 0 and 1
```

### Quantum Circuits

```python
from sympy.physics.quantum.gate import H, CNOT
from sympy.physics.quantum.qapply import qapply

# Create Bell state circuit
q = Qubit('00')
circuit = CNOT(0, 1) * H(0)

# Apply circuit to state
bell_state = qapply(circuit * q)
```

### Famous Quantum Algorithms

#### Grover's Algorithm

```python
from sympy.physics.quantum.grover import apply_grover

# Search in 4-element list
result = apply_grover(00, numqubits=2, iterations=1)
```

#### Quantum Fourier Transform

```python
from sympy.physics.quantum.qft import QFT

# 3-qubit QFT
qft = QFT(0, 3)  # Start qubit=0, count=3
```

## Angular Momentum

### Spin Operators

```python
from sympy.physics.quantum.spin import (
    Jx, Jy, Jz, J2,
    JxKet, JyKet, JzKet
)

# Spin-1/2 state
j, m = sp.Rational(1, 2), sp.Rational(1, 2)
state = JzKet(j, m)  # |1/2, 1/2>

# Apply operators
Jz * state  # m*ħ*state
J2 * state  # j(j+1)*ħ²*state
```

### Clebsch-Gordan Coefficients

```python
from sympy.physics.quantum.cg import CG

# <j1, m1; j2, m2 | j3, m3>
j1, m1 = sp.Rational(1, 2), sp.Rational(1, 2)
j2, m2 = sp.Rational(1, 2), sp.Rational(-1, 2)
j3, m3 = 1, 0

coeff = CG(j1, m1, j2, m2, j3, m3)
print(coeff.doit())
```

## Quantum Harmonic Oscillator

### 1D Harmonic Oscillator

```python
from sympy.physics.quantum.qho_1d import (
    RaisingOp, LoweringOp,
    NumberOp,
    Hamiltonian
)

# Creation/annihilation operators
a_dag = RaisingOp('a')
a = LoweringOp('a')

# Number operator
N = NumberOp('N')

# Hamiltonian
H = Hamiltonian('H')
```

### Energy Eigenstates and Wavefunctions

```python
from sympy.physics.quantum.qho_1d import psi_n

x = sp.Symbol('x', real=True)
m, omega = sp.symbols('m omega', positive=True)

# Ground state wavefunction
psi_0 = psi_n(0, x, m, omega)

# First excited state
psi_1 = psi_n(1, x, m, omega)
```

## Particle in a Box

```python
from sympy.physics.quantum.piab import PIABHamiltonian, PIABKet

# Infinite square well
n = sp.Symbol('n', integer=True, positive=True)
m, L = sp.symbols('m L', positive=True)

# Energy eigenstate
state = PIABKet(n)

# Hamiltonian
H = PIABHamiltonian('H')
energy = H * state  # E_n = n²π²ħ²/(2mL²)
```

## Hydrogen Atom

```python
from sympy.physics.hydrogen import R_nl, Psi_nlm

n, l, m = sp.symbols('n l m', integer=True)
r, theta, phi = sp.symbols('r theta phi', real=True)
Z = sp.Symbol('Z', positive=True)

# Radial wavefunction
R = R_nl(n, l, r, Z)

# Complete wavefunction
psi = Psi_nlm(n, l, m, r, theta, phi, Z)
```

## Pauli Algebra

```python
from sympy.physics.paulialgebra import Pauli

# Pauli matrices
sigma_x = Pauli(1)
sigma_y = Pauli(2)
sigma_z = Pauli(3)

# Pauli algebra
sigma_x * sigma_y  # i*sigma_z
sigma_y * sigma_x  # -i*sigma_z
```

## Second Quantization

```python
from sympy.physics.secondquant import (
    Fd, F,  # Fermionic creation/annihilation
    Bd, B   # Bosonic creation/annihilation
)

# Fermion operators
p, q = sp.symbols('p q', above_fermi=True)
c_dag = Fd(p)
c = F(q)

# Anticommutator
{c, c_dag}  # δ_pq

# Boson operators
a_dag = Bd(p)
a = B(q)

# Commutator
[a, a_dag]  # δ_pq
```

## Quantum Optics

```python
from sympy.physics.quantum.state import Wavefunction
from sympy.physics.quantum.operator import DifferentialOperator

x = sp.Symbol('x', real=True)

# Define wavefunction
psi = Wavefunction(sp.exp(-x**2/2), x)

# Position operator
X = DifferentialOperator(x, x)

# Momentum operator
P = DifferentialOperator(-sp.I * sp.diff(x, x), x)
```

## Representation Theory

### Matrix Representation

```python
from sympy.physics.quantum.represent import represent
from sympy.physics.quantum.spin import Jz

# Get matrix representation of operator
j = sp.Rational(1, 2)
matrix = represent(Jz, j=j)
print(matrix)
# Matrix([[1/2, 0], [0, -1/2]])
```

## Practical Example: Quantum Teleportation

```python
from sympy.physics.quantum.qubit import Qubit
from sympy.physics.quantum.gate import H, CNOT, X, Z
from sympy.physics.quantum.qapply import qapply

# Initial state to teleport
psi = Qubit('0')  # Can be any state

# Create Bell pair
bell_pair = qapply(CNOT(1, 2) * H(1) * Qubit('00'))

# Complete teleportation circuit
# 1. Entangle psi with Bell pair
state = TensorProduct(psi, bell_pair)

# 2. Apply CNOT and Hadamard
state = qapply(H(0) * CNOT(0, 1) * state)

# 3. Measure qubits 0 and 1 (symbolic)
# 4. Apply corrections to qubit 2 based on measurements
```

## Symbolic Quantum Computation

```python
# Define symbolic parameters
alpha, beta = sp.symbols('alpha beta', complex=True)

# Superposition state
state = alpha * Qubit('0') + beta * Qubit('1')

# Normalization condition
norm_condition = sp.Abs(alpha)**2 + sp.Abs(beta)**2 - 1

# Solve for normalized state
solutions = sp.solve(norm_condition, beta)
```

## Time Evolution

```python
from sympy.physics.quantum import Operator

# Time-dependent Schrödinger equation
H = Operator('H')  # Hamiltonian
t = sp.Symbol('t', real=True, positive=True)
hbar = sp.Symbol('hbar', real=True, positive=True)

# Time evolution operator
U = sp.exp(-sp.I * H * t / hbar)

# Evolve state
psi_t = U * Ket('psi')
```

## Best Practices

### 1. Use Symbolic Parameters

```python
# Good - symbolic
n = sp.Symbol('n', integer=True, positive=True)
state = PIABKet(n)

# Works for any n
energy = (n**2 * sp.pi**2) / (2 * m * L**2)
```

### 2. Simplify Quantum Expressions

```python
from sympy.physics.quantum import qsimplify

expr = Commutator(A, B) * Ket('psi')
simplified = qsimplify(expr)
```

### 3. Verify Quantum Identities

```python
# Verify Pauli matrix anticommutation
sigma_x, sigma_y = Pauli(1), Pauli(2)

anticomm = sigma_x * sigma_y + sigma_y * sigma_x
sp.simplify(anticomm)  # Should be 0
```

## Summary

SymPy's quantum module provides:
- Bra-ket notation and Dirac formalism
- Quantum gates and circuits
- Angular momentum and spin
- Quantum harmonic oscillator
- Hydrogen atom
- Second quantization
- Pauli algebra
- Quantum algorithms (Grover, QFT, Shor)

**Key functions:**
- `qapply()`: Apply operators to states
- `qsimplify()`: Simplify quantum expressions
- `represent()`: Get matrix representations
- `Commutator()`, `AntiCommutator()`: Operator algebra
