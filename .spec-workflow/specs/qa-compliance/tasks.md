# Tasks Document

## Important: Iterative Refactoring Workflow

**CRITICAL**: Pre-commit hooks may fail at any point during implementation, catching quality violations (type errors, complexity issues, line count violations, etc.). When pre-commit errors occur:

1. **Refactor Immediately**: Do NOT defer refactoring to later tasks - fix violations as soon as they are detected
2. **Loop Back**: If a commit fails pre-commit checks, refactor the code immediately before proceeding
3. **Incremental Compliance**: Each task should leave the codebase in a pre-commit-passing state
4. **Test After Refactoring**: Always run pre-commit hooks after refactoring to verify fixes

**Expected Workflow Pattern**:
```
Task → Code Changes → git add → git commit
                         ↓
                   Pre-commit Runs
                         ↓
                    ┌────┴────┐
                    ↓         ↓
                  PASS      FAIL
                    ↓         ↓
               Commit OK   Refactor Now!
                              ↓
                         git add (fixes)
                              ↓
                         git commit (retry)
```

Tasks 13-20 (type hints and complexity refactoring) are designed to proactively address violations, but pre-commit may still catch issues in later tasks. **When it does, stop and refactor immediately.**

## Implementation Tasks

- [x] 1. Create pre-commit configuration file
  - File: `.pre-commit-config.yaml`
  - Create pre-commit framework configuration with all quality checks
  - Configure Rust checks (cargo check, clippy, rustfmt)
  - Configure Python checks (mypy, flake8, black)
  - Configure custom validators (complexity, line count, function size)
  - Purpose: Establish automated quality gate for all commits
  - _Leverage: None (new file)_
  - _Requirements: 1, 5, 6_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: DevOps Engineer specializing in CI/CD and git hooks | Task: Create comprehensive `.pre-commit-config.yaml` in repository root following requirements 1, 5, and 6, configuring all Rust checks (cargo check, clippy, rustfmt), Python checks (mypy, flake8, black --check), and custom validators as specified in design.md | Restrictions: Use pre-commit framework version ≥3.0.0, ensure hooks work on Linux/macOS/Windows, do not include hooks for tools not yet installed, set appropriate file filters for each hook | _Leverage: design.md Component 1 for exact configuration structure_ | Success: File created with all hooks properly configured, hooks target correct file types (.rs for Rust, .py for Python), exit codes properly handled, configuration follows pre-commit best practices | Instructions: After creating the file, edit tasks.md to change this task from [ ] to [x] when complete_

- [x] 2. Create Python tool configuration in pyproject.toml
  - File: `packages/python/zlibrary-downloader/pyproject.toml`
  - Extend existing pyproject.toml with tool configurations
  - Add [tool.mypy] with strict mode settings
  - Add [tool.black] with line-length 100
  - Add [tool.pytest.ini_options] with coverage settings
  - Add [tool.coverage.run] and [tool.coverage.report] sections
  - Purpose: Centralize Python quality tool configuration
  - _Leverage: Existing pyproject.toml structure_
  - _Requirements: 6, 7, 8_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in project configuration and tool integration | Task: Extend existing `packages/python/zlibrary-downloader/pyproject.toml` following requirements 6, 7, and 8, adding mypy strict mode configuration, black formatting with line-length 100, pytest with coverage ≥80%, and coverage reporting as detailed in design.md Configuration Files section | Restrictions: Do not modify existing [project] or [build-system] sections, maintain backward compatibility, ensure configurations match design.md specifications exactly | _Leverage: design.md "Configuration Files" section for exact settings, existing pyproject.toml for structure_ | Success: All tool configurations added correctly, mypy strict mode enabled, pytest configured with coverage targets, black line-length set to 100, configurations are valid TOML syntax | Instructions: After editing the file, edit tasks.md to change this task from [ ] to [x] when complete_

- [x] 3. Create flake8 configuration file
  - File: `.flake8`
  - Create flake8 configuration with project standards
  - Set max-line-length to 100
  - Set max-complexity to 10
  - Configure exclusions (venv/, .git/, __pycache__, *.egg-info)
  - Add per-file-ignores for __init__.py (F401)
  - Purpose: Configure Python linting standards
  - _Leverage: None (new file)_
  - _Requirements: 6, 8_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in code quality and linting | Task: Create `.flake8` configuration file in repository root following requirements 6 and 8, setting max-line-length 100, max-complexity 10, and exclusions as specified in design.md Configuration Files section | Restrictions: Must use INI format, ensure compatibility with flake8 ≥7.0.0, do not conflict with black formatting rules (extend-ignore E203, W503), exclude appropriate directories | _Leverage: design.md "Configuration Files - Flake8 Configuration" for exact content_ | Success: File created with correct INI syntax, all settings match design specifications, flake8 can parse configuration without errors, exclusions cover build artifacts and virtual environments | Instructions: After creating the file, edit tasks.md to change this task from [ ] to [x] when complete_

