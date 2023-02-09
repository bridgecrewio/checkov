---
id: gm0ti
name: Creating a Solver
file_version: 1.0.2
app_version: 0.9.4-0
file_blobs:
  checkov/common/checks_infra/solvers/complex_solvers/not_solver.py: 60e9301de2a35a51b0464babaf537104d82cf00a
  checkov/common/checks_infra/checks_parser.py: 50130edc6639275b43dbd287572972b826eee687
  checkov/common/checks_infra/solvers/complex_solvers/__init__.py: 2e25b8e1f51406fe5e2995019eb6046fdf3650f2
  checkov/common/graph/checks_infra/solvers/base_solver.py: e84d471f6fc2e8ef12d82fa061784c57a7915d5c
  checkov/common/checks_infra/solvers/complex_solvers/base_complex_solver.py: 186dd8805259132d32936fafc19c389d452869c4
  checkov/common/checks_infra/solvers/connections_solvers/or_connection_solver.py: 38df2db8112768f7ee10facc3feac82b84affc32
  checkov/common/checks_infra/solvers/attribute_solvers/any_attribute_solver.py: 5aa38478ce1174ea46d2cff94ec52358e8595369
  checkov/common/checks_infra/solvers/attribute_solvers/not_contains_attribute_solver.py: 0d44d643a7ba2f1fc78fa86ad53b46c47e546ee1
  checkov/common/checks_infra/solvers/attribute_solvers/not_ending_with_attribute_solver.py: 334cc79488dc5f5f52e3d66ef9b24e3ad89f1e99
---

A Solver is a major component in our system. This document will describe what it is and how to add a new one.

A Solver is a graph operator that impelements a certain piece of logic, such as AttributeEquals, GreaterThan, Exists and more. There are also more complext solvers such as the `And` solver which implement logic between two or more solvers

