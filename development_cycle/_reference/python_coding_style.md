# Python Coding Style Guide

## File Structure & Organization
- Begin files with comprehensive docstrings that explain:
  - Purpose of the module/script
  - Features and capabilities
  - Usage examples with real command samples
  - Input/output specifications
  - Common pitfalls or edge cases

- Organize imports in clear groups:
  ```python
  # Standard library imports
  import json
  import os
  import time
  
  # Third-party imports
  import aiohttp
  import tiktoken
  
  # Local application imports
  from myapp.utils import helper
  ```

- Place main execution logic in a clearly defined async function that handles the core workflow
- Use descriptive function and variable names that indicate their purpose
- Structure files in a logical progression:
  1. Imports
  2. Main processing function(s)
  3. Data structure definitions (classes/dataclasses)
  4. Helper functions
  5. Main execution block with `if __name__ == "__main__"`

## Async Programming Patterns
- Use `asyncio` for I/O-bound operations, especially when dealing with API calls
- Create a main async function that orchestrates the workflow
- Use `asyncio.Queue` for managing concurrent tasks with limited resources
- Use `async with` context managers for proper resource cleanup
- Create tasks with `asyncio.create_task()` for concurrent execution
- Implement appropriate sleep intervals to prevent CPU hogging during idle periods
- Handle rate limits with exponential backoff or timed pauses

## Data Structures
- Use dataclasses for structured data, especially when tracking multiple fields
- Include type hints for all fields in dataclasses
- Use clear field defaults when appropriate
- Add docstrings to dataclasses that explain their purpose
- Implement methods in dataclasses when they logically operate on the data they contain

## Error Handling
- Use try/except blocks for operations that may fail
- Log detailed error information for debugging
- Implement retry mechanisms for transient failures
- Track error statistics for monitoring
- Handle rate limit errors specifically with cooldown periods
- Use appropriate logging levels for different error severities

## Function Design
- Give functions descriptive names that indicate what they do
- Add clear docstrings to all functions explaining:
  - What the function does
  - Parameters and their types
  - Return values and their types
  - Exceptions that might be raised
- Keep functions focused on a single responsibility
- Use type hints for all parameters and return values
- Avoid side effects where possible; make functions pure when appropriate

## Concurrency Control
- Implement rate limiting with token bucket algorithms
- Track available capacity for resources (requests, tokens, etc.)
- Dynamically adjust request timing based on capacity
- Use queues for managing backlogged tasks
- Implement cooldown periods after hitting rate limits

## Command-Line Interface
- Use `argparse` for processing command-line arguments
- Provide sensible defaults for optional parameters
- Include clear help text for each parameter
- Support environment variables for sensitive values
- Validate inputs before processing

## Logging
- Use the `logging` module with appropriate levels
- Configure logging level via command-line arguments
- Include contextual information in log messages (request IDs, timestamps)
- Use different levels appropriately:
  - DEBUG: Detailed information for diagnosis
  - INFO: Confirmation that things are working as expected
  - WARNING: Something unexpected happened but the program can continue
  - ERROR: Program couldn't perform a function due to a serious problem
- Log the start and completion of significant operations

## API Interaction
- Create reusable API client abstractions
- Handle rate limits gracefully with retries and backoffs
- Process API responses consistently
- Extract common patterns into helper functions
- Track API usage metrics
- Implement robust error handling for API calls

## File Operations
- Use context managers (`with` statements) for file operations
- Process large files incrementally to manage memory usage
- Implement atomic writes where possible
- Use appropriate error handling for file operations
- Support compressed file formats when handling large datasets

## Performance Considerations
- Process data in batches where appropriate
- Use generators for memory-efficient processing of large datasets
- Implement caching for expensive operations
- Monitor and track performance metrics
- Use appropriate data structures for quick lookups (dictionaries, sets)
- Balance concurrency to maximize throughput while respecting limits

## Example Implementation Patterns

### Status Tracking
```python
@dataclass
class StatusTracker:
    """Tracks operational statistics during processing."""
    requests_completed: int = 0
    requests_failed: int = 0
    total_tokens_processed: int = 0
    rate_limit_errors: int = 0
```

### Rate Limiting
```python
# Update available capacity
current_time = time.time()
seconds_since_update = current_time - last_update_time
available_request_capacity = min(
    available_request_capacity + max_requests_per_minute * seconds_since_update / 60.0,
    max_requests_per_minute
)
last_update_time = current_time
```

### Async Request Processing
```python
async def process_request(request_data, session, tracker):
    """Process a single API request asynchronously."""
    try:
        async with session.post(url=endpoint, json=request_data) as response:
            result = await response.json()
            tracker.requests_completed += 1
            return result
    except Exception as e:
        tracker.requests_failed += 1
        return {"error": str(e)}
```

### Main Execution Pattern
```python
if __name__ == "__main__":
    args = parse_arguments()
    asyncio.run(main_processing_function(
        input_file=args.input,
        output_file=args.output,
        max_concurrency=args.concurrency
    ))
```