# LaTeX Math Symbols Cheatsheet for Manim

Quick reference for mathematical notation in `MathTex()` and `Tex()`.

## Basic Usage

```python
# Math mode (automatic in MathTex)
MathTex(r"\frac{a}{b}")

# Mixed text and math in Tex
Tex(r"The value is $x = 5$")
```

**Always use raw strings:** `r"..."` to avoid escape issues.

## Greek Letters

| Lowercase | LaTeX | Uppercase | LaTeX |
|-----------|-------|-----------|-------|
| α | `\alpha` | Α | `A` |
| β | `\beta` | Β | `B` |
| γ | `\gamma` | Γ | `\Gamma` |
| δ | `\delta` | Δ | `\Delta` |
| ε | `\epsilon` | Ε | `E` |
| ζ | `\zeta` | Ζ | `Z` |
| η | `\eta` | Η | `H` |
| θ | `\theta` | Θ | `\Theta` |
| ι | `\iota` | Ι | `I` |
| κ | `\kappa` | Κ | `K` |
| λ | `\lambda` | Λ | `\Lambda` |
| μ | `\mu` | Μ | `M` |
| ν | `\nu` | Ν | `N` |
| ξ | `\xi` | Ξ | `\Xi` |
| π | `\pi` | Π | `\Pi` |
| ρ | `\rho` | Ρ | `P` |
| σ | `\sigma` | Σ | `\Sigma` |
| τ | `\tau` | Τ | `T` |
| φ | `\phi` | Φ | `\Phi` |
| χ | `\chi` | Χ | `X` |
| ψ | `\psi` | Ψ | `\Psi` |
| ω | `\omega` | Ω | `\Omega` |

Variants: `\varepsilon`, `\vartheta`, `\varphi`, `\varsigma`

## Operators

### Binary Operators
| Symbol | LaTeX |
|--------|-------|
| × | `\times` |
| ÷ | `\div` |
| ± | `\pm` |
| ∓ | `\mp` |
| · | `\cdot` |
| ∗ | `\ast` |
| ⊕ | `\oplus` |
| ⊗ | `\otimes` |

### Relations
| Symbol | LaTeX |
|--------|-------|
| ≤ | `\leq` or `\le` |
| ≥ | `\geq` or `\ge` |
| ≠ | `\neq` |
| ≈ | `\approx` |
| ≡ | `\equiv` |
| ∼ | `\sim` |
| ∝ | `\propto` |
| ≪ | `\ll` |
| ≫ | `\gg` |
| ⊂ | `\subset` |
| ⊃ | `\supset` |
| ⊆ | `\subseteq` |
| ⊇ | `\supseteq` |
| ∈ | `\in` |
| ∉ | `\notin` |
| ∋ | `\ni` |

## Fractions & Roots

```latex
\frac{a}{b}           % Fraction a/b
\dfrac{a}{b}          % Display-style fraction (larger)
\tfrac{a}{b}          % Text-style fraction (smaller)
\cfrac{a}{b}          % Continued fraction

\sqrt{x}              % Square root
\sqrt[n]{x}           % nth root
\sqrt[3]{x}           % Cube root
```

## Superscripts & Subscripts

```latex
x^2                   % Superscript
x_i                   % Subscript
x^{2n}                % Multi-char superscript
x_{ij}                % Multi-char subscript
x_i^2                 % Both
{}^{14}_6\text{C}     % Isotope notation
```

## Sums, Products, Integrals

```latex
\sum_{i=1}^{n} x_i           % Sum
\prod_{i=1}^{n} x_i          % Product
\int_{a}^{b} f(x)\,dx        % Integral
\iint f(x,y)\,dx\,dy         % Double integral
\iiint f\,dV                 % Triple integral
\oint f\,ds                  % Contour integral
\lim_{x \to \infty}          % Limit
\bigcup_{i=1}^{n} A_i        % Union
\bigcap_{i=1}^{n} A_i        % Intersection
```

## Brackets & Delimiters

```latex
(x)                   % Parentheses
[x]                   % Brackets
\{x\}                 % Braces (curly)
|x|                   % Absolute value
\|x\|                 % Norm
\langle x \rangle     % Angle brackets
\lfloor x \rfloor     % Floor
\lceil x \rceil       % Ceiling

% Auto-sizing
\left( \frac{a}{b} \right)
\left[ \frac{a}{b} \right]
\left\{ \frac{a}{b} \right\}
\left| \frac{a}{b} \right|
```

## Matrices

```latex
% Basic matrix
\begin{matrix}
a & b \\
c & d
\end{matrix}

% With parentheses
\begin{pmatrix}
a & b \\
c & d
\end{pmatrix}

% With brackets
\begin{bmatrix}
a & b \\
c & d
\end{bmatrix}

% With braces
\begin{Bmatrix}
a & b \\
c & d
\end{Bmatrix}

% With vertical bars (determinant)
\begin{vmatrix}
a & b \\
c & d
\end{vmatrix}

% Double vertical bars
\begin{Vmatrix}
a & b \\
c & d
\end{Vmatrix}
```

