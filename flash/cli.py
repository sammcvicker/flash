#!/usr/bin/env python3

import click
import csv
import random
import sys
import os
from typing import List, Tuple, Dict, Optional

try:
    from .voice import VoiceReader, AVAILABLE_VOICES, DEFAULT_VOICE, LANGUAGE_INSTRUCTIONS
    VOICE_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    VOICE_AVAILABLE = False
    LANGUAGE_INSTRUCTIONS = {}


def load_cards(
    csv_path: str, from_col: int = 0, to_col: int = 1
) -> List[Tuple[str, str]]:
    """Load flashcards from a CSV file.

    Args:
        csv_path: Path to the CSV file
        from_col: Column index to use for questions (0-based)
        to_col: Column index to use for answers (0-based)
    """
    cards = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) > max(from_col, to_col):
                    cards.append((row[from_col], row[to_col]))
    except FileNotFoundError:
        click.echo(f"Error: File '{csv_path}' not found.")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error reading CSV file: {e}")
        sys.exit(1)

    if not cards:
        click.echo("No valid flashcards found in the CSV file.")
        sys.exit(1)

    return cards


def run_round(
    cards: List[Tuple[str, str]], 
    confirm: bool, 
    round_num: int = 1,
    voice_col: Optional[int] = None,
    voice: Optional[str] = None,
    language: Optional[str] = None
) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """
    Run a single round of flashcards.

    Args:
        cards: List of (question, answer) tuples
        confirm: Whether to require typing the correct answer when wrong
        round_num: The current round number
        voice_col: Column to read aloud using text-to-speech (0-based)
        voice: Voice to use for text-to-speech
        language: Language to use for text-to-speech

    Returns:
        Tuple of (correct_cards, incorrect_cards)
    """
    correct_cards = []
    incorrect_cards = []
    
    voice_reader = None
    voice_enabled = VOICE_AVAILABLE and voice_col is not None
    
    if voice_enabled:
        try:
            voice_reader = VoiceReader()
        except Exception as e:
            click.echo(click.style(f"Error initializing voice reader: {e}", fg="red"))
            if click.confirm("Continue without voice?", default=True):
                voice_enabled = False
            else:
                sys.exit(1)

    click.echo(f"\n--- Round {round_num} ({len(cards)} cards) ---")

    for i, (question, answer) in enumerate(cards, 1):
        # Play audio if requested and available
        if voice_enabled and voice_reader is not None:
            try:
                text_to_speak = question if voice_col == 0 else answer
                voice_reader.speak(text_to_speak, voice or DEFAULT_VOICE, language)
            except Exception as e:
                click.echo(click.style(f"Voice error: {e}", fg="red"))
                if click.confirm("Continue without voice?", default=True):
                    voice_enabled = False
                else:
                    sys.exit(1)
        
        click.echo(f"\n[{i}/{len(cards)}] {question}")
        user_answer = click.prompt("Your answer", type=str)

        if user_answer.strip().lower() == answer.strip().lower():
            click.echo(click.style("✔", fg="green", bold=True))
            correct_cards.append((question, answer))
        else:
            click.echo(click.style(f"✘ {answer}", fg="red", bold=True))
            incorrect_cards.append((question, answer))

            if confirm:
                while True:
                    confirmation = click.prompt(
                        "Type the correct answer to continue", type=str
                    )
                    if confirmation.strip().lower() == answer.strip().lower():
                        break
                    click.echo(click.style("✘", fg="red", bold=True))

    if cards:
        correct_count = len(correct_cards)
        total_count = len(cards)
        click.echo(
            f"\nRound {round_num}: You got {correct_count} out of {total_count} correct ({correct_count/total_count*100:.1f}%)."
        )

    return correct_cards, incorrect_cards


