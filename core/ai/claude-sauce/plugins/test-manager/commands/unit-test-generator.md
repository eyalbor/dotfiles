---
description: Create well-designed unit tests for staged files ready to be committed
---
# Unit Test Generator

Generate comprehensive unit tests for files that are staged and ready to be committed. Tests are designed for clarity, include permutations of test cases, and follow best practices.

## Behavior

1. Get the list of staged files using `git diff --cached --name-only`
2. Filter to only testable source files (exclude configs, assets, etc.)
3. For each file, analyze the code and generate unit tests following the design principles below

## Execution Flow

1. Create the tests (Steps 1-6)
2. **MANDATORY**: Invoke `test-security-scanner-agent` sub-agent to scan for security issues (Step 7)
3. **MANDATORY**: Invoke `test-quality-reviewer-agent` sub-agent for static quality analysis (Step 8)
4. **MANDATORY**: Invoke `test-execution-analyzer-agent` sub-agent to validate and run tests (Step 9)

## Test Design Principles

### Naming Convention
Use descriptive test names that explain what is being tested:
- Pattern: `test_<function/method>_<scenario>_<expected_outcome>`
- Example: `test_calculate_total_with_empty_cart_returns_zero`

### Test Structure (AAA Pattern)
Each test should follow Arrange-Act-Assert:
```
# Arrange - Set up test data and preconditions
# Act - Execute the code under test
# Assert - Verify the expected outcome
```

### Required Test Permutations
For each function/method, generate tests for:

1. **Happy Path** - Normal expected inputs and behavior
2. **Edge Cases**
   - Empty inputs (empty string, empty array, null/None)
   - Boundary values (0, -1, max int, min int)
   - Single element collections
3. **Error Cases**
   - Invalid inputs
   - Type mismatches (if applicable)
   - Expected exceptions/errors
4. **State Variations** (if applicable)
   - Different initial states
   - Before/after mutations

### Test Grouping
Group related tests logically by class/module and method. Use the language's idiomatic grouping mechanism:

**JavaScript/TypeScript (Jest, Vitest, Mocha):**
```javascript
describe('CartService', () => {
  describe('calculateTotal', () => {
    it('should return zero for empty cart', ...)
    it('should sum all item prices', ...)
  })
})
```

**Python (pytest):**
```python
class TestCartService:
    class TestCalculateTotal:
        def test_returns_zero_for_empty_cart(self): ...
        def test_sums_all_item_prices(self): ...
```

**Go:**
```go
func TestCartService_CalculateTotal(t *testing.T) {
    t.Run("returns zero for empty cart", func(t *testing.T) { ... })
    t.Run("sums all item prices", func(t *testing.T) { ... })
}
```

**Java/Kotlin (JUnit 5):**
```java
@Nested
@DisplayName("CartService")
class CartServiceTest {
    @Nested
    @DisplayName("calculateTotal")
    class CalculateTotal {
        @Test void returnsZeroForEmptyCart() { ... }
        @Test void sumsAllItemPrices() { ... }
    }
}
```

**Rust:**
```rust
mod cart_service_tests {
    mod calculate_total {
        #[test]
        fn returns_zero_for_empty_cart() { ... }
        #[test]
        fn sums_all_item_prices() { ... }
    }
}
```

**C# (xUnit/NUnit):**
```csharp
public class CartServiceTests
{
    public class CalculateTotal
    {
        [Fact] public void ReturnsZeroForEmptyCart() { ... }
        [Fact] public void SumsAllItemPrices() { ... }
    }
}
```

## How to Execute

### Step 1: Detect Test Framework
Before generating tests, determine the test framework:

1. **Check README/documentation files** for test framework mentions:
   ```bash
   find . -maxdepth 2 -name "README*" -o -name "CONTRIBUTING*" | head -5
   ```
   Look for sections like "Testing", "Development", "Running Tests"

2. **Check existing test files** for framework imports:
   - JavaScript/TypeScript: Look for `import { describe } from 'vitest'`, `jest`, `mocha`
   - Python: Look for `import pytest`, `import unittest`
   - Go: Standard library `testing` package
   - Java: `import org.junit`, `import org.testng`
   - Rust: `#[cfg(test)]` with standard test macros or external crates

3. **Check package/config files**:
   - `package.json` → `devDependencies` for jest, vitest, mocha
   - `pyproject.toml` / `setup.py` → pytest, unittest
   - `pom.xml` / `build.gradle` → junit, testng
   - `Cargo.toml` → test dependencies

4. **If framework cannot be detected**, ask the user:
   > "I couldn't detect the test framework for this project. Which test framework should I use?"