- [x] 4. Extend Rust Cargo.toml with clippy lints
  - File: `packages/rust/Cargo.toml`
  - Add [workspace.lints.clippy] section to existing workspace Cargo.toml
  - Configure clippy warnings: all, pedantic
  - Configure clippy denies: unwrap_used, expect_used, panic
  - Add missing_docs_in_private_items as warn
  - Purpose: Enforce Rust code quality standards via clippy
  - _Leverage: Existing workspace Cargo.toml_
  - _Requirements: 5, 8_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Rust Developer with expertise in cargo workspaces and clippy configuration | Task: Extend existing `packages/rust/Cargo.toml` workspace configuration following requirements 5 and 8, adding [workspace.lints.clippy] section with strict linting rules as specified in design.md Configuration Files section | Restrictions: Do not modify existing [workspace], [workspace.package], or [workspace.dependencies] sections, ensure TOML syntax is valid, lint levels must be "warn" or "deny" only | _Leverage: design.md "Configuration Files - Rust Clippy Configuration", existing Cargo.toml structure_ | Success: Clippy lints section added to workspace configuration, all specified lints configured with correct levels, cargo clippy accepts configuration, lints apply to all workspace members | Instructions: After editing the file, edit tasks.md to change this task from [ ] to [x] when complete_

- [x] 5. Create Rust complexity checker script
  - File: `scripts/check_rust_complexity.sh`
  - Create bash script to run rust-code-analysis and check complexity
  - Run rust-code-analysis-cli on Rust source files
  - Output JSON metrics to temporary file
  - Call Python parser script to validate complexity ≤10
  - Purpose: Automate Rust cyclomatic complexity validation
  - _Leverage: None (new files)_
  - _Requirements: 3, 8_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: DevOps Engineer with expertise in bash scripting and code analysis | Task: Create `scripts/check_rust_complexity.sh` bash script following requirements 3 and 8, implementing the workflow specified in design.md Component 2: run rust-code-analysis-cli, save JSON output, call parser script with threshold 10 | Restrictions: Must use #!/bin/bash shebang, must use 'set -e' for error propagation, do not hardcode file paths (use script directory resolution), ensure cross-platform compatibility (Linux/macOS) | _Leverage: design.md Component 2 for exact implementation, scripts directory must be created if it doesn't exist_ | Success: Script is executable (chmod +x), runs rust-code-analysis-cli correctly, handles errors gracefully, calls parser script with correct arguments, exits with appropriate code (0=pass, 1=fail) | Instructions: After creating the script, edit tasks.md to change this task from [ ] to [x] when complete_

- [x] 6. Create Rust complexity parser script
  - File: `scripts/parse_rust_complexity.py`
  - Create Python script to parse rust-code-analysis JSON output
  - Accept JSON file path and complexity threshold as arguments
  - Extract cyclomatic complexity for each function
  - Report functions exceeding threshold
  - Exit with code 1 if violations found
  - Purpose: Parse and validate Rust complexity metrics
  - _Leverage: None (new file)_
  - _Requirements: 3_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in JSON parsing and data validation | Task: Create `scripts/parse_rust_complexity.py` script following requirement 3, parsing rust-code-analysis JSON output and reporting functions with cyclomatic complexity exceeding threshold (default 10) | Restrictions: Must use #!/usr/bin/env python3 shebang, must use only stdlib (no external dependencies), must validate JSON structure, must provide clear error messages with file paths and line numbers | _Leverage: design.md Component 2 for specifications, rust-code-analysis JSON format documentation_ | Success: Script is executable, correctly parses rust-code-analysis JSON, identifies complexity violations accurately, provides detailed output (function name, file, line, complexity score), exits with proper codes (0=pass, 1=violations, 2=error) | Instructions: After creating the script, edit tasks.md to change this task from [ ] to [x] when complete_

- [x] 7. Create Python complexity checker script
  - File: `scripts/check_python_complexity.sh`
  - Create bash script to run radon and check complexity
  - Run radon cc --min C --json on Python source files
  - Output JSON metrics to temporary file
  - Call Python parser script to validate complexity ≤10
  - Purpose: Automate Python cyclomatic complexity validation
  - _Leverage: None (new file)_
  - _Requirements: 3, 8_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: DevOps Engineer with expertise in bash scripting and Python tooling | Task: Create `scripts/check_python_complexity.sh` bash script following requirements 3 and 8, implementing the workflow specified in design.md Component 3: run radon cc with JSON output, call parser script with threshold 10 | Restrictions: Must use #!/bin/bash shebang, must use 'set -e', do not hardcode paths, check if radon is installed before running, ensure cross-platform compatibility | _Leverage: design.md Component 3 for exact implementation_ | Success: Script is executable, runs radon correctly with proper options, handles missing radon gracefully with error message, calls parser script with correct arguments, exits with appropriate code | Instructions: After creating the script, edit tasks.md to change this task from [ ] to [x] when complete_

