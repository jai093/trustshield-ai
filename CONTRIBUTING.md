# Contributing to TrustShield AI

We love your input! We want to make contributing to TrustShield AI as easy and transparent as possible.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots and animated GIFs if possible**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and the proposed behavior**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Follow the Python/JavaScript/TypeScript styleguides
* Include appropriate test cases
* End all files with a newline
* Document new code based on the Documentation Styleguide

## Development Setup

1. Fork the repository
2. Clone your fork locally
3. Create a new branch: `git checkout -b feature/my-feature`
4. Make your changes
5. Add tests for your changes
6. Run tests: `npm test` or `pytest`
7. Commit: `git commit -am 'Add my feature'`
8. Push: `git push origin feature/my-feature`
9. Create a Pull Request

## Styleguides

### Python Code

* Follow PEP 8
* Use type hints
* Max line length: 100 characters
* Use meaningful variable names

```python
def analyze_email(email: EmailData) -> AnalysisResult:
    """
    Analyze email for phishing.
    
    Args:
        email: Email data to analyze
        
    Returns:
        Analysis result with risk score
    """
    pass
```

### TypeScript Code

* Follow ESLint configuration
* Use strict type checking
* Use meaningful variable names
* Document complex logic

```typescript
interface EmailData {
  sender: string;
  subject: string;
  body: string;
}

function analyzeEmail(email: EmailData): Promise<AnalysisResult> {
  // Implementation
}
```

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Good examples:
* `Add email extraction agent`
* `Fix URL parsing bug in intelligence agent`
* `Improve documentation for API endpoints`

## Additional Notes

### Issue and Pull Request Labels

* `bug` - Something isn't working
* `enhancement` - New feature or request
* `documentation` - Improvements or additions to documentation
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed
* `question` - Further information is requested

## Questions?

Feel free to open an issue tagged with `question` if you have any questions.

Thank you for contributing to TrustShield AI!
