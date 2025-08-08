# Contributing to SAP RFC MCP Server

Thank you for your interest in contributing to the SAP RFC MCP Server! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** from `main`
4. **Make your changes** following our guidelines
5. **Test your changes** thoroughly
6. **Submit a pull request**

## 📋 Development Setup

### Prerequisites

- Python 3.9 or higher
- SAP NetWeaver RFC SDK
- Git
- Access to a SAP system (for integration testing)

### Environment Setup

```bash
# Clone your fork
git clone https://github.com/thupalo/sap-rfc-mcp-server.git
cd sap-rfc-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Configuration for Development

Create a `.env.dev` file for development:

```env
# Development SAP Connection
SAP_ASHOST=dev-sap-hostname
SAP_SYSNR=00
SAP_CLIENT=100
SAP_USER=dev-username
SAP_PASSWD=dev-password
SAP_LANG=EN

# Development Settings
DEBUG=true
LOG_LEVEL=DEBUG
CACHE_DIR=./dev_cache
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sap_rfc_mcp_server --cov-report=html

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests (requires SAP access)
pytest -m "not slow"    # Skip slow tests

# Run tests for specific module
pytest tests/test_metadata_manager.py
```

### Writing Tests

- **Unit tests**: Test individual functions/methods in isolation
- **Integration tests**: Test SAP connectivity and real RFC calls
- **End-to-end tests**: Test complete workflows

Example test structure:

```python
import pytest
from sap_rfc_mcp_server.metadata_manager import RFCMetadataManager

class TestRFCMetadataManager:
    @pytest.fixture
    def metadata_manager(self):
        # Setup test instance
        pass
    
    @pytest.mark.unit
    def test_language_code_mapping(self, metadata_manager):
        # Test language code conversion
        assert metadata_manager._get_sap_language_code("EN") == "E"
        assert metadata_manager._get_sap_language_code("PL") == "L"
    
    @pytest.mark.integration
    def test_function_metadata_retrieval(self, metadata_manager):
        # Test real SAP metadata retrieval
        metadata = metadata_manager.get_function_metadata("RFC_READ_TABLE")
        assert metadata is not None
        assert "function_name" in metadata
```

## 🎨 Code Style

### Formatting Tools

We use the following tools to maintain code quality:

```bash
# Format code
black sap_rfc_mcp_server tests examples
isort sap_rfc_mcp_server tests examples

# Lint code
flake8 sap_rfc_mcp_server tests
mypy sap_rfc_mcp_server

# Pre-commit (runs all checks)
pre-commit run --all-files
```

### Style Guidelines

- **Line length**: 88 characters (Black default)
- **Imports**: Use isort with Black profile
- **Type hints**: Required for all public functions
- **Docstrings**: Google style for all public functions/classes
- **Variable naming**: snake_case for variables, PascalCase for classes

Example function:

```python
def get_function_metadata(
    self, 
    function_name: str, 
    language: str = "EN"
) -> Optional[Dict[str, Any]]:
    """
    Retrieve metadata for a specific RFC function.
    
    Args:
        function_name: Name of the RFC function
        language: Language code for descriptions (EN, PL, DE, etc.)
        
    Returns:
        Function metadata dictionary or None if not found
        
    Raises:
        SAPConnectionError: If SAP connection fails
        ValueError: If function_name is empty
        
    Example:
        >>> manager = RFCMetadataManager(connection_params)
        >>> metadata = manager.get_function_metadata("RFC_READ_TABLE", "EN")
        >>> print(metadata["description"])
    """
```

## 📝 Documentation

### Updating Documentation

- **Code documentation**: Update docstrings for any new/changed functions
- **API documentation**: Update if adding new MCP tools or HTTP endpoints
- **README**: Update for significant feature additions
- **Changelog**: Add entries for all changes

### Documentation Style

- Use clear, concise language
- Include code examples for complex features
- Update both inline documentation and external docs
- Test all code examples to ensure they work

## 🔍 Pull Request Guidelines

### Before Submitting

- [ ] All tests pass (`pytest`)
- [ ] Code is formatted (`black`, `isort`)
- [ ] No linting errors (`flake8`, `mypy`)
- [ ] Documentation updated
- [ ] Changelog entry added
- [ ] Commit messages follow convention

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Changelog updated
```

### Commit Message Convention

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

Examples:
```
feat(metadata): add version-aware language code mapping
fix(cache): resolve TTL calculation bug
docs(readme): update installation instructions
test(integration): add SAP R/3 4.5B compatibility tests
```

## 🐛 Bug Reports

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Update to latest version** to see if bug is fixed
3. **Test in clean environment** to isolate the issue

### Bug Report Template

```markdown
**Bug Description**
Clear description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Configure with '...'
2. Call function '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Environment**
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python version: [e.g., 3.9.7]
- SAP system: [e.g., R/3 4.5B, ECC 6.0]
- Package version: [e.g., 1.0.0]

**Additional Context**
- Error logs
- Configuration (sanitized)
- Screenshots if applicable
```

## 💡 Feature Requests

### Before Requesting

1. **Check existing feature requests** to avoid duplicates
2. **Consider the scope** - does it fit the project goals?
3. **Think about implementation** - how would it work?

### Feature Request Template

```markdown
**Feature Description**
Clear description of the desired feature.

**Use Case**
Explain why this feature would be useful.

**Proposed Solution**
Describe how you envision this working.

**Alternatives Considered**
Other approaches you've considered.

**Additional Context**
- Related issues
- External resources
- Examples from other projects
```

## 🎯 Development Focus Areas

### High Priority
- Performance improvements
- SAP version compatibility
- Security enhancements
- Error handling improvements

### Medium Priority
- Additional MCP tools
- New HTTP endpoints
- Documentation improvements
- Test coverage expansion

### Future Considerations
- GraphQL API
- WebSocket support
- Additional language support
- Plugin system

## 🔐 Security

### Reporting Security Issues

**Do not report security vulnerabilities through public issues.**

Email security issues to: security@sap-rfc-mcp.example.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Guidelines

- Never commit credentials or sensitive data
- Use environment variables for configuration
- Validate all user inputs
- Follow secure coding practices
- Keep dependencies updated

## 📞 Getting Help

### Development Questions
- 💬 [GitHub Discussions](https://github.com/thupalo/sap-rfc-mcp-server/discussions)
- 📧 Email: dev@sap-rfc-mcp.example.com

### SAP-Specific Questions
- 📚 [SAP RFC SDK Documentation](https://help.sap.com/doc/saphelp_nwpi711/7.1.1/en-US/48/a994a77e28674be10000000a421937/frameset.htm)
- 🐍 [pyrfc Documentation](https://sap.github.io/pyrfc/)

## 🏆 Recognition

Contributors will be recognized in:
- CHANGELOG.md for each release
- README.md contributors section
- GitHub contributor graph
- Special mentions for significant contributions

Thank you for contributing to SAP RFC MCP Server! 🎉