- [x] 8. Create Python complexity parser script
  - File: `scripts/parse_python_complexity.py`
  - Create Python script to parse radon JSON output
  - Accept JSON file path and complexity threshold as arguments
  - Extract cyclomatic complexity for each function
  - Report functions exceeding threshold
  - Exit with code 1 if violations found
  - Purpose: Parse and validate Python complexity metrics
  - _Leverage: None (new file)_
  - _Requirements: 3_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in code metrics and JSON parsing | Task: Create `scripts/parse_python_complexity.py` script following requirement 3, parsing radon JSON output and reporting functions with cyclomatic complexity exceeding threshold (default 10) | Restrictions: Must use #!/usr/bin/env python3 shebang, stdlib only, must handle radon JSON format correctly, provide clear output with function names and locations | _Leverage: design.md Component 3 for specifications, radon JSON output format_ | Success: Script is executable, correctly parses radon JSON, identifies violations accurately, provides detailed output (function name, file, line, complexity score), exits with proper codes, handles malformed JSON gracefully | Instructions: After creating the script, edit tasks.md to change this task from [ ] to [x] when complete_

- [x] 9. Create line count validator script
  - File: `scripts/validate_line_count.py`
  - Create Python script to validate file line counts ≤400
  - Accept list of file paths as arguments (from pre-commit)
  - Count non-empty, non-comment lines for each file
  - Exclude test files, generated code, build artifacts
  - Report files exceeding 400 lines
  - Exit with code 1 if violations found
  - Purpose: Enforce file size limit automatically
  - _Leverage: None (new file)_
  - _Requirements: 4_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in file parsing and validation | Task: Create `scripts/validate_line_count.py` script following requirement 4, validating file line counts ≤400 lines excluding comments, blank lines, test files, and generated code as specified in design.md Component 4 | Restrictions: Must use #!/usr/bin/env python3 shebang, stdlib only, must handle both .rs and .py file formats, must exclude patterns: test_, _test., target/, venv/, __pycache__, do not count comments or blank lines | _Leverage: design.md Component 4 for implementation, structure.md for file size guidelines_ | Success: Script is executable, correctly counts lines for both Rust and Python, excludes appropriate files, provides clear violation reports with file paths and line counts, exits with proper codes | Instructions: After creating the script, edit tasks.md to change this task from [ ] to [x] when complete_

- [x] 10. Create function size validator script
  - File: `scripts/validate_function_size.py`
  - Create Python script to validate function sizes ≤30 lines
  - Accept list of file paths as arguments
  - Parse Python files with AST to extract function line counts
  - Parse Rust files with basic regex/parsing to extract function line counts
  - Report functions exceeding 30 lines
  - Exit with code 1 if violations found
  - Purpose: Enforce function size limit automatically
  - _Leverage: Python ast module for Python parsing_
  - _Requirements: 4_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in AST parsing and static analysis | Task: Create `scripts/validate_function_size.py` script following requirement 4, validating function sizes ≤30 lines using Python AST for .py files and regex/basic parsing for .rs files as specified in design.md Component 5 | Restrictions: Must use #!/usr/bin/env python3 shebang, stdlib only (including ast module), must count lines excluding function signature and docstrings, handle both sync and async Python functions, use reasonable heuristics for Rust functions | _Leverage: design.md Component 5 for implementation and structure, Python ast module documentation_ | Success: Script is executable, correctly parses Python functions with AST, identifies Rust functions with reasonable accuracy, provides detailed violation reports (function name, file, line number, actual line count), exits with proper codes | Instructions: After creating the script, edit tasks.md to change this task from [ ] to [x] when complete_

- [x] 11. Install pre-commit and Rust tools
  - Install pre-commit framework (pip install pre-commit)
  - Install rust-code-analysis-cli (cargo install rust-code-analysis-cli)
  - Run pre-commit install to setup git hooks
  - Verify installations successful
  - **NOTE**: Once pre-commit is installed, ALL subsequent commits will be checked. If commits fail, refactor immediately before proceeding to next task.
  - Purpose: Install required tooling for QA automation
  - _Leverage: Existing pip and cargo package managers_
  - _Requirements: 1, 8_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: DevOps Engineer with expertise in development environment setup | Task: Install required quality assurance tools following requirements 1 and 8: install pre-commit framework via pip, install rust-code-analysis-cli via cargo, and run pre-commit install to setup git hooks as specified in design.md Tool Selection section | Restrictions: Use pip install (not pip3 unless necessary), ensure tools are installed in user environment not system-wide, verify each installation before proceeding, must document installation commands in commit message | _Leverage: design.md Tool Selection sections for versions (pre-commit ≥3.0.0, rust-code-analysis ≥0.0.25)_ | Success: pre-commit installed and available in PATH, rust-code-analysis-cli installed and available, git hooks installed in .git/hooks/, can run 'pre-commit --version' and 'rust-code-analysis-cli --version' successfully | Instructions: After installation, edit tasks.md to change this task from [ ] to [x] when complete_

