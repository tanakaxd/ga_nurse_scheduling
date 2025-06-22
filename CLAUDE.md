# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a genetic algorithm-based nurse scheduling system written in Python. The system optimizes shift assignments for healthcare workers based on multiple constraints and preferences including individual work preferences, availability, and operational requirements.

## Initial Setup Requirements

### Required Dependencies
Install the following Python packages:
```bash
pip install matplotlib numpy scikit-learn
```
Standard library modules used: `csv`, `random`, `os`, `sys`, `copy`

### Directory Structure Setup
The application requires the following directory structure:
```
ga_nurse_scheduling/
├── data/
│   ├── _fixed_plot.csv          # Required: Fixed shift assignments
│   ├── charts/                  # Auto-created: Fitness graph outputs
│   ├── schedule_cache.csv       # Optional: Cached best schedule for warm start
│   └── schedule_*.csv           # Auto-generated: Final schedule outputs
```

### Required Configuration Files

#### 1. Fixed Plot Assignment File (`data/_fixed_plot.csv`)
**Critical requirement**: This file must exist before running the application.

Format: CSV with 31 rows (days) × 7 columns (employees), where:
- `X` = No fixed assignment (algorithm decides)
- `A`, `B`, `C`, `E`, `NE` = Fixed shift assignment
- `R` = Fixed rest day

Example structure:
```csv
X,X,X,X,X,X,X
X,X,X,X,X,R,NE
X,X,X,C,X,C,NE
A,X,X,X,X,X,A
```

#### 2. Employee Configuration (`constants.py`)
Modify the `EMPLOYEES` list to match your workforce:
```python
EMPLOYEES = [
    Employee("Name", able_to_cnt, desired_weekly_hours, unavailable_dates, preferences),
    # Add/modify employees as needed
]
```

Where:
- `able_to_cnt`: Number of different shift types employee can handle
- `desired_weekly_hours`: Target weekly work hours  
- `unavailable_dates`: List of dates employee cannot work
- `preferences`: Dictionary of shift preferences (use -100 for impossible assignments)

### Optional Cache System
- Set `LOAD = True` in `constants.py` to load cached schedules for warm start
- Set `SAVE_TO_CACHE = True` to save best results for future runs
- Cache file: `data/schedule_cache.csv` (auto-generated after first successful run)

## Running the Application

- **Main execution**: `python main.py`
- **Output**: Generates schedule CSV files and fitness graphs in `data/` directory
- **Runtime**: Typically 1000 generations with population of 300 (configurable in `constants.py`)

## Core Architecture

The genetic algorithm operates on a population of `Schedule` objects, each representing a complete monthly shift assignment. Key components:

### Core Classes
- **Schedule** (`schedule.py`): Main GA individual containing fitness calculation and genetic operations
  - Manages a list of `Day` objects representing daily shift assignments
  - Implements crossover (`cross()`) and fitness evaluation (`calcFitness()`)
  - Handles CSV import/export for schedule persistence
  
- **Employee** (`employee.py`): Base class for staff members with preferences and constraints
  - Stores shift preferences (`plot_preference`) and desired work frequency
  - Uses MinMaxScaler for preference normalization
  - Extensible through inheritance (see `Shimura` class)

- **Day** (`day.py`): Represents daily shift assignments for all employees
  - Manages shift assignments as `cells` array (A/B/C/E/NE/R for shifts/rest)
  - Handles mutation operations and fixed assignment constraints
  - Implements `fixed_merge_shuffle()` for constraint enforcement

### Genetic Algorithm Parameters
- Population size: 300 individuals (`POP`)
- Generations: 1000 (`NGEN`) 
- Mutation rate: 3% (`MUTPB`)
- Elitism: 1 individual preserved per generation
- Fitness uses weighted multi-objective optimization with 8 criteria

### Data Management
- **Fixed assignments**: Loaded from `_fixed_plot.csv` via `csv_to_dict()` converter
- **Schedule persistence**: Cache system using `schedule_cache.csv`
- **Output**: Saves best schedules and fitness graphs to `data/` directory

## Key Implementation Details

