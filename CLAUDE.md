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

## Common Issues and Solutions

### Issue 1: Closed Days (Wednesday) Not Preserved Across Generations

**Problem**: Wednesday (closed day) shows work assignments after several generations despite `is_closed_day` flag.

**Root Causes**:
1. **Crossover processing**: `Schedule.cross()` method overwrites closed days with parent data that may contain work assignments
2. **Fixed constraint processing**: `Day.fixed_merge_shuffle()` ignores `is_closed_day` and forces shift assignments even on closed days

**Solution**:
```python
# In schedule.py:cross() - Skip crossover for closed days
if child.days[i].is_closed_day:
    continue

# In day.py:fixed_merge_shuffle() - Skip processing for closed days  
if self.is_closed_day:
    return
```

### Issue 2: Evolution Halts (Generation Updates Stop)

**Problem**: All individuals converge to same near-zero fitness (`sys.float_info.epsilon`), causing evolution to halt.

**Root Cause**: Large negative penalty values (e.g., -1400) in fitness calculation cause `total_fitness` to be negative, which gets clamped to epsilon by `max(sys.float_info.epsilon, total_fitness)`.

**Solution**: Transform negative fitness values to small positive values:
```python
# In schedule.py:calcFitness()
if total_fitness <= 0:
    # Convert negative values to small positive values
    self.fitness = 1.0 / (1.0 + abs(total_fitness))
else:
    self.fitness = total_fitness
```

**Technical Details**:
- Worse schedules (larger negative values) get smaller positive fitness
- Maintains selection pressure while avoiding zero-fitness convergence
- Preserves relative ranking between individuals

### Issue 3: Debugging Evolution Problems

**Diagnostic Steps**:
1. Check `AVERAGE` fitness in output - if all near-zero, fitness transformation issue
2. Verify `Utilities_Fraction` values - large negatives indicate constraint violations
3. Monitor if same schedule prints repeatedly - indicates halted evolution
4. Check water/closed day assignments in output - should remain all 'R'

**Key Monitoring Values**:
- `fitness2` (preference satisfaction): Should use geometric mean, not zero
- `fitness5` (individual wishes): Employee-specific constraints
- `fitness8` (fixed constraints): Heaviest penalty weight (100)

## Data Format and Field Definitions

### Schedule CSV Structure
The original schedule files use a specific format with paired columns for each employee:

**Column Structure**: `[日付, 曜日, 員工名1, メガネ割当1, 員工名2, メガネ割当2, ..., 備考, cnt, vld, メガネ]`

### Field Definitions
- **Alphabet (A, B, C, E, NE)**: 清掃区画の割当 (Cleaning area assignments)
  - Each cleaning area must be assigned to exactly one person per day (with education day exceptions)
  - If assigned a cleaning area → employee is working that day
- **Numbers (1-5)**: メガネコーナーの割当番号 (Glasses corner assignment numbers)  
  - 5 people are assigned unique numbers 1-5 each day
  - Only assigned to employees who are working (have cleaning assignments)
- **'休'**: Rest day (no assignments)
- **'C/D'**: Special cleaning assignment notation

### Assignment Rules for Restoration
1. **Cleaning area assignment** → **Employee is working** → **Requires glasses corner number**
2. **No cleaning assignment** → **Employee is resting** → **No glasses corner number**
3. **Numbers 1-5 must be uniquely distributed** among working employees
4. **Cleaning areas A,B,C,E,NE must be assigned** (except during education days)

### Complete Workflow: Transform → GA Optimization → Restore

#### 1. Forward Transform (`transform_schedule_with_metadata()`)
- **Input**: Original Japanese schedule CSV with all metadata
- **Process**: Extract only cleaning assignments (A,B,C,E,NE,R) for GA processing
- **Output**: Simplified CSV + metadata JSON (preserving all lost information)
- **Purpose**: Prepare data for genetic algorithm optimization

#### 2. GA Optimization (`main.py`)
- **Input**: Simplified CSV with cleaning assignments only
- **Process**: Genetic algorithm optimizes shift assignments based on:
  - Employee preferences and constraints
  - Workload distribution
  - Operational requirements
- **Output**: **NEW optimized** cleaning assignments
- **Important**: GA modifies the cleaning assignments - this is the core optimization

#### 3. Reverse Transform (`perfect_inverse_transform_improved()`)
- **Input**: GA-optimized CSV + original metadata JSON
- **Process**: 
  - Use **NEW optimized cleaning assignments** (not original ones)
  - Reconstruct glasses corner numbers (1-5) based on who is working
  - Restore all other metadata (dates, remarks, etc.) from JSON
- **Output**: Complete Japanese schedule with optimized assignments
- **Validation**: Ensure glasses number uniqueness and work status consistency

#### Key Principle
**The cleaning assignments in the final output reflect GA optimization results, not original assignments. Only supporting metadata (dates, structure, etc.) is restored from the original file.**