- [x] 12. Install Python development dependencies
  - Update pyproject.toml [project.optional-dependencies] dev section
  - Add mypy>=1.8.0, black>=24.0.0, flake8>=7.0.0, radon>=6.0.0
  - Add pytest>=8.0.0, pytest-cov>=4.1.0
  - Add flake8 plugins: flake8-bugbear, flake8-comprehensions, flake8-simplify
  - Install with pip install -e ".[dev]"
  - Purpose: Install Python quality tools and testing framework
  - _Leverage: Existing pyproject.toml structure_
  - _Requirements: 6, 7, 8_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in package management and dependencies | Task: Update `packages/python/zlibrary-downloader/pyproject.toml` [project.optional-dependencies].dev section following requirements 6, 7, and 8, adding all Python quality tools with versions specified in design.md Tool Selection, then install with editable install | Restrictions: Use minimum version specifiers (>=) not pinned versions, ensure dev dependencies are separate from runtime dependencies, do not modify existing dev dependencies if any, must test installation succeeds | _Leverage: design.md Tool Selection sections for exact versions, existing pyproject.toml for structure_ | Success: All tools added to [project.optional-dependencies].dev with correct versions, installation via 'pip install -e ".[dev]"' succeeds without errors, all tools available and runnable (mypy --version, black --version, etc.) | Instructions: After installation, edit tasks.md to change this task from [ ] to [x] when complete_

- [x] 13. Add type hints to zlibrary_downloader/__init__.py
  - File: `packages/python/zlibrary-downloader/zlibrary_downloader/__init__.py`
  - Add module-level type hints and docstring
  - Add type annotations to any existing functions/classes
  - Ensure imports are properly typed
  - Run mypy to verify no errors
  - **IMPORTANT**: When you commit these changes, pre-commit may catch other issues (formatting, complexity, etc.). If commit fails, refactor immediately and retry.
  - Purpose: Begin Python type hint coverage for mypy compliance
  - _Leverage: Existing __init__.py_
  - _Requirements: 2_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in type hints and PEP 484 | Task: Add complete type hints to `packages/python/zlibrary-downloader/zlibrary_downloader/__init__.py` following requirement 2, ensuring all exports are properly typed and module passes mypy strict mode | Restrictions: Must follow PEP 484 and PEP 526 standards, use typing module for complex types (List, Dict, Optional, Union), do not change runtime behavior, ensure backward compatibility | _Leverage: Existing __init__.py code, mypy documentation, PEP 484 specification_ | Success: All functions/classes have complete type annotations, mypy --strict passes with zero errors for this file, imports are properly typed, module docstring added with type information | Instructions: After adding type hints and verifying with mypy, edit tasks.md to change this task from [ ] to [x] when complete_

- [ ] 14. Add type hints to zlibrary_downloader/client.py
  - File: `packages/python/zlibrary-downloader/zlibrary_downloader/client.py`
  - Add type annotations to Zlibrary class and all methods
  - Add type hints for private methods (__makePostRequest, __makeGetRequest, etc.)
  - Use proper typing for request/response dicts (TypedDict or Dict[str, Any])
  - Add return type annotations for all methods
  - Run mypy to verify no errors
  - Purpose: Complete type coverage for API client module
  - _Leverage: Existing client.py with 362 lines_
  - _Requirements: 2_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in type hints and API clients | Task: Add comprehensive type hints to `packages/python/zlibrary-downloader/zlibrary_downloader/client.py` (362 lines) following requirement 2, annotating all methods in Zlibrary class including private methods, ensuring mypy strict mode compliance | Restrictions: Must use proper types for dict returns (consider TypedDict for structured responses), use Optional for nullable parameters, use Union for multiple types, maintain existing method signatures except for type annotations, do not break existing functionality | _Leverage: Existing client.py code (read file first), requests library type stubs, typing module_ | Success: All methods have complete type annotations including parameters and return types, private methods are typed, mypy --strict passes with zero errors, TypedDict or proper dict types used for structured data | Instructions: After adding type hints and verifying with mypy, edit tasks.md to change this task from [ ] to [x] when complete_