### Fitness Function
The system optimizes 8 weighted objectives in `schedule.py:calcFitness()`:
1. Desired work frequency matching (weight: 50)
2. Shift preference satisfaction using geometric mean (weight: 80) 
3. Individual wish fulfillment (weight: 10)
4. Consecutive shift penalty (weight: 10)
5. Shift variety enforcement (weight: 10)
6. Fixed assignment compliance (weight: 100)

### Constraint Handling
- Fixed shifts enforced through `fixed_merge_shuffle()` during initialization and crossover
- Employee availability handled during schedule generation
- Shift coverage requirements maintained through mandatory shift assignment

### Extensibility
- New employee types via inheritance (see `Shimura` class example)
- Custom fitness criteria through `Employee.wish()` method
- Configurable shift types and preferences in `constants.py`

## Design Principles and Architectural Intentions

### Constraint Handling Philosophy
The system implements a **dual-layer constraint approach** to handle hard constraints:

1. **Initialization-level enforcement**: Fixed schedules applied through `fixed_merge_shuffle()` during object creation
2. **Fitness-level penalties**: Constraint violations penalized in fitness calculation as backup

**Key insight**: Fixed constraints are treated as "infinite fitness" requirements rather than normal optimization objectives, since they represent absolute requirements that cannot be violated.

### Genetic Algorithm Design Decisions

**Crossover Strategy**: Uses an innovative approach where children start as random schedules and are selectively overwritten with parent genes. Non-overwritten portions effectively represent mutation, creating a unified crossover-mutation mechanism.

**Selection Pressure**: Employs squared fitness values for selection probabilities to amplify differences between good and poor solutions, accelerating convergence while maintaining diversity.

**Elitism**: Preserves exactly one elite individual per generation to ensure best solutions are never lost while allowing population exploration.

### Fitness Function Design Rationale

**Multi-objective Optimization**: Implements 8 weighted fitness components with careful consideration of interaction effects:
- Uses **multiplicative evaluation** for shift preferences (geometric mean) to ensure all preferences matter
- Uses **additive penalties** for constraint violations to allow fine-grained control
- **Weight hierarchy**: Fixed constraints (weight: 100) > Preference satisfaction (weight: 80) > Workload balance (weight: 50)

**Utility vs Fairness Trade-off**: Deliberately chose geometric mean over arithmetic mean for preference calculation to prevent one person's high satisfaction from masking another's dissatisfaction.

### Constraint Satisfaction Strategy

**Gender-specific Constraints**: E/NE shifts restricted to female staff through negative preference values (-100) rather than hard exclusions, maintaining algorithmic consistency.

**Workload Distribution**: Monthly rather than weekly evaluation chosen for practical scheduling flexibility while maintaining fairness through consecutive work penalties.

**Shift Coverage**: Ensures minimum one person per shift type through mandatory assignment during day initialization, preventing coverage gaps.

### Extensibility Architecture

**Employee Specialization**: Inheritance-based system allows custom constraint handling (e.g., `Shimura` class implements anti-consecutive-rest preferences).

**Preference Normalization**: Uses MinMaxScaler (0.95-1.01 range) to maintain multiplicative compatibility while preserving preference ordering and avoiding zero-multiplication issues.

**Modular Constraint System**: Individual `wish()` methods allow employee-specific rules without modifying core algorithm.

### Performance and Robustness Considerations

**Zero-fitness Protection**: Ensures fitness never reaches zero to prevent selection algorithm breakdown: `max(sys.float_info.epsilon, total_fitness)`

**Cache Integration**: Supports loading high-quality cached schedules while maintaining population diversity through random initialization of remaining individuals.

**Mutation Rate Philosophy**: Fixed 3% rate chosen as compromise between exploration and exploitation, with architectural support for future adaptive mutation strategies.

## Development Notes

- Comments are primarily in Japanese, reflecting deep algorithmic reasoning and design trade-offs
- The system demonstrates sophisticated understanding of multi-objective optimization challenges in workforce scheduling
- Architecture prioritizes both algorithmic soundness and practical applicability
- Extensive TODO comments indicate planned enhancements for worker compatibility, preference reloading, and constraint system improvements