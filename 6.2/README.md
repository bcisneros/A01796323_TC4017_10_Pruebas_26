# 📘 Activity 6.2 – Reservation System & Validation (Rubric‑Ready)

This README summarizes the work completed for **Activity 6.2**, organized to make evaluation **fast** and **traceable** against the rubric. It includes:

- Overview of the system and requirements coverage
- Exact project structure
- How to lint, test, and inspect coverage (single‑command targets)
- Evidence locations (Pylint, Flake8, Coverage)
- Rubric‑aligned scoring guide (what to check and where)
- Commit discipline (Conventional Commits)

---

## 1) Overview of the Program

The **Reservation System** implements three abstractions and their behaviors:

- **Hotel** — create, display, update, delete, list
- **Customer** — create, display, update, delete, list
- **Reservation** — create, cancel, list

Persistence is a simple **JSON store** with resilience to malformed or missing files (continues execution and logs a message).

An optional **CLI** (`scripts/cli.py`) provides a **Spanish** interactive menu to exercise all features with seeded sample data.

### ✔ Features Implemented (mapping to requirements)

- **Req 1 (Abstractions):** `Hotel`, `Customer`, `Reservation` (domain + service methods)
- **Req 2 (Persistent behaviors in files):**
  - Hotel: create, delete, display, modify, list
  - Customer: create, delete, display, modify, list
  - Reservation: create, cancel, list
- **Req 3 (Unit tests):** comprehensive tests under `tests/` (service tests mock I/O; storage tests hit the filesystem)
- **Req 4 (≥85% coverage):** enforced via `coverage` (see “Evidence & Coverage”)
- **Req 5 (Invalid data tolerance):** malformed JSON handled gracefully (error message + continue)
- **Req 6 (PEP 8):** enforced with Pylint/Flake8
- **Req 7 (Zero warnings):** Pylint & Flake8: **0 findings** (see evidence files)

---

## 2) Project Structure

```
├── Makefile
├── README.md
├── data
│   ├── customers.json
│   ├── hotels.json
│   └── reservations.json
├── pyproject.toml
├── requirements.txt
├── scripts
│   └── cli.py
├── src
│   ├── __init__.py
│   └── reservation
│       ├── __init__.py
│       ├── models.py
│       ├── service.py
│       └── storage.py
└── tests
    ├── __init__.py
    ├── customer_test.py
    ├── hotel_test.py
    ├── reservation_test.py
    └── store_test.py
```

---

## 3) How to Build, Lint, Test, and Inspect Coverage

> **Python:** 3.9+ recommended

**Install (editable):**

```bash
pip install -e .
pip install -r requirements.txt
```

**Lint (PEP8 / Static Analysis)**

```bash
make lint

🔎 Linting with flake8 and pylint...
flake8 src tests
pylint src/reservation tests

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```

**Run Tests + Coverage**

```bash
make cov
🧪 Running unit tests with coverage...
coverage erase
coverage run -m unittest discover -s tests -p "*_test.py" -v
test_create_customer_duplicate_id_raises (customer_test.CustomerTest.test_create_customer_duplicate_id_raises) ... ok
test_create_customer_empty_id_raises (customer_test.CustomerTest.test_create_customer_empty_id_raises) ... ok
...
test_load_missing_file_returns_empty_list (store_test.StoreTest.test_load_missing_file_returns_empty_list) ... ok
test_save_overwrites_existing_file (store_test.StoreTest.test_save_overwrites_existing_file) ... ok
test_save_then_load_round_trip_ok (store_test.StoreTest.test_save_then_load_round_trip_ok) ... ok

----------------------------------------------------------------------
Ran 40 tests in 0.024s

OK
📈 Coverage (text report)
coverage report -m --include="src/*"
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
src/reservation/__init__.py       0      0   100%
src/reservation/service.py      110      0   100%
src/reservation/storage.py       21      0   100%
-----------------------------------------------------------
TOTAL                           131      0   100%

```

**Generate HTML Coverage Report**

```
----------------------------------------------------------------------
Ran 40 tests in 0.024s

OK
🌐 Generating HTML coverage...
coverage html
Wrote HTML report to htmlcov/index.html
Open: htmlcov/index.html
```

**Optional – Run CLI (Spanish Menu):**

```
make demo
Running Demo
python scripts/cli.py

===== Sistema de Reservaciones =====
1. Crear hotel
2. Mostrar hotel
3. Modificar hotel
4. Eliminar hotel
5. Listar hoteles
6. Crear cliente
7. Mostrar cliente
8. Modificar cliente
9. Eliminar cliente
10. Listar clientes
11. Crear reservación
12. Cancelar reservación
13. Listar reservaciones
0. Salir
Selecciona una opción:
```

## 4) Evaluation

### Pylint + PEP8 + Flake

Generate with:

```
make lint
```

![Static Analysis Evidence](./evidences/static_analysis.png)

### Correct Test Case Design (incl. negatives)

#### Strategy

- Service tests are pure unit tests with a catalog‑based mocked store (load returns by filename) and in‑memory persistence after save. This makes tests deterministic and independent of call order.
- Storage tests (``store_test.py) validate the real filesystem behavior of JsonStore.
- Test names are descriptive about its intention and keep small setup and test minimal behavior
- TDD approach was taken to create some of the basic behavior and let the design emerge to facilitate refactoring to avoid repetition or reduce complexity.

#### Happy Paths

- **Hotels**: create new hotels (new id), return one or multiple hotels, update hotel information, remove hotel and display hotel information
- **Customers**: create valid customers, remove customers, return customers by id, update and display customer information
- **Reservations**: make new reservations, cancel reservations
- **Storage**: files can be created and write json content on them

#### Negative scenarios

- **Hotels**: duplicate id, invalid rooms (≤0), empty id, empty name, update not found, invalid rooms on update, empty name on update.
- **Customers**: duplicate id, invalid email (no @), delete not found, update not found
- **Reservations**: hotel not found, customer not found, room out of range (low/high), duplicate reservation id, room already taken, cancel unknown.
- **Storage**: missing file → []; corrupted JSON → logs + []; overwrite existing file.

### Coverage Report

Expected: ≥ 85%

![Coverage Report](./evidences/coverage_report.png)

Generate with:

```
make html
```

Open with:

```
open ./htmlcov/index.html
```

### Conventional Commits

**Quick verification**

```
git log --oneline --decorate --graph --all
```

![Conventional Commits](./evidences/conventional_commits.png)

> Note: I started using conventional commits just in this activity, so the history shows non conventional before that.

## 5) Conclusions

- All functional and technical requirements are satisfied.
- Tests are cleanly layered (service vs storage), deterministic, and include ample negative cases.
- Pylint/Flake8 report zero issues (PEP‑8 compliance).
- Coverage meets or exceeds the 85% rubric threshold; HTML report included.
- Documentation and Makefile targets are provided to streamline evaluation.

### Lessons learned

- Python Test Suite is easy to use and configure, but probably for more complex scenarios is required to use external libraries.
- Small increments of tested functionality increases confidence about adding more complex logic as soon this is discovered.
- Commit often and using conventional messages helps to keep a traceable log of events and is easier to rollback if a step is not the best way to do it.
