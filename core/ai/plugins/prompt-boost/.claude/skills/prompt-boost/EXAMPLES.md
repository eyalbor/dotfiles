# Prompt Enhancement Examples

This document provides concrete before/after examples demonstrating the prompt enhancement methodology in action.

---

## Example 1: Simple Coding Task

### BEFORE

```
write a function to sort an array
```

### AFTER

```
You are a senior software engineer specializing in algorithm implementation and code optimization. Your task is to create a robust, well-documented array sorting function.

<context>
Additional context about the programming language, performance requirements, or specific use case may be provided here.
</context>

## Instructions

1. Create a sorting function with the following specifications:
   - Accept an array of numbers as input
   - Return a new sorted array (do not mutate the original)
   - Use an efficient sorting algorithm (O(n log n) time complexity)
   - Handle edge cases: empty arrays, single-element arrays, arrays with duplicates

2. Include comprehensive documentation:
   - Function signature with parameter types
   - Description of the sorting algorithm used
   - Time and space complexity analysis
   - Usage examples

3. Add input validation:
   - Check if input is an array
   - Verify array elements are numbers
   - Throw descriptive errors for invalid inputs

4. Write the function in clean, idiomatic code:
   - Use meaningful variable names
   - Add inline comments for complex logic
   - Follow language-specific best practices

## Constraints

- Do NOT use built-in sort methods (implement the algorithm yourself)
- Do NOT mutate the input array
- Do NOT exceed 50 lines of code
- Avoid unnecessary complexity (prefer readability over cleverness)

## Output Format

Provide your response in this structure:

```language
// Function implementation with comments
function sortArray(arr) {
  // implementation
}

// Usage examples
const example1 = sortArray([3, 1, 4, 1, 5]);
// Output: [1, 1, 3, 4, 5]
```

Then include:
- Algorithm explanation (2-3 sentences)
- Time complexity: O(?)
- Space complexity: O(?)

## Examples

---EXAMPLE 1: Valid Input---
Input: `[5, 2, 8, 1, 9]`
Output: `[1, 2, 5, 8, 9]`
Reasoning: Standard ascending sort with no duplicates

---EXAMPLE 2: Edge Case---
Input: `[]`
Output: `[]`
Reasoning: Empty array returns empty array without errors

---EXAMPLE 3: Duplicates---
Input: `[3, 1, 3, 2, 1]`
Output: `[1, 1, 2, 3, 3]`
Reasoning: Duplicates are preserved in sorted order

## Validation Checklist

Before submitting your solution, verify:
- [ ] Function does not mutate input array
- [ ] Edge cases are handled correctly
- [ ] Time complexity is O(n log n) or better
- [ ] Code includes clear documentation
- [ ] Examples demonstrate correct behavior

**CRITICAL REMINDERS:**
- Do NOT use built-in sort methods - implement the algorithm yourself
- Handle edge cases: empty arrays, single elements, duplicates
- Include time and space complexity analysis in your response
```

---

## Example 2: Prompt Validation

### PROMPT TO VALIDATE

```
Write a Python function that reads a CSV file and calculates the average of a column. Make sure it handles errors.
```

### VALIDATION REPORT

```markdown
# Prompt Validation Report

## Summary
- **Overall Score**: 3.2/10 (Grade: Needs Improvement)
- **Strengths**:
  - Task is clear and specific (CSV processing with averaging)
  - Mentions error handling requirement
- **Priority Improvements**:
  - No role assignment or expertise level defined
  - Missing structured instructions and examples
  - No context section for dynamic inputs

## Detailed Scores

### 1. Structural Foundation: 2.4/10
- **Role & Task Assignment**: 4/10 - Task is clear ("calculate average of a column") but no role assignment. Missing: specific expertise level like "You are a senior Python developer specializing in data processing"
- **Context Sections**: 0/10 - No XML-tagged context sections for file path, column name, or other dynamic inputs
- **Detailed Instructions**: 3/10 - Single sentence instruction. Missing: numbered steps, sub-tasks, edge case handling
- **Constraints & Boundaries**: 2/10 - Vague "handles errors" without specifics. Missing: explicit error types, scope limitations
- **Output Format Specification**: 3/10 - Implies code output but doesn't specify format, documentation requirements, or return value structure

### 2. Content Requirements: 2.3/10
- **Examples Quality & Quantity**: 0/10 - No examples provided. Missing: sample CSV structure, expected input/output pairs
- **Reasoning Patterns**: 3/10 - No explicit chain-of-thought or reasoning instructions
- **Multi-Step Scaffolding**: 5/10 - Not applicable for this relatively simple task, but could benefit from phases (read → validate → calculate → return)

### 3. Quality Assurance: 1.7/10
- **Hallucination Prevention**: 0/10 - No instructions for handling uncertainty or unknowns
- **Output Validation Rules**: 2/10 - "Handles errors" implies validation but lacks specifics
- **Quality Checklist**: 3/10 - No explicit checklist for verification

### 4. Optimization & Formatting: 5.0/10
- **Token Efficiency**: 8/10 - Very concise (perhaps too concise)
- **Clarity & Specificity**: 5/10 - "Average of a column" is clear but "handles errors" is vague
- **Formatting Standards**: 3/10 - Plain text, no structural formatting
- **Critical Repetition**: 4/10 - No repetition (but also short enough that it's less critical)

## Specific Improvement Suggestions

### High Priority
1. **Add role assignment**: Start with "You are a senior Python developer specializing in data processing and pandas library. Your task is to create a robust CSV file reader with column averaging functionality."

2. **Add context section with XML tags**:
   ```
   <context:file-details>
   CSV file path, column name to average, and any specific requirements will be provided here.
   </context:file-details>
   ```

3. **Break down into numbered steps**:
   - Read CSV file using pandas/csv module
   - Validate file exists and is readable
   - Validate specified column exists
   - Calculate average, handling non-numeric values
   - Return result with appropriate error handling

4. **Add concrete examples**:
   ```
   ---EXAMPLE 1---
   Input: CSV with columns ['name', 'age', 'score'], calculate average of 'score'
   Output: {'average': 85.5, 'count': 100}

   ---EXAMPLE 2: Error Case---
   Input: Non-existent file
   Output: Raise FileNotFoundError with descriptive message
   ```

### Medium Priority
1. **Specify error types**: Define which errors to handle (FileNotFoundError, ValueError for non-numeric data, KeyError for missing column)

2. **Add output format specification**: Define return type (dict, float, custom object) and structure

3. **Include constraints**: "Do NOT load entire file into memory if > 1GB", "Use pandas if available, otherwise csv module"

### Optional Enhancements
1. Add hallucination prevention rules (uncertainty expression, step-by-step thinking)
2. Include quality checklist for self-verification
3. Add critical reminders section

## Next Steps
Would you like me to generate an enhanced version of this prompt using the Advance methodology? I can address all the high and medium priority improvements identified above.
```