- [ ] 15. Add type hints to zlibrary_downloader/cli.py
  - File: `packages/python/zlibrary-downloader/zlibrary_downloader/cli.py`
  - Add type annotations to all functions (main, command_line_mode, interactive_mode, etc.)
  - Add type hints for function parameters (z_client, args, etc.)
  - Add return type annotations (mostly -> None for CLI functions)
  - Handle argparse.Namespace type properly
  - Run mypy to verify no errors
  - Purpose: Complete type coverage for CLI module
  - _Leverage: Existing cli.py with 340 lines_
  - _Requirements: 2_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in type hints and CLI applications | Task: Add comprehensive type hints to `packages/python/zlibrary-downloader/zlibrary_downloader/cli.py` (340 lines) following requirement 2, annotating all functions including argparse integration, ensuring mypy strict mode compliance | Restrictions: Must properly type argparse.Namespace objects, use None return type for CLI functions with no return, use Optional for optional parameters with None defaults, maintain function signatures except type annotations, ensure sys.exit calls are properly handled | _Leverage: Existing cli.py code (read file first), argparse type stubs, typing module_ | Success: All functions have complete type annotations, argparse.Namespace properly typed, mypy --strict passes with zero errors, function return types are accurate (mostly -> None) | Instructions: After adding type hints and verifying with mypy, edit tasks.md to change this task from [ ] to [x] when complete_

- [ ] 16. Add type hints to zlibrary_downloader/tui.py
  - File: `packages/python/zlibrary-downloader/zlibrary_downloader/tui.py`
  - Add type annotations to ZLibraryTUI class and all methods
  - Add type hints for method parameters and return types
  - Handle rich library types properly (Console, Table, etc.)
  - Add type hints for class attributes (FORMATS, LANGUAGES, etc.)
  - Run mypy to verify no errors
  - Purpose: Complete type coverage for TUI module
  - _Leverage: Existing tui.py with 364 lines_
  - _Requirements: 2_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in type hints and terminal UI applications | Task: Add comprehensive type hints to `packages/python/zlibrary-downloader/zlibrary_downloader/tui.py` (364 lines) following requirement 2, annotating ZLibraryTUI class and all methods including rich library integration, ensuring mypy strict mode compliance | Restrictions: Must properly type rich library objects (Console, Table, Panel, etc.), use class variables annotations for FORMATS/LANGUAGES/SORT_ORDERS, handle Optional returns where methods may return None, maintain existing signatures except type annotations | _Leverage: Existing tui.py code (read file first), rich library type stubs, typing module_ | Success: ZLibraryTUI class fully typed including __init__, all methods have type annotations, class attributes properly typed, mypy --strict passes with zero errors, rich library types correctly used | Instructions: After adding type hints and verifying with mypy, edit tasks.md to change this task from [ ] to [x] when complete_

- [ ] 17. Run initial complexity audit on Python code
  - Run radon cc on all Python modules
  - Generate report of functions with complexity >10
  - Document functions requiring refactoring
  - Create task list for refactoring high-complexity functions
  - Purpose: Identify Python complexity violations before enforcement
  - _Leverage: Installed radon tool_
  - _Requirements: 3, 10_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in code metrics and refactoring | Task: Run comprehensive complexity audit on Python codebase following requirements 3 and 10, using radon to identify all functions with cyclomatic complexity >10, generating detailed report for refactoring | Restrictions: Must use radon cc --min C command, must generate JSON output for parsing, must document each violation with file path, function name, line number, and complexity score, do not refactor yet (audit only) | _Leverage: Installed radon tool, design.md Component 3 for usage, existing Python codebase in packages/python/zlibrary-downloader/zlibrary_downloader/_ | Success: Audit complete with comprehensive report, all functions with complexity >10 identified, report includes file paths, function names, line numbers, and complexity scores, refactoring task list created for each violation | Instructions: Create audit report as comment in this task or separate file, edit tasks.md to change this task from [ ] to [x] when audit complete_

- [ ] 18. Run initial complexity audit on Rust code
  - Run rust-code-analysis on Rust modules
  - Generate report of functions with complexity >10
  - Document functions requiring refactoring
  - Create task list for refactoring high-complexity functions
  - Purpose: Identify Rust complexity violations before enforcement
  - _Leverage: Installed rust-code-analysis-cli tool_
  - _Requirements: 3, 10_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Rust Developer with expertise in code metrics and refactoring | Task: Run comprehensive complexity audit on Rust codebase following requirements 3 and 10, using rust-code-analysis to identify all functions with cyclomatic complexity >10, generating detailed report for refactoring | Restrictions: Must use rust-code-analysis-cli --metrics -O json, must parse JSON output to extract complexity metrics, must document each violation with file path, function name, line number, and complexity score, do not refactor yet (audit only) | _Leverage: Installed rust-code-analysis-cli tool, design.md Component 2 for usage, existing Rust codebase in packages/rust/text-extractor/src/_ | Success: Audit complete with comprehensive report, all functions with complexity >10 identified, report includes file paths, function names, line numbers, and complexity scores, refactoring task list created for each violation | Instructions: Create audit report as comment in this task or separate file, edit tasks.md to change this task from [ ] to [x] when audit complete_