@click.command()
@click.argument("csv_path", type=click.Path(exists=True))
@click.option("-s", "--shuffle", is_flag=True, help="Shuffle the flashcards.")
@click.option(
    "-c",
    "--confirm",
    is_flag=True,
    help="Require typing the correct answer when wrong.",
)
@click.option(
    "-r",
    "--recursive",
    is_flag=True,
    help="Recursively test on incorrect cards until all are answered correctly.",
)
@click.option(
    "-f",
    "--from",
    "from_col",
    type=int,
    default=0,
    help="Column index to use for questions (0-based, default: 0).",
)
@click.option(
    "-t",
    "--to",
    "to_col",
    type=int,
    default=1,
    help="Column index to use for answers (0-based, default: 1).",
)
@click.option(
    "-v",
    "--voice",
    "voice_col",
    type=int,
    help="Column index to read aloud using text-to-speech (0-based).",
)
@click.option(
    "--voice-type",
    type=str,
    default=DEFAULT_VOICE if VOICE_AVAILABLE else None,
    help=f"Voice to use for text-to-speech. Available voices: {', '.join(AVAILABLE_VOICES) if VOICE_AVAILABLE else 'none'}."
)
@click.option(
    "-l",
    "--language",
    type=str,
    help=f"Language to use for text-to-speech. Available languages: {', '.join(LANGUAGE_INSTRUCTIONS.keys()) if VOICE_AVAILABLE else 'none'}."
)
def flash(
    csv_path: str,
    shuffle: bool,
    confirm: bool,
    recursive: bool,
    from_col: int,
    to_col: int,
    voice_col: Optional[int] = None,
    voice_type: Optional[str] = None,
    language: Optional[str] = None,
) -> None:
    """A simple flashcard CLI tool.

    Provide a CSV file with columns of data. By default, questions are shown from the first column (0)
    and answers are expected from the second column (1). Use --from and --to options to customize
    which columns to use.
    """
    if from_col < 0 or to_col < 0:
        click.echo("Error: Column indices must be non-negative.")
        sys.exit(1)

    if from_col == to_col:
        click.echo("Error: Question and answer columns must be different.")
        sys.exit(1)
        
    # Check voice options
    if voice_col is not None:
        if not VOICE_AVAILABLE:
            click.echo(click.style("Error: Voice functionality not available. Make sure the OpenAI package is installed.", fg="red"))
            if not click.confirm("Continue without voice?", default=True):
                sys.exit(1)
            voice_col = None
            
        elif voice_col < 0:
            click.echo(click.style("Error: Voice column index must be non-negative.", fg="red"))
            if not click.confirm("Continue without voice?", default=True):
                sys.exit(1)
            voice_col = None
            
        elif voice_type and voice_type not in AVAILABLE_VOICES:
            click.echo(click.style(f"Error: Invalid voice type. Choose from: {', '.join(AVAILABLE_VOICES)}", fg="red"))
            if not click.confirm("Continue without voice?", default=True):
                sys.exit(1)
            voice_col = None
            
        elif language and language.lower() not in LANGUAGE_INSTRUCTIONS:
            click.echo(click.style(f"Error: Invalid language. Choose from: {', '.join(LANGUAGE_INSTRUCTIONS.keys())}", fg="red"))
            if not click.confirm("Continue without voice?", default=True):
                sys.exit(1)
            voice_col = None
            
        elif not os.environ.get("OPENAI_API_KEY"):
            click.echo(click.style("Error: OPENAI_API_KEY environment variable is not set.", fg="red"))
            if not click.confirm("Continue without voice?", default=True):
                sys.exit(1)
            voice_col = None

    cards = load_cards(csv_path, from_col, to_col)

    if shuffle:
        random.shuffle(cards)

    round_num = 1
    current_cards = cards
    all_results: Dict[int, Tuple[int, int]] = {}  # {round: (correct, total)}

    while current_cards:
        _, incorrect_cards = run_round(
            current_cards, 
            confirm, 
            round_num, 
            voice_col, 
            voice_type,
            language
        )

        # Store the results for this round
        all_results[round_num] = (
            len(current_cards) - len(incorrect_cards),
            len(current_cards),
        )

        # If we're not in recursive mode or there are no incorrect cards, we're done
        if not recursive or not incorrect_cards:
            break

        # Otherwise, prepare for the next round with just the incorrect cards
        if shuffle:
            random.shuffle(incorrect_cards)

        current_cards = incorrect_cards
        round_num += 1

    # Show a final summary if we had multiple rounds
    if recursive and round_num > 1:
        click.echo("\n--- Final Summary ---")
        total_cards = len(cards)
        for r, (correct, total) in all_results.items():
            click.echo(
                f"Round {r}: {correct}/{total} correct ({correct/total*100:.1f}%)"
            )

        if not incorrect_cards:
            click.echo(
                click.style(
                    "\nCongratulations! You've mastered all the cards!",
                    fg="green",
                    bold=True,
                )
            )


if __name__ == "__main__":
    flash()
