# Flash

A simple command-line flashcard application that uses CSV files for studying.

## Installation

With pip:

```bash
pip install .
```

With uv:

```bash
uv pip install .
```

## Usage

After installation, run the flashcard application with a CSV file:

```bash
flash path/to/your/flashcards.csv
```

### Options

- `-s, --shuffle`: Shuffle the flashcards
- `-c, --confirm`: Require typing the correct answer when wrong to move to the next card

### Examples

Basic usage:

```bash
flash sample.csv
```

With shuffling:

```bash
flash sample.csv --shuffle
```

With confirmation:

```bash
flash sample.csv --confirm
```

With both options:

```bash
flash sample.csv --shuffle --confirm
```

## CSV Format

The CSV file should have at least two columns:

- First column: Question/prompt
- Second column: Answer

Example CSV content:

```
What is the capital of France?,Paris
What is 2+2?,4
Who wrote "Romeo and Juliet"?,Shakespeare
```