- [ ] 19. Refactor Python high-complexity functions (if any found)
  - File: Varies based on audit results from task 17
  - Refactor each function with complexity >10 into smaller functions
  - Maintain existing behavior (verify with tests)
  - Ensure refactored functions have complexity ≤10
  - Update any affected tests
  - Purpose: Reduce Python code complexity to meet standards
  - _Leverage: Audit results from task 17, existing test suite_
  - _Requirements: 3, 10_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in refactoring and code simplification | Task: Refactor all Python functions identified in complexity audit (task 17) to achieve cyclomatic complexity ≤10 following requirements 3 and 10, using extract method refactoring and decomposition techniques while maintaining behavior | Restrictions: Must not change external behavior or API, must verify with existing tests after each refactoring, must use meaningful names for extracted functions, must maintain SLAP (Single Level of Abstraction Principle), do not over-engineer or introduce unnecessary abstractions | _Leverage: Audit results from task 17 for target functions, existing test suite for verification, design.md error handling principles_ | Success: All identified functions refactored to complexity ≤10, existing tests still pass, behavior unchanged, radon cc confirms compliance, code is more readable and maintainable | Instructions: Refactor one function at a time, run tests after each refactoring, edit tasks.md to change this task from [ ] to [x] when all refactorings complete_

- [ ] 20. Refactor Rust high-complexity functions (if any found)
  - File: Varies based on audit results from task 18
  - Refactor each function with complexity >10 into smaller functions
  - Maintain existing behavior (verify with tests)
  - Ensure refactored functions have complexity ≤10
  - Update any affected tests
  - Purpose: Reduce Rust code complexity to meet standards
  - _Leverage: Audit results from task 18, cargo test_
  - _Requirements: 3, 10_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Rust Developer with expertise in refactoring and code simplification | Task: Refactor all Rust functions identified in complexity audit (task 18) to achieve cyclomatic complexity ≤10 following requirements 3 and 10, using extract method refactoring and decomposition techniques while maintaining behavior | Restrictions: Must not change external behavior or API, must verify with cargo test after each refactoring, must use meaningful names for extracted functions, must maintain SLAP principle, must follow Rust idioms and borrow checker rules | _Leverage: Audit results from task 18 for target functions, cargo test for verification, design.md error handling principles_ | Success: All identified functions refactored to complexity ≤10, cargo test passes, behavior unchanged, rust-code-analysis confirms compliance, code is more readable and maintainable | Instructions: Refactor one function at a time, run cargo test after each refactoring, edit tasks.md to change this task from [ ] to [x] when all refactorings complete_

- [ ] 21. Test pre-commit hooks with clean commit
  - Make a small, compliant code change (e.g., add comment)
  - Stage the change with git add
  - Attempt commit
  - Verify all pre-commit hooks run and pass
  - Verify commit succeeds
  - Purpose: Validate pre-commit setup with passing scenario
  - _Leverage: Configured pre-commit hooks from task 1_
  - _Requirements: 1_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: QA Engineer with expertise in integration testing | Task: Test pre-commit hook integration following requirement 1 by making a compliant code change and verifying all hooks run and pass, validating the complete pre-commit workflow | Restrictions: Must use git commands only (git add, git commit), must verify each hook runs by checking pre-commit output, must not use --no-verify to bypass hooks, change must be compliant with all quality standards | _Leverage: Configured .pre-commit-config.yaml from task 1, all installed tools_ | Success: All hooks run in sequence, all hooks pass (green check marks), commit succeeds, git log shows commit was created, pre-commit output is readable and clear | Instructions: After successful test commit, edit tasks.md to change this task from [ ] to [x] when complete_

- [ ] 22. Test pre-commit hooks with type error
  - Introduce a deliberate type error in Python code
  - Stage the change with git add
  - Attempt commit
  - Verify mypy hook fails and blocks commit
  - Verify error message is clear
  - Fix the type error and verify commit succeeds
  - Purpose: Validate pre-commit catches type errors
  - _Leverage: Configured mypy hook_
  - _Requirements: 2, 6_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: QA Engineer with expertise in negative testing | Task: Test pre-commit type checking following requirements 2 and 6 by introducing a deliberate type error, verifying mypy blocks commit with clear error message, then fixing and verifying success | Restrictions: Must introduce actual type error (e.g., wrong argument type), must not use --no-verify, must verify mypy specifically fails (not other hooks), must document error message received | _Leverage: Configured mypy hook from .pre-commit-config.yaml, type hints added in tasks 13-16_ | Success: Type error introduced in Python file, mypy hook fails and blocks commit, error message clearly indicates type error with file and line, fixing error allows commit to succeed | Instructions: Document the test results, revert test changes or commit the fix, edit tasks.md to change this task from [ ] to [x] when complete_

