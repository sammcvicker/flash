# Contributing to Flash

Thank you for your interest in contributing to Flash! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) for dependency management

### Setting up your development environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/flash.git
   cd flash
   ```

2. **Install dependencies**
   ```bash
   uv pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks** (optional but recommended)
   ```bash
   uv run pre-commit install
   ```

4. **Verify your setup**
   ```bash
   uv run pytest tests/ -v
   ```

## Development Workflow

### Before making changes

1. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make sure tests pass:
   ```bash
   uv run pytest tests/
   ```

### Making changes

1. **Write tests first** - We follow test-driven development
2. **Keep changes focused** - One feature/fix per pull request
3. **Follow coding standards** - See below for details

### Code Quality Standards

We maintain high code quality through automated tools:

#### Formatting
```bash
# Format code with black
uv run black flash/ tests/

# Sort imports with isort
uv run isort flash/ tests/
```

#### Linting
```bash
# Check code style with flake8
uv run flake8 flash/ tests/

# Type checking with mypy
uv run mypy flash/
```

#### Testing
```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=flash --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_cli.py -v
```

### Testing Guidelines

- **Write tests for all new functionality**
- **Maintain or improve code coverage** - aim for >90%
- **Use descriptive test names** that explain what is being tested
- **Mock external dependencies** (like OpenAI API calls)
- **Test both success and failure cases**

#### Test Structure
```python
def test_function_name_expected_behavior(self):
    """Test that function_name does expected_behavior when condition."""
    # Arrange
    setup_test_data()
    
    # Act
    result = function_under_test()
    
    # Assert
    assert result == expected_value
```

### Voice Feature Testing

The voice feature requires special consideration:

- **Always mock OpenAI API calls** in tests
- **Don't use real API keys** in test environment
- **Test both audio generation and playback**
- **Test graceful degradation** when voice features fail

## Pull Request Process

### Before submitting

1. **Run the full test suite**:
   ```bash
   uv run pytest tests/
   ```

2. **Check code quality**:
   ```bash
   uv run black --check flash/ tests/
   uv run isort --check-only flash/ tests/
   uv run flake8 flash/ tests/
   uv run mypy flash/
   ```

3. **Update documentation** if needed

### Pull Request Guidelines

1. **Clear title and description**
   - Use descriptive titles
   - Explain what changes you made and why
   - Reference any related issues

2. **Keep PRs focused**
   - One feature/fix per PR
   - Avoid mixing code style changes with functionality changes

3. **Include tests**
   - All new functionality must have tests
   - Bug fixes should include regression tests

4. **Update documentation**
   - Update README.md if you add new features
   - Add docstrings to new functions/classes
   - Update type hints

### Example PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Tested on multiple platforms (if applicable)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-reviewed the code
- [ ] Added comments for complex logic
- [ ] Updated documentation
```

## Project Structure

```
flash/
├── flash/           # Main package
│   ├── __init__.py
│   ├── cli.py       # Command-line interface
│   └── voice.py     # Text-to-speech functionality
├── tests/           # Test suite
│   ├── fixtures/    # Test data files
│   ├── test_cli.py
│   └── test_voice.py
├── .github/         # GitHub Actions workflows
├── pyproject.toml   # Project configuration
└── README.md
```

## Coding Standards

### Python Style
- **Follow PEP 8** with 88-character line length
- **Use type hints** for all function parameters and return values
- **Write descriptive docstrings** using Google style
- **Prefer explicit over implicit**

### Error Handling
- **Use custom exceptions** instead of generic ones when appropriate
- **Provide helpful error messages** with suggestions for fixes
- **Handle edge cases gracefully**
- **Use context managers** for resource management

### Documentation
- **Document all public functions** with docstrings
- **Include usage examples** in docstrings
- **Keep README.md up to date**
- **Comment complex logic**

## Common Development Tasks

### Adding a new feature

1. **Plan the feature**
   - Consider backward compatibility
   - Think about edge cases
   - Design the API

2. **Write tests first**
   ```bash
   # Create test file
   touch tests/test_new_feature.py
   
   # Write failing tests
   # Implement feature
   # Make tests pass
   ```

3. **Implement the feature**
   - Follow existing code patterns
   - Add proper error handling
   - Include type hints and docstrings

4. **Update documentation**
   - Add to README.md if user-facing
   - Update help text if CLI-related

### Debugging

```bash
# Run tests with verbose output
uv run pytest tests/ -v -s

# Run specific test with debugging
uv run pytest tests/test_cli.py::TestClass::test_method -v -s

# Add print statements or use pdb
import pdb; pdb.set_trace()
```

## Release Process

Releases are handled by maintainers:

1. Version bump in `pyproject.toml` and `__init__.py`
2. Update CHANGELOG.md
3. Create GitHub release
4. Automated PyPI publication via GitHub Actions

## Getting Help

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and general discussion
- **Code Review** - All maintainers help with PR reviews

## Code of Conduct

Please note that this project follows the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct. By participating, you are expected to uphold this code.

Thank you for contributing to Flash! 🚀 