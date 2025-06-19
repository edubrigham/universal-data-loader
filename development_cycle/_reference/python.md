Python-Specific Code Generation Rules
1. Python Style
style_rules:
  - Follow PEP 8 conventions
  - Use type hints (Python 3.6+)
  - Use f-strings for string formatting
  - 4 spaces for indentation
  - Maximum line length of 88 characters (black formatter)

# 2. Python Idioms
idiom_rules:
  - Use list/dict comprehensions when clear
  - Prefer generator expressions for large sequences
  - Use context managers (with statements)
  - Leverage itertools and functools
  - Use pathlib over os.path

# 3. Type System
type_rules:
  - Use typing.Optional over None defaults
  - Leverage typing.Protocol for duck typing
  - Use typing.Final for constants
  - Define custom types with typing.NewType
  - Use collections.abc over built-in types

# 4. Data Structures
data_rules:
  - Use dataclasses for data containers and meaningful abstractions
  - Design dataclasses to combine related data with behavior when appropriate
  - Use dataclasses for managing state across the application
  - Prefer NamedTuple over tuple
  - Use sets for membership testing
  - Use defaultdict for nested structures
  - Leverage enum.Enum for constants

# 5. Exception Handling
exception_rules:
  - Create custom exception hierarchies
  - Use contextlib for complex cleanup
  - Catch specific exceptions
  - Use else clause in try blocks
  - Implement proper cleanup in finally

# 6. Async Programming
async_rules:
  - Use asyncio for IO-bound operations
  - Implement proper cancellation
  - Use async context managers
  - Prefer async/await over callbacks
  - Handle event loop properly

# 7. Package Structure
structure_rules:
  - Use __init__.py for exports
  - Implement proper package boundaries
  - Use relative imports within package
  - Keep modules focused and small
  - Use __all__ for explicit exports

# 8. File Structure
file_structure_rules:
  - Begin files with a docstring explaining purpose, features, and usage examples
  - Group imports logically (standard library, third-party, local)
  - Place main function near the top to tell the "story" of the code
  - Separate supporting classes and dataclasses with clear responsibilities
  - Group utility functions by purpose
  - Place script entry point at the bottom of the file
  - Use clear section headers as comments to delineate major sections

# 9. Testing
test_rules:
  - Use pytest as testing framework
  - Implement fixtures for setup
  - Use parametrize for multiple cases
  - Mock external dependencies
  - Use proper assert messages

# 10. Documentation
doc_rules:
  - Use Google-style docstrings for all modules, classes, and functions
  - Begin each module with a comprehensive docstring that includes:
    * Clear purpose statement
    * Features and capabilities
    * Usage examples with code
    * Command-line examples if applicable
    * Input/output specifications
    * Common pitfalls and edge cases
  - Document all public APIs
  - Include type information in docstrings
  - Document exceptions raised
  - Add usage examples for complex functions
  - Document parameters thoroughly with meaningful descriptions
  - Include return value documentation

# 11. Dependencies
dependency_rules:
  - Use requirements.txt or pyproject.toml
  - Pin exact versions in production
  - Use virtual environments
  - Minimize external dependencies
  - Document all requirements

# 12. Performance
performance_rules:
  - Use generators for large datasets
  - Leverage numpy for numerical ops
  - Profile before optimizing
  - Use proper data structures
  - Consider Cython for hotspots

# 13. Security
security_rules:
  - Use secrets module for crypto
  - Sanitize all inputs
  - Use proper password hashing
  - Implement proper RBAC
  - Use environment variables

# 14. Concurrency
concurrency_rules:
  - Prefer asyncio over threads
  - Use multiprocessing for CPU-bound
  - Implement proper locks
  - Use Queue for thread communication
  - Handle shutdown properly

# 15. Logging
logging_rules:
  - Use structured logging
  - Implement proper log levels
  - Add context information
  - Configure handlers properly
  - Use proper formatting

# 16. CLI Applications
cli_rules:
  - Use argparse or click
  - Implement proper help messages
  - Add command completion
  - Handle signals properly
  - Provide proper exit codes

# 17. RAG-Specific Patterns
rag_rules:
  - Implement stateless workflow nodes for LangGraph
  - Structure prompts with clear input/output contracts
  - Use structured parsing for LLM outputs
  - Separate chain definitions from execution logic
  - Implement consistent error handling in LLM chains
  - Use callback handlers for state tracking
  - Cache expensive embedding operations
  - Implement graceful fallbacks for LLM failures
  - Use batched processing for document operations
  - Structure evaluation metrics for interpretability