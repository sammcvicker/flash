# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2025-06-08

### Added
- Comprehensive test suite with 36+ tests
- GitHub Actions CI/CD pipeline
- Code quality tools (Ruff, mypy)
- Pre-commit hooks for automated quality checks
- Contributing guidelines and development documentation
- MIT license for open source distribution
- Enhanced PyPI metadata with proper classifiers and keywords

### Fixed
- CSV parsing edge cases with Unicode and malformed data
- Cross-platform audio playback compatibility
- Error handling for missing OpenAI API keys
- Version consistency across project files

## [0.1.0]

### Added
- Initial release of Flash flashcard CLI tool
- CSV-based flashcard system with flexible column mapping
- Text-to-speech support via OpenAI API
- Multi-language voice support
- Audio caching to minimize API costs
- Shuffle, confirmation, and recursive learning modes
- Cross-platform audio playback (macOS, Linux, Windows)

### Features
- Support for any CSV format with configurable columns
- 7 voice options (alloy, echo, fable, onyx, nova, shimmer, coral)
- 14 language support for text-to-speech
- Intelligent caching system in ~/.flash directory
- Command-line interface with comprehensive options 