### Step 2: Detect Test Directory Location
Determine where to place generated test files:

1. **Check README/documentation files** for test directory information:
   - Look for "Tests are located in...", "Test directory", or similar

2. **Explore project structure** for existing test directories:
   ```bash
   find . -type d \( -name "tests" -o -name "test" -o -name "__tests__" -o -name "spec" \) -not -path "*/node_modules/*" -not -path "*/.git/*" | head -10
   ```

3. **Check existing test files** to understand the pattern:
   ```bash
   find . -type f \( -name "*.test.*" -o -name "*_test.*" -o -name "*Test.*" -o -name "*_spec.*" \) -not -path "*/node_modules/*" | head -10
   ```

4. **If test directory cannot be detected**, ask the user:
   > "I couldn't determine where tests should be placed. Where should I create the test files?"

### Step 3: Get Staged Files
```bash
git diff --cached --name-only --diff-filter=ACM
```

### Step 4: Analyze Each File
For each staged source file:
1. Read the file content
2. Identify functions, methods, and classes
3. Understand the logic and possible code paths

### Step 5: Generate Tests
Create test files using:
- The detected (or user-specified) test framework
- The detected (or user-specified) test directory location
- Match existing test file naming conventions in the project

### Step 6: Output Summary
After generating tests, provide:
- List of test files created/modified
- Number of test cases per file
- Coverage of permutations (happy path, edge cases, error cases)

### Step 7: Security Scan (REQUIRED)

**You MUST invoke the test-security-scanner-agent sub-agent to scan for security vulnerabilities before any other validation.**

Use the Task tool to spawn the agent:
```
Task tool parameters:
- subagent_type: "test-security-scanner-agent"
- prompt: "Scan the following generated test files for security issues: [list the test files you created]. Source files being tested: [list source files]. Test framework: [framework]."
- description: "Security scan tests"
```

This agent scans for:
- Hardcoded secrets (API keys, passwords, tokens)
- Dangerous operations (file system attacks, command injection)
- Sensitive data in fixtures (PII, production data)
- Execution risks (privilege escalation, resource exhaustion)

**If security issues are found:**
- **CRITICAL issues:** STOP. Fix immediately before proceeding.
- **HIGH issues:** Fix before test execution.
- **MEDIUM/LOW issues:** Review and fix as recommended.

Do NOT skip this step. Security scan prevents harmful tests from running.

### Step 8: Review Test Quality (REQUIRED)

**You MUST invoke the test-quality-reviewer-agent sub-agent for static quality analysis before running tests.**

Use the Task tool to spawn the agent:
```
Task tool parameters:
- subagent_type: "test-quality-reviewer-agent"
- prompt: "Review test quality for the following generated test files: [list the test files you created]. Source files being tested: [list source files]. Test framework: [framework]."
- description: "Review test quality"
```

This agent performs static analysis to check:
- Assertion quality (flags weak assertions like `toBeTruthy()`)
- Edge case coverage (identifies missing permutations)
- Test isolation (detects shared state issues)
- Naming and structure conventions

**If quality issues are found:**
1. Review the agent's recommendations
2. Fix high-priority issues (weak assertions, missing edge cases)
3. Re-run the quality reviewer to confirm fixes

Do NOT skip this step. Quality review catches issues before execution.

### Step 9: Execute and Validate Tests (REQUIRED)

**You MUST invoke the test-execution-analyzer-agent sub-agent to validate the generated tests.**

Use the Task tool to spawn the agent:
```
Task tool parameters:
- subagent_type: "test-execution-analyzer-agent"
- prompt: "Validate and run the following generated test files: [list the test files you created]. Test framework: [framework]. Test directory: [directory]."
- description: "Validate generated tests"
```
IF the session had failed and you fix, call the test-execution-analyzer-agent sub-agent AGAIN! so it will make sure the tests passed.
Do NOT skip this step. The test generation is not complete until the sub-agent confirms the tests pass.

## Language-Specific Guidelines

### JavaScript/TypeScript
- Use Jest, Vitest, or project's existing framework
- Use `describe` and `it` blocks
- Mock dependencies with jest.mock() or vi.mock()

### Python
- Use pytest or unittest
- Use fixtures for setup
- Use parametrize for permutations

### Go
- Use table-driven tests
- Place in same package with `_test.go` suffix

### Java/Kotlin
- Use JUnit 5
- Use `@Nested` for grouping
- Use `@ParameterizedTest` for permutations

## Important Notes

- Only generate tests for files that are staged (`git diff --cached`)
- Do not modify the source files being tested
- Follow the project's existing test style and conventions
- If no test framework is detected, ask the user which to use
