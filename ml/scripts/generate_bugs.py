"""
SocraCode Bug Injection Generator (Step 1).
Introduces controlled synthetic bugs into clean Python reference programs
to generate training examples for bug category classification.
"""

import os
import json
import random
from typing import Dict, List, Optional, Tuple


class BugInjector:
    """Injects syntax and semantic bugs into clean Python programs."""

    def __init__(self, seed: Optional[int] = 42):
        if seed is not None:
            random.seed(seed)

    def inject_missing_colon(self, code: str) -> Tuple[str, str, int]:
        """Removes a colon from a control statement (if, for, while, def)."""
        lines = code.splitlines()
        candidate_indices = [
            i
            for i, line in enumerate(lines)
            if line.rstrip().endswith(":")
            and any(
                line.strip().startswith(kw)
                for kw in ("if ", "elif ", "else:", "for ", "while ", "def ", "class ")
            )
        ]
        if not candidate_indices:
            return code, "syntax_error", 1

        target_idx = random.choice(candidate_indices)
        orig_line = lines[target_idx]
        lines[target_idx] = orig_line.rstrip()[:-1]
        return "\n".join(lines), "syntax_error", target_idx + 1

    def inject_off_by_one(self, code: str) -> Tuple[str, str, int]:
        """Mutates range(len(...)) or range(n) to introduce an off-by-one boundary."""
        lines = code.splitlines()
        candidate_indices = [
            i for i, line in enumerate(lines) if "range(" in line
        ]
        if not candidate_indices:
            return code, "index_out_of_range", 1

        target_idx = random.choice(candidate_indices)
        lines[target_idx] = lines[target_idx].replace("range(", "range(1, ")
        return "\n".join(lines), "index_out_of_range", target_idx + 1

    def inject_undefined_name(self, code: str) -> Tuple[str, str, int]:
        """Introduces an identifier typo in a variable access."""
        lines = code.splitlines()
        candidate_indices = [
            i for i, line in enumerate(lines) if "=" in line and not line.strip().startswith("#")
        ]
        if not candidate_indices:
            return code, "undefined_name", 1

        target_idx = random.choice(candidate_indices)
        line = lines[target_idx]
        words = [w for w in line.replace("=", " ").split() if w.isidentifier()]
        if words:
            typo_word = random.choice(words)
            mutated_word = typo_word + "_typo"
            lines[target_idx] = line.replace(typo_word, mutated_word, 1)
        return "\n".join(lines), "undefined_name", target_idx + 1

    def inject_wrong_operator(self, code: str) -> Tuple[str, str, int]:
        """Swaps comparison operators (e.g. > to < or == to !=)."""
        lines = code.splitlines()
        candidate_indices = [
            i for i, line in enumerate(lines) if " > " in line or " < " in line or " == " in line
        ]
        if not candidate_indices:
            return code, "wrong_operator", 1

        target_idx = random.choice(candidate_indices)
        line = lines[target_idx]
        if " > " in line:
            lines[target_idx] = line.replace(" > ", " < ", 1)
        elif " < " in line:
            lines[target_idx] = line.replace(" < ", " > ", 1)
        elif " == " in line:
            lines[target_idx] = line.replace(" == ", " != ", 1)
        return "\n".join(lines), "wrong_operator", target_idx + 1

    def inject_missing_return(self, code: str) -> Tuple[str, str, int]:
        """Comments out the return statement from a function."""
        lines = code.splitlines()
        candidate_indices = [
            i for i, line in enumerate(lines) if line.strip().startswith("return ")
        ]
        if not candidate_indices:
            return code, "missing_return", 1

        target_idx = random.choice(candidate_indices)
        lines[target_idx] = lines[target_idx].replace("return ", "# return ")
        return "\n".join(lines), "missing_return", target_idx + 1
    def inject_missing_semicolon(self, code: str) -> Tuple[str, str, int]:
        """Removes a semicolon from a Java or C++ statement."""
        lines = code.splitlines()
        candidates = [
            i for i, line in enumerate(lines)
            if line.rstrip().endswith(";") and not line.strip().startswith("//")
        ]
        if not candidates:
            return code, "syntax_error", 1
        target_idx = random.choice(candidates)
        lines[target_idx] = lines[target_idx].rstrip()[:-1]
        return "\n".join(lines), "syntax_error", target_idx + 1

    def mutate_program(self, code: str, language: str = "python") -> Dict[str, object]:
        """Applies a random bug mutation to a Python, Java, or C++ program."""
        norm_lang = language.lower()
        if norm_lang in ("java", "cpp", "c++"):
            mutators = [
                self.inject_missing_semicolon,
                self.inject_undefined_name,
                self.inject_wrong_operator,
                self.inject_missing_return,
            ]
        else:
            mutators = [
                self.inject_missing_colon,
                self.inject_off_by_one,
                self.inject_undefined_name,
                self.inject_wrong_operator,
                self.inject_missing_return,
            ]
        chosen_mutator = random.choice(mutators)
        mutated_code, category, line_no = chosen_mutator(code)

        return {
            "language": language,
            "original_code": code,
            "mutated_code": mutated_code,
            "bug_category": category,
            "buggy_line": line_no,
        }

    def generate_batch(self, items: List[Tuple[str, str]], samples_per_program: int = 10) -> List[Dict[str, object]]:
        """Generates a dataset of mutated programs for multiple languages."""
        dataset = []
        for code, lang in items:
            for _ in range(samples_per_program):
                mutated = self.mutate_program(code, language=lang)
                dataset.append(mutated)
        return dataset


def run_generation():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, "data", "raw")
    gen_dir = os.path.join(base_dir, "data", "generated")
    os.makedirs(gen_dir, exist_ok=True)

    programs = []
    if os.path.exists(raw_dir):
        for fname in os.listdir(raw_dir):
            ext = os.path.splitext(fname)[1].lower()
            lang = "python" if ext == ".py" else ("java" if ext == ".java" else ("cpp" if ext == ".cpp" else None))
            if lang:
                with open(os.path.join(raw_dir, fname), "r", encoding="utf-8") as f:
                    programs.append((f.read(), lang))

    if not programs:
        programs = [
            ("def sum_all(arr):\n    s = 0\n    for x in arr:\n        s = s + x\n    return s\n", "python")
        ]

    injector = BugInjector(seed=42)
    dataset = injector.generate_batch(programs, samples_per_program=30)

    out_file = os.path.join(gen_dir, "synthetic_dataset.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    print(f"Generated {len(dataset)} multi-language synthetic buggy programs -> {out_file}")


if __name__ == "__main__":
    run_generation()
