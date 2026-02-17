# Project 2 - CSP - NQueens

Project by: Omar Imamverdiyev  
Peer Reviewed by: Mehriban Aliyeva

## Overview
This project solves the N-Queens problem on an `n x n` board using a CSP-based iterative search approach.
The main solver is implemented for the assignment workflow and is designed for `10 <= n <= 1000`.

## Assignment Requirement Coverage

### 1. Solve N-Queens on an `n x n` grid
- Implemented in the project solver pipeline:
  - `main.py`
  - `nqueens/csp.py`
  - `nqueens/min_conflicts.py`

### 2. Start with a random board, one queen in each column
- Project solver always starts from a fresh random permutation board.
- A permutation guarantees exactly one queen per column.
- Implemented in:
  - `nqueens/csp.py` (project solver initialization)
  - `nqueens/csp_state.py` (random permutation board support)

### 3. Use iterative search algorithm
- Implemented as an iterative min-conflicts style local search with plateau escape and restarts.
- Implemented in:
  - `nqueens/min_conflicts.py`

### 4. Constraints: `10 <= n <= 1000`
- Enforced at runtime in:
  - `main.py`

### 5. Input format support
- Input file format: one integer per line, where line `i` gives the column for row `i`.
- Supports comments (`# ...`) and blank lines.
- Validates board values are within range and form a permutation of `0..n-1`.
- Implemented in:
  - `nqueens/io_utils.py`

### 6. CSP algorithm components
- Search algorithm:
  - Iterative local search over board assignments (`nqueens/min_conflicts.py`).
- Heuristics:
  - MRV-style row selection from propagated domains.
  - LCV value ordering for candidate column moves.
  - Deterministic tie-breaking.
- Constraint propagation:
  - AC-3 propagation over active row domains.
  - Implemented in:
    - `nqueens/min_conflicts.py`
    - `nqueens/ac3.py`

## Project Structure
- `main.py`: CLI entry point, input loading, constraint check for `n`.
- `nqueens/csp.py`: CSP wrapper and project-solver orchestration.
- `nqueens/csp_state.py`: Board state and O(1) conflict counters.
- `nqueens/min_conflicts.py`: Iterative CSP search (MRV/LCV/tie-break, AC-3-guided domains, restarts).
- `nqueens/ac3.py`: AC-3 constraint propagation primitives.
- `nqueens/io_utils.py`: Input parsing and validation.
- `nqueens/utils.py`: Solution validation helper.
- `generate_nqueens.py`: Input generator utilities.

## How To Run
Run with sample input:
```bash
python main.py .\test1.txt
```

Run with a higher step limit:
```bash
python main.py .\test1.txt --max-steps 300000
```

## Input Generator
Generate test files:
```bash
python generate_nqueens.py <n> <output_file> [--random | --easy | --solution | --hard-diagonal | --hard-anti]
```

Examples:
```bash
python generate_nqueens.py 20 test1.txt --easy
python generate_nqueens.py 1000 test1.txt --random
```

## Notes
- The project solver is stochastic; different runs may take different numbers of steps.
- For larger `n` (for example `n=1000`), increase `--max-steps` if needed.