When we add a new Solver, we create a class that inherits from `BaseSolver`[<sup id="2wxET6">↓</sup>](#f-2wxET6).

Some examples of `BaseSolver`[<sup id="2wxET6">↓</sup>](#f-2wxET6)s are `OrConnectionSolver`[<sup id="Z1oapTp">↓</sup>](#f-Z1oapTp), `AnyResourceSolver`[<sup id="Z7ghIg">↓</sup>](#f-Z7ghIg), `NotContainsAttributeSolver`[<sup id="Z136myH">↓</sup>](#f-Z136myH), and `NotEndingWithAttributeSolver`[<sup id="923Qq">↓</sup>](#f-923Qq). Note: some of these examples inherit indirectly from `BaseSolver`[<sup id="2wxET6">↓</sup>](#f-2wxET6).

> **NOTE: Inherit from** `BaseComplexSolver`[<sup id="10523X">↓</sup>](#f-10523X)
> 
> Most `BaseSolver`[<sup id="2wxET6">↓</sup>](#f-2wxET6)s inherit directly from `BaseComplexSolver`[<sup id="10523X">↓</sup>](#f-10523X) and almost none inherit directly from `BaseSolver`[<sup id="2wxET6">↓</sup>](#f-2wxET6). In this document we demonstrate inheriting from `BaseComplexSolver`[<sup id="10523X">↓</sup>](#f-10523X).

## TL;DR - How to Add a `BaseComplexSolver`[<sup id="10523X">↓</sup>](#f-10523X)

1.  Create a new class inheriting from `BaseComplexSolver`[<sup id="10523X">↓</sup>](#f-10523X) 
    
    *   Place the file under `📄 checkov/common/checks_infra/solvers/complex_solvers`, e.g. `NotSolver`[<sup id="Z2wW09R">↓</sup>](#f-Z2wW09R) is defined in `📄 checkov/common/checks_infra/solvers/complex_solvers/not_solver.py`.
        
2.  Define `operator`[<sup id="Z1HozjT">↓</sup>](#f-Z1HozjT).
    
3.  Implement `__init__`[<sup id="ZDc3b7">↓</sup>](#f-ZDc3b7), `_get_operation`[<sup id="Z1IWbj3">↓</sup>](#f-Z1IWbj3), and `get_operation`[<sup id="I3t5K">↓</sup>](#f-I3t5K).
    
4.  Update `📄 checkov/common/checks_infra/checks_parser.py`.
    
5.  Update `📄 checkov/common/checks_infra/solvers/complex_solvers/__init__.py`.
    
6.  **Profit** 💰
    

## Example Walkthrough - `NotSolver`[<sup id="Z2wW09R">↓</sup>](#f-Z2wW09R)

We'll follow the implementation of `NotSolver`[<sup id="Z2wW09R">↓</sup>](#f-Z2wW09R) for this example.

A `NotSolver`[<sup id="Z2wW09R">↓</sup>](#f-Z2wW09R) is a solver that inverts the logic of the solvers within it

## Steps to Adding a new `BaseComplexSolver`[<sup id="10523X">↓</sup>](#f-10523X)

### 1\. Inherit from `BaseComplexSolver`[<sup id="10523X">↓</sup>](#f-10523X).

All `BaseComplexSolver`[<sup id="10523X">↓</sup>](#f-10523X)s are defined in files under `📄 checkov/common/checks_infra/solvers/complex_solvers`.

<br/>

We first need to define our class in the relevant file, and inherit from `BaseComplexSolver`[<sup id="10523X">↓</sup>](#f-10523X):
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 checkov/common/checks_infra/solvers/complex_solvers/not_solver.py
```python
⬜ 5      from checkov.common.checks_infra.solvers.complex_solvers.base_complex_solver import BaseComplexSolver
⬜ 6      
⬜ 7      
🟩 8      class NotSolver(BaseComplexSolver):
⬜ 9          operator = Operators.NOT  # noqa: CCE003  # a static attribute
⬜ 10     
⬜ 11         def __init__(self, solvers: List[BaseSolver], resource_types: List[str]) -> None:
```

<br/>

> **Note**: the class name should end with "Solver".

### 2\. Define `operator`[<sup id="Z1HozjT">↓</sup>](#f-Z1HozjT)

`BaseSolver`[<sup id="2wxET6">↓</sup>](#f-2wxET6)s should define this variable:

*   `operator`[<sup id="Z1HozjT">↓</sup>](#f-Z1HozjT)

<br/>



<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 checkov/common/checks_infra/solvers/complex_solvers/not_solver.py
```python
⬜ 6      
⬜ 7      
⬜ 8      class NotSolver(BaseComplexSolver):
🟩 9          operator = Operators.NOT  # noqa: CCE003  # a static attribute
⬜ 10     
⬜ 11         def __init__(self, solvers: List[BaseSolver], resource_types: List[str]) -> None:
⬜ 12             if len(solvers) != 1:
```

<br/>

### 3\. Implement `__init__`[<sup id="ZDc3b7">↓</sup>](#f-ZDc3b7), `_get_operation`[<sup id="Z1IWbj3">↓</sup>](#f-Z1IWbj3), and `get_operation`[<sup id="I3t5K">↓</sup>](#f-I3t5K)

Here is how we do it for `NotSolver`[<sup id="Z2wW09R">↓</sup>](#f-Z2wW09R):

Implement `__init__`[<sup id="ZDc3b7">↓</sup>](#f-ZDc3b7).

<br/>



<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 checkov/common/checks_infra/solvers/complex_solvers/not_solver.py
```python
⬜ 8      class NotSolver(BaseComplexSolver):
⬜ 9          operator = Operators.NOT  # noqa: CCE003  # a static attribute
⬜ 10     
🟩 11         def __init__(self, solvers: List[BaseSolver], resource_types: List[str]) -> None:
🟩 12             if len(solvers) != 1:
🟩 13                 raise Exception('The "not" operator must have exactly one child')
🟩 14             super().__init__(solvers, resource_types)
⬜ 15     
⬜ 16         def _get_operation(self, *args: Any, **kwargs: Any) -> Any:
⬜ 17             if len(args) != 1:
```

<br/>



<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 checkov/common/checks_infra/solvers/complex_solvers/not_solver.py
```python
⬜ 13                 raise Exception('The "not" operator must have exactly one child')
⬜ 14             super().__init__(solvers, resource_types)
⬜ 15     
🟩 16         def _get_operation(self, *args: Any, **kwargs: Any) -> Any:
🟩 17             if len(args) != 1:
🟩 18                 raise Exception('The "not" operator must have exactly one child')
🟩 19             return not args[0]
⬜ 20     
⬜ 21         def get_operation(self, vertex: Dict[str, Any]) -> bool:  # type:ignore[override]
⬜ 22             return not self.solvers[0].get_operation(vertex)
```

<br/>



<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 checkov/common/checks_infra/solvers/complex_solvers/not_solver.py
```python
⬜ 18                 raise Exception('The "not" operator must have exactly one child')
⬜ 19             return not args[0]
⬜ 20     
🟩 21         def get_operation(self, vertex: Dict[str, Any]) -> bool:  # type:ignore[override]
🟩 22             return not self.solvers[0].get_operation(vertex)
⬜ 23     
```

<br/>

## Update additional files with the new class

Every time we add new `BaseComplexSolver`[<sup id="10523X">↓</sup>](#f-10523X)s, we reference them in a few locations.

We will still look at `NotSolver`[<sup id="Z2wW09R">↓</sup>](#f-Z2wW09R) as our example.

<br/>

4\. Update `📄 checkov/common/checks_infra/checks_parser.py`, as we do with `NotSolver`[<sup id="Z2wW09R">↓</sup>](#f-Z2wW09R) here:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 checkov/common/checks_infra/checks_parser.py
```python
⬜ 19         NotEndingWithAttributeSolver,
⬜ 20         AndSolver,
⬜ 21         OrSolver,
🟩 22         NotSolver,
⬜ 23         ConnectionExistsSolver,
⬜ 24         ConnectionNotExistsSolver,
⬜ 25         AndConnectionSolver,
```

<br/>

In addition, in the same file:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 checkov/common/checks_infra/checks_parser.py
```python
⬜ 93     operators_to_complex_solver_classes: dict[str, Type[BaseComplexSolver]] = {
⬜ 94         "and": AndSolver,
⬜ 95         "or": OrSolver,
🟩 96         "not": NotSolver,
⬜ 97     }
⬜ 98     
⬜ 99     operator_to_connection_solver_classes: dict[str, Type[BaseConnectionSolver]] = {
```

<br/>

4\. We modify `📄 checkov/common/checks_infra/solvers/complex_solvers/__init__.py`, for example:
<!-- NOTE-swimm-snippet: the lines below link your snippet to Swimm -->
### 📄 checkov/common/checks_infra/solvers/complex_solvers/__init__.py
```python
⬜ 1      from checkov.common.checks_infra.solvers.complex_solvers.or_solver import OrSolver  # noqa
⬜ 2      from checkov.common.checks_infra.solvers.complex_solvers.and_solver import AndSolver  # noqa
🟩 3      from checkov.common.checks_infra.solvers.complex_solvers.not_solver import NotSolver  # noqa
⬜ 4      
```

<br/>

<!-- THIS IS AN AUTOGENERATED SECTION. DO NOT EDIT THIS SECTION DIRECTLY -->
### Swimm Note

<span id="f-ZDc3b7">__init__</span>[^](#ZDc3b7) - "checkov/common/checks_infra/solvers/complex_solvers/not_solver.py" L11
```python
    def __init__(self, solvers: List[BaseSolver], resource_types: List[str]) -> None:
```

<span id="f-Z1IWbj3">_get_operation</span>[^](#Z1IWbj3) - "checkov/common/checks_infra/solvers/complex_solvers/not_solver.py" L16
```python
    def _get_operation(self, *args: Any, **kwargs: Any) -> Any:
```

<span id="f-Z7ghIg">AnyResourceSolver</span>[^](#Z7ghIg) - "checkov/common/checks_infra/solvers/attribute_solvers/any_attribute_solver.py" L7
```python
class AnyResourceSolver(BaseAttributeSolver):
```

<span id="f-10523X">BaseComplexSolver</span>[^](#10523X) - "checkov/common/checks_infra/solvers/complex_solvers/base_complex_solver.py" L9
```python
class BaseComplexSolver(BaseSolver):
```

<span id="f-2wxET6">BaseSolver</span>[^](#2wxET6) - "checkov/common/graph/checks_infra/solvers/base_solver.py" L9
```python
class BaseSolver:
```

<span id="f-I3t5K">get_operation</span>[^](#I3t5K) - "checkov/common/checks_infra/solvers/complex_solvers/not_solver.py" L21
```python
    def get_operation(self, vertex: Dict[str, Any]) -> bool:  # type:ignore[override]
```

<span id="f-Z136myH">NotContainsAttributeSolver</span>[^](#Z136myH) - "checkov/common/checks_infra/solvers/attribute_solvers/not_contains_attribute_solver.py" L7
```python
class NotContainsAttributeSolver(ContainsAttributeSolver):
```

<span id="f-923Qq">NotEndingWithAttributeSolver</span>[^](#923Qq) - "checkov/common/checks_infra/solvers/attribute_solvers/not_ending_with_attribute_solver.py" L7
```python
class NotEndingWithAttributeSolver(EndingWithAttributeSolver):
```

<span id="f-Z2wW09R">NotSolver</span>[^](#Z2wW09R) - "checkov/common/checks_infra/solvers/complex_solvers/not_solver.py" L8
```python
class NotSolver(BaseComplexSolver):
```

<span id="f-Z1HozjT">operator</span>[^](#Z1HozjT) - "checkov/common/checks_infra/solvers/complex_solvers/not_solver.py" L9
```python
    operator = Operators.NOT  # noqa: CCE003  # a static attribute
```

<span id="f-Z1oapTp">OrConnectionSolver</span>[^](#Z1oapTp) - "checkov/common/checks_infra/solvers/connections_solvers/or_connection_solver.py" L11
```python
class OrConnectionSolver(ComplexConnectionSolver):
```

<br/>

This file was generated by Swimm. [Click here to view it in the app](https://app.swimm.io/repos/Z2l0aHViJTNBJTNBY2hlY2tvdiUzQSUzQWJyaWRnZWNyZXdpbw==/docs/gm0ti).