- [ ] 23. Test pre-commit hooks with complexity violation
  - Temporarily add a function with complexity >10
  - Stage the change with git add
  - Attempt commit
  - Verify complexity hook fails and blocks commit
  - Verify error message shows function name and complexity score
  - Remove the test function
  - Purpose: Validate pre-commit catches complexity violations
  - _Leverage: Configured complexity checker hooks_
  - _Requirements: 3_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: QA Engineer with expertise in code quality validation | Task: Test pre-commit complexity checking following requirement 3 by adding a function with cyclomatic complexity >10, verifying complexity hook blocks commit with detailed error message, then removing test code | Restrictions: Must create realistic high-complexity function (e.g., deeply nested if-else), must not use --no-verify, must verify complexity hook specifically fails, must document error output format | _Leverage: Configured complexity hooks from .pre-commit-config.yaml (task 1), complexity checker scripts (tasks 5-8)_ | Success: High-complexity function added and staged, complexity hook fails and blocks commit, error message shows function name, file, line number, and actual complexity score, removing function allows normal commits | Instructions: Document the test results showing exact error output, revert test changes, edit tasks.md to change this task from [ ] to [x] when complete_

- [ ] 24. Update root README.md with QA setup instructions
  - File: `README.md`
  - Add "Quality Assurance" or "Development Setup" section
  - Document pre-commit installation and setup
  - Document required tool installations (Rust, Python)
  - Include commands for installing dev dependencies
  - Document how to run quality checks manually
  - Purpose: Enable new developers to setup QA tooling
  - _Leverage: Existing README.md structure_
  - _Requirements: 9_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Technical Writer with expertise in developer documentation | Task: Update root README.md following requirement 9, adding comprehensive QA setup instructions covering pre-commit installation, tool installation, running checks manually, and common troubleshooting | Restrictions: Must follow existing README format and tone, must provide copy-pasteable commands, must include both quick setup and detailed setup options, do not duplicate existing content, ensure instructions work on Linux/macOS/Windows | _Leverage: Existing README.md for style, design.md documentation sections for content, installation commands from tasks 11-12_ | Success: QA section added to README with clear structure, all installation commands provided and tested, manual check commands documented (mypy, black, flake8, cargo clippy, etc.), troubleshooting tips included | Instructions: After updating README, edit tasks.md to change this task from [ ] to [x] when complete_

- [ ] 25. Create Python package tests directory structure
  - Directory: `packages/python/zlibrary-downloader/tests/`
  - Create tests directory if not exists
  - Create __init__.py in tests directory
  - Create test_client.py stub file
  - Create test_cli.py stub file
  - Create test_tui.py stub file
  - Create conftest.py for pytest fixtures
  - Purpose: Establish testing infrastructure for Python package
  - _Leverage: pytest conventions_
  - _Requirements: 7_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python Developer with expertise in pytest and test infrastructure | Task: Create comprehensive test directory structure following requirement 7, setting up pytest-compatible layout with test files for each module, fixtures, and configuration | Restrictions: Must follow pytest conventions, must create __init__.py to make tests a package, stub files should have basic structure with docstrings, conftest.py should include commonly needed fixtures (mock zlibrary client, etc.) | _Leverage: pytest documentation, design.md testing strategy section, existing Python package structure_ | Success: tests/ directory created with proper structure, all stub files have basic test class/function templates, conftest.py contains useful fixtures, pytest discovers all test files with --collect-only | Instructions: After creating test structure, edit tasks.md to change this task from [ ] to [x] when complete_

- [ ] 26. Write unit tests for zlibrary_downloader/client.py
  - File: `packages/python/zlibrary-downloader/tests/test_client.py`
  - Write tests for Zlibrary class initialization
  - Test login methods with mocked requests
  - Test search functionality with mocked API responses
  - Test downloadBook with mocked file download
  - Aim for >80% coverage of client.py
  - Purpose: Ensure API client reliability
  - _Leverage: pytest, pytest-mock, test_client.py stub from task 25_
  - _Requirements: 7_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python QA Engineer with expertise in API testing and mocking | Task: Write comprehensive unit tests for zlibrary_downloader/client.py following requirement 7, achieving >80% coverage, mocking all HTTP requests, testing success and error scenarios | Restrictions: Must use pytest framework, must mock requests library (use pytest-mock or unittest.mock), must not make real API calls, must test both success and failure paths, must follow AAA pattern (Arrange-Act-Assert) | _Leverage: test_client.py stub from task 25, existing client.py code, pytest fixtures from conftest.py, design.md testing strategy_ | Success: All major Zlibrary methods tested, >80% coverage of client.py, tests pass with pytest, mocking properly isolates unit tests, both success and error scenarios covered | Instructions: After writing tests and verifying coverage, edit tasks.md to change this task from [ ] to [x] when complete_

