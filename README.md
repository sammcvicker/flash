# Flash

[![CI](https://github.com/yourusername/flash/workflows/CI/badge.svg)](https://github.com/yourusername/flash/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A highly configurable multi-sided flashcard system for the command line that works with any CSV data. Whether you're studying languages, memorizing facts, or learning code snippets, Flash adapts to your data and learning style.

## Features

- **Flexible data handling**: Works with any CSV format and lets you specify which columns to use
- **Multi-sided cards**: Support for question/answer pairs from any columns in your data
- **Audio support**: Read flashcards aloud in multiple languages using OpenAI's Text-to-Speech
- **Custom learning flow**: Options for shuffling, recursive practice, and confirmation modes
- **Intelligent caching**: Audio files are cached to minimize API calls and costs

## Installation

### Using pip

```bash
# From the project directory
pip install .
```

### Using uv

```bash
# From the project directory
uv pip install .
```

### Building a distributable package

```bash
# Build the package
uv build

# Install globally with pipx
pipx install dist/flash-0.1.0-py3-none-any.whl

# Or install with pip
pip install dist/flash-0.1.0-py3-none-any.whl
```

## Usage

After installation, run the flashcard application with a CSV file:

```bash
flash path/to/your/flashcards.csv
```

### Options

- `-s, --shuffle`: Shuffle the flashcards
- `-c, --confirm`: Require typing the correct answer when wrong to move to the next card
- `-r, --recursive`: Recursively test incorrect cards until all are answered correctly
- `-f, --from COL`: Column index to use for questions (0-based, default: 0)
- `-t, --to COL`: Column index to use for answers (0-based, default: 1)
- `-v, --voice COL`: Column index to read aloud using text-to-speech (0-based)
- `--voice-type VOICE`: Voice to use for text-to-speech (default: onyx)
- `-l, --language LANG`: Language to use for text-to-speech (e.g., japanese, spanish)

### Voice Feature

The voice feature provides audio pronunciation of your cards, which is particularly helpful for language learning.

#### Requirements
1. The OpenAI Python package (automatically installed as a dependency)
2. An OpenAI API key set as the `OPENAI_API_KEY` environment variable (if you plan on using the voice feature)

#### Available voices
- alloy
- echo
- fable
- onyx (default)
- nova
- shimmer
- coral

#### Available languages
- english
- japanese
- chinese
- korean
- spanish
- french
- german
- italian
- russian
- portuguese
- arabic
- hindi
- thai
- vietnamese

Audio files are cached in the `~/.flash` directory to avoid unnecessary API calls and reduce costs. If the voice feature encounters an error, you'll be prompted to continue without audio.

### Examples

Basic usage:

```bash
flash sample.csv
```

Using different columns (questions from column 2, answers from column 3):

```bash
flash sample.csv --from 2 --to 3
```

With shuffling and confirmation:

```bash
flash sample.csv --shuffle --confirm
```

Recursive practice (repeat incorrect cards until mastered):

```bash
flash sample.csv --recursive
```

Using the voice feature (reads questions aloud):

```bash
flash sample.csv --voice 0
```

Using the voice feature with a specific voice and language:

```bash
flash sample.csv --voice 1 --voice-type coral --language japanese
```

Full-featured example:

```bash
flash sample.csv --shuffle --confirm --recursive --voice 0 --language chinese
```

## CSV Format

The CSV file can have any number of columns. By default:
- First column (index 0): Question/prompt
- Second column (index 1): Answer

You can specify different columns using the `--from` and `--to` options.

### Example CSV content

```
What is the capital of France?,Paris
What is 2+2?,4
Who wrote "Romeo and Juliet"?,Shakespeare
```

### Multi-column example

```
1,一,one,いち
2,二,two,に
3,三,three,さん
```

Using this CSV, you could practice:
- Numbers to Japanese: `flash numbers.csv --from 0 --to 3 --voice 3 --language japanese`
- Kanji to English: `flash numbers.csv --from 1 --to 2`
- English to Kanji: `flash numbers.csv --from 2 --to 1`