### ENHANCED VERSION (After User Approval)

```
You are a senior Python developer specializing in data processing with extensive experience in pandas and error handling. Your task is to create a robust CSV file reader that calculates the average of a specified column with comprehensive error handling.

<context:file-details>
The CSV file path, target column name for averaging, and any specific requirements (encoding, delimiter, etc.) will be provided here.
</context:file-details>

## Instructions

1. **Read CSV file**:
   - Accept file_path and column_name as parameters
   - Use pandas if available (import pandas as pd), otherwise fall back to csv module
   - Handle file encoding issues (try UTF-8, fall back to latin-1)

2. **Validate inputs**:
   - Check if file exists and is readable (raise FileNotFoundError with clear message)
   - Verify file has .csv extension or can be parsed as CSV
   - Confirm column_name exists in CSV headers (raise KeyError with available columns list)

3. **Calculate average**:
   - Convert column values to numeric type (use pd.to_numeric or float conversion)
   - Skip or handle non-numeric values (log warning, count skipped rows)
   - Calculate mean using appropriate method (pandas .mean() or statistics.mean())
   - Handle empty column or all non-numeric values (return None or raise ValueError)

4. **Return results**:
   - Return dict with: {'average': float, 'count': int, 'skipped': int}
   - Include count of values used and count of skipped values
   - Log informative messages for debugging

## Constraints

- Do NOT load entire file into memory if size > 1GB (use chunking with pandas chunksize parameter)
- Do NOT fail silently - raise descriptive errors with actionable messages
- Do NOT assume column contains only numbers - handle mixed data types
- Limit function to < 50 lines of code

## Output Format

Return a dictionary:
```python
{
    'average': 85.5,        # float or None if no valid values
    'count': 100,           # int: number of values used in calculation
    'skipped': 5            # int: number of non-numeric values skipped
}
```

## Examples

---EXAMPLE 1: Successful Calculation---
Input:
- File: data.csv with columns ['name', 'age', 'score']
- Column: 'score'
- Data: [85, 90, 88, 92, 83]

Output:
```python
{'average': 87.6, 'count': 5, 'skipped': 0}
```
Reasoning: All values numeric, straightforward average

---EXAMPLE 2: Mixed Data Types---
Input:
- File: data.csv with column 'score'
- Data: [85, 'N/A', 90, '', 88]

Output:
```python
{'average': 87.67, 'count': 3, 'skipped': 2}
```
Reasoning: Skip non-numeric values, average remaining

---EXAMPLE 3: Error Case---
Input:
- File: nonexistent.csv

Output:
```python
raise FileNotFoundError("File 'nonexistent.csv' not found. Please verify the file path.")
```
Reasoning: Clear error message with actionable guidance

## Validation Checklist

Before finalizing your solution, verify:
- [ ] File existence is checked before reading
- [ ] Column name is validated against actual CSV headers
- [ ] Non-numeric values are handled without crashing
- [ ] Empty file or column returns appropriate result/error
- [ ] Return value matches specified dict structure
- [ ] Error messages are descriptive and actionable

**CRITICAL REMINDERS:**
- ALWAYS validate file exists and column exists before processing
- HANDLE non-numeric values gracefully - skip and count them
- RETURN dict with average, count, and skipped keys as specified
- RAISE descriptive errors (FileNotFoundError, KeyError, ValueError) with actionable messages
```

**Score Improvement**: Original 3.2/10 → Enhanced 9.1/10

**What Changed**:
- Added specific role and task assignment
- Added XML-tagged context section
- Broke down into 4 detailed numbered steps with sub-steps
- Added 3 concrete examples including edge case
- Specified exact output format with example
- Added constraints and validation checklist
- Included critical reminders at end

---

## Key Takeaways from Examples

1. **Specificity Matters**: Transform vague requests into detailed, actionable instructions
2. **Structure Enables Success**: Clear sections, numbered steps, and formatting guide the AI
3. **Examples Are Essential**: Concrete input-output pairs dramatically improve output quality
4. **Constraints Prevent Errors**: Explicitly stating what NOT to do is as important as what to do
5. **Validation Ensures Quality**: Checklists and self-verification catch mistakes before delivery
6. **Context Sections**: XML-tagged context areas make it clear where dynamic content goes
7. **Hallucination Prevention**: Explicit instructions about uncertainty and source attribution improve accuracy
8. **Critical Repetition**: Ending with key reminders reinforces the most important requirements