- [ ] 27. Write unit tests for validator scripts
  - Files: `scripts/tests/test_validators.py`
  - Create tests directory under scripts/
  - Test line count validator with sample files
  - Test function size validator with sample Python/Rust code
  - Test complexity parsers with sample JSON
  - Verify validators correctly identify violations
  - Purpose: Ensure validator scripts work correctly
  - _Leverage: pytest, sample code snippets_
  - _Requirements: 4, 7_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Python QA Engineer with expertise in testing validation logic | Task: Create comprehensive unit tests for custom validator scripts following requirements 4 and 7, testing line count, function size, and complexity validators with various scenarios | Restrictions: Must create scripts/tests/ directory, must use pytest, must test both passing and failing scenarios, must test edge cases (exactly at limit, just over limit), must use temporary files for testing | _Leverage: pytest tmpdir fixture, validators from tasks 9-10, complexity parsers from tasks 6 and 8_ | Success: All validators tested with multiple scenarios, tests cover edge cases and boundary conditions, tests verify correct exit codes, tests verify error message format, all tests pass | Instructions: After writing tests and verifying they pass, edit tasks.md to change this task from [ ] to [x] when complete_

- [ ] 28. Run full QA validation and generate coverage report
  - Run pre-commit on all files: pre-commit run --all-files
  - Run pytest with coverage: pytest --cov --cov-report=html
  - Run cargo test for Rust
  - Verify all checks pass
  - Generate and review coverage report
  - Document any remaining issues
  - Purpose: Validate complete QA implementation
  - _Leverage: All configured tools and tests_
  - _Requirements: All_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: QA Engineer with expertise in comprehensive testing and validation | Task: Perform complete QA validation following all requirements, running all quality checks, tests, and generating coverage reports to verify entire QA compliance implementation is working | Restrictions: Must run on clean working directory (git status should be clean except for any documented exceptions), must document any failures or warnings, must achieve >80% Python test coverage, must verify all pre-commit hooks pass | _Leverage: All tools configured in previous tasks, pytest, pre-commit, cargo test, coverage reports_ | Success: pre-commit run --all-files passes completely, pytest achieves >80% coverage, cargo test passes, coverage report generated in htmlcov/, no critical issues remain, all QA goals from requirements.md achieved | Instructions: Document final validation results, address any remaining issues, edit tasks.md to change this task from [ ] to [x] when validation complete_

- [ ] 29. Create QA compliance documentation
  - File: `docs/qa-compliance.md` (create docs/ if needed)
  - Document all QA tools and their configurations
  - Explain pre-commit hook workflow
  - Document how to bypass hooks (emergency only)
  - Include troubleshooting guide
  - Document code metrics and thresholds
  - Purpose: Provide comprehensive QA reference documentation
  - _Leverage: All QA configurations and tools_
  - _Requirements: 9_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Technical Writer with expertise in development process documentation | Task: Create comprehensive QA compliance documentation following requirement 9, documenting all tools, configurations, workflows, and troubleshooting for the QA compliance system | Restrictions: Must be clear and concise, must include concrete examples, must cover all tools (pre-commit, mypy, black, flake8, clippy, rustfmt, complexity checkers), must explain when and why to bypass hooks, must document threshold values (400/30/10) | _Leverage: All configurations from tasks 1-4, all tools from design.md, all validators from tasks 5-10, requirements.md and design.md for context_ | Success: Documentation is comprehensive and well-structured, all tools documented with examples, troubleshooting guide covers common issues, bypass procedures clearly explained with warnings, code metrics clearly documented | Instructions: After creating documentation, edit tasks.md to change this task from [ ] to [x] when complete_

- [ ] 30. Final review and cleanup
  - Review all configuration files for consistency
  - Verify all scripts are executable (chmod +x)
  - Check all documentation is up to date
  - Remove any temporary files or test artifacts
  - Verify git status is clean (no untracked files except .git/hooks/)
  - Create final validation commit
  - Purpose: Ensure QA implementation is production-ready
  - _Leverage: All previous tasks_
  - _Requirements: All_
  - _Prompt: Implement the task for spec qa-compliance, first run spec-workflow-guide to get the workflow guide then implement the task: Role: Senior Developer with expertise in code review and quality assurance | Task: Perform final review and cleanup of QA compliance implementation covering all requirements, ensuring everything is consistent, documented, tested, and production-ready | Restrictions: Must review every configuration file for accuracy, must verify executable permissions on scripts, must test one final time that pre-commit works, must not break any existing functionality, must ensure documentation matches implementation | _Leverage: All tasks completed previously, git status, ls -la scripts/ to check permissions, pre-commit run --all-files for final check_ | Success: All configuration files reviewed and consistent, all scripts executable, all documentation accurate and complete, no temporary files or artifacts remain, pre-commit runs successfully, ready for team rollout and enforcement | Instructions: After final review and cleanup, edit tasks.md to change this task from [ ] to [x] when complete, then mark all tasks as done_
