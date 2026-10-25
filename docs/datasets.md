# SocraCode: Bug Taxonomy & Dataset Generation Strategy

SocraCode does not use any third-party pre-trained models or commercial LLMs. Classification models must be trained from scratch on synthetic datasets generated via deterministic bug injection into clean reference programs.

---

## 1. The 8 Shared Bug Categories

| ID | Category Name | Description | Example Pattern |
|---|---|---|---|
| `syntax_error` | Syntax Error | Missing colons, unbalanced brackets/parentheses, bad indentation. | `for i in range(10)` (missing `:`) |
| `undefined_name` | Undefined Name / Variable | Using a variable or function name before declaration or typo in identifier. | `total = toatl + 1` |
| `type_error` | Type Incompatibility | Incompatible operand types or invalid operations on types. | `'Count: ' + 5` |
| `index_out_of_range` | Index / Off-by-One | Array/list indexing past bounds or off-by-one loop limits. | `items[len(items)]` |
| `wrong_operator` | Wrong Operator / Condition | Incorrect comparison (`>` instead of `<`), assignment in condition (`=` vs `==`). | `if score = 100:` |
| `missing_return` | Missing Return Value | Function computes a result but fails to return it, yielding `None`. | `def add(a, b): res = a + b` |
| `loop_boundary` | Loop Boundary / Infinite Loop | While loops without progress steps, incorrect increment or range steps. | `while i < n: print(i)` (no increment) |
| `wrong_variable` | Variable Shadowing / Misuse | Passing or using the wrong variable in a calculation or loop. | `for x in row: total += y` |

---

## 2. Dataset Generation Mechanics

Synthetic buggy programs are synthesized through Python Abstract Syntax Tree (`ast`) and token-level mutations applied to correct Python algorithms:
1. **Source Corpus**: Correct implementations of common introductory programming problems (loops, math, string manipulation, list processing).
2. **Mutators**:
   - `ColonRemover`: Strips terminal colons from header statements (`def`, `for`, `while`, `if`).
   - `OffByOneMutator`: Alters range stop values (`range(len(arr) + 1)`).
   - `VariableTypoMutator`: Swaps or typos identifier characters in expressions.
   - `OperatorSwapper`: Inverts comparison operators (`<` -> `>`, `==` -> `!=`).
   - `ReturnStripper`: Drops the `return` statement from fruit-bearing functions.
3. **Data Splitting**:
   - Training Set: Generated program mutations (thousands of instances).
   - Validation Set: Independent synthetic mutations.
   - Held-out Test Set: Hand-crafted student code snippets never seen in training, representing real classroom exercises.