## Calculus

```latex
\frac{d}{dx}f(x)              % Derivative
\frac{\partial f}{\partial x}  % Partial derivative
\nabla f                       % Gradient
\nabla \cdot \vec{F}           % Divergence
\nabla \times \vec{F}          % Curl
\Delta f                       % Laplacian
f'(x), f## Arrows

```latex
\rightarrow or \to         % →
\leftarrow or \gets        % ←
\leftrightarrow            % ↔
\Rightarrow                % ⇒
\Leftarrow                 % ⇐
\Leftrightarrow            % ⇔
\mapsto                    % ↦
\uparrow                   % ↑
\downarrow                 % ↓
\nearrow                   % ↗
\searrow                   % ↘
\xrightarrow{text}         % Long arrow with text
\xleftarrow{text}          % Long arrow with text
```

## Sets & Logic

```latex
\emptyset                  % Empty set ∅
\mathbb{N}                 % Natural numbers ℕ
\mathbb{Z}                 % Integers ℤ
\mathbb{Q}                 % Rationals ℚ
\mathbb{R}                 % Real numbers ℝ
\mathbb{C}                 % Complex numbers ℂ
\forall                    % For all ∀
\exists                    % Exists ∃
\nexists                   % Not exists ∄
\land                      % Logical and ∧
\lor                       % Logical or ∨
\neg                       % Negation ¬
\therefore                 % Therefore ∴
\because                   % Because ∵
```

## Accents & Decorations

```latex
\hat{a}                    % â (hat)
\bar{a}                    % ā (bar)
\tilde{a}                  % ã (tilde)
\vec{a}                    % a⃗ (vector)
\dot{a}                    % ȧ (dot)
\ddot{a}                   % ä (double dot)
\overline{abc}             % Overline
\underline{abc}            % Underline
\widehat{abc}              % Wide hat
\widetilde{abc}            % Wide tilde
\overrightarrow{AB}        % Vector from A to B
\overbrace{abc}^{text}     % Overbrace
\underbrace{abc}_{text}    % Underbrace
```

## Functions

```latex
\sin, \cos, \tan           % Trig functions
\arcsin, \arccos, \arctan  % Inverse trig
\sinh, \cosh, \tanh        % Hyperbolic
\log, \ln, \lg             % Logarithms
\exp                       % Exponential
\min, \max                 % Min/Max
\sup, \inf                 % Supremum/Infimum
\det                       % Determinant
\dim                       % Dimension
\ker                       % Kernel
\gcd                       % GCD
\Pr                        % Probability
```

## Spacing

```latex
a\,b                       % Thin space
a\:b                       % Medium space
a\;b                       % Thick space
a\ b                       % Normal space
a\quad b                   % Quad space
a\qquad b                  % Double quad space
a\!b                       % Negative thin space
```

## Text in Math

```latex
\text{some text}           % Normal text
\mathrm{text}              % Roman (upright)
\mathit{text}              % Italic
\mathbf{text}              % Bold
\mathsf{text}              % Sans-serif
\mathtt{text}              % Typewriter
\mathcal{ABC}              % Calligraphic
\mathfrak{ABC}             % Fraktur
\mathbb{ABC}               % Blackboard bold
```

## Common Equations

```latex
% Quadratic formula
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}

% Euler's identity
e^{i\pi} + 1 = 0

% Pythagorean theorem
a^2 + b^2 = c^2

% Einstein's mass-energy
E = mc^2

% Maxwell's equations (one of them)
\nabla \times \vec{E} = -\frac{\partial \vec{B}}{\partial t}

% Taylor series
f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!}(x-a)^n

% Gaussian integral
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}

% Binomial coefficient
\binom{n}{k} = \frac{n!}{k!(n-k)!}
```

## Manim-Specific Tips

### Isolating Subexpressions

```python
# Use {{ }} to isolate parts for coloring/transforming
eq = MathTex(r"{{ a }}^2 + {{ b }}^2 = {{ c }}^2")
eq.set_color_by_tex("a", RED)
eq.set_color_by_tex("b", BLUE)
```

### Multi-part Equations

```python
# Pass multiple strings for better control
eq = MathTex("a^2", "+", "b^2", "=", "c^2")
eq[0].set_color(RED)  # a^2
eq[2].set_color(BLUE)  # b^2
```

### Aligned Equations

```python
# align* environment (default in MathTex)
aligned = MathTex(
    r"f(x) &= x^2 + 2x + 1 \\",
    r"&= (x+1)^2"
)
```
