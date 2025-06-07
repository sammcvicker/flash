"""Tests for the CLI module."""

import csv
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from flash.cli import flash, load_cards, run_round


class TestLoadCards:
    """Test the load_cards function."""

    def test_load_basic_cards(self):
        """Test loading basic two-column cards."""
        fixture_path = Path(__file__).parent / "fixtures" / "basic_cards.csv"
        cards = load_cards(str(fixture_path))

        assert len(cards) == 4
        assert cards[0] == ("What is the capital of France?", "Paris")
        assert cards[1] == ("What is 2+2?", "4")
        assert cards[2] == ("Who wrote Romeo and Juliet?", "Shakespeare")
        assert cards[3] == ("What color is the sky?", "Blue")

    def test_load_cards_custom_columns(self):
        """Test loading cards with custom column indices."""
        fixture_path = Path(__file__).parent / "fixtures" / "multi_column.csv"

        # Test English to Japanese (columns 1 -> 2)
        cards = load_cards(str(fixture_path), from_col=1, to_col=2)
        assert len(cards) == 4
        assert cards[0] == ("one", "一")
        assert cards[1] == ("two", "二")

        # Test Japanese to Hiragana (columns 2 -> 3)
        cards = load_cards(str(fixture_path), from_col=2, to_col=3)
        assert len(cards) == 4
        assert cards[0] == ("一", "いち")

    def test_load_cards_unicode(self):
        """Test loading cards with Unicode characters."""
        fixture_path = Path(__file__).parent / "fixtures" / "unicode_cards.csv"
        cards = load_cards(str(fixture_path))

        assert len(cards) == 5
        assert cards[0] == ("Здравствуй", "Hello (Russian)")
        assert cards[1] == ("こんにちは", "Hello (Japanese)")
        assert cards[4] == ("🌟", "Star emoji")

    def test_load_cards_file_not_found(self):
        """Test error handling when file doesn't exist."""
        with pytest.raises(SystemExit):
            load_cards("nonexistent_file.csv")

    def test_load_cards_invalid_columns(self):
        """Test loading cards when specified columns don't exist."""
        fixture_path = Path(__file__).parent / "fixtures" / "basic_cards.csv"

        # Should exit when no valid cards are found
        with pytest.raises(SystemExit):
            load_cards(
                str(fixture_path), from_col=0, to_col=5
            )  # Column 5 doesn't exist

    def test_load_cards_malformed_csv(self):
        """Test loading cards from malformed CSV."""
        fixture_path = Path(__file__).parent / "fixtures" / "malformed.csv"
        cards = load_cards(str(fixture_path))

        # Should load rows that have both columns (even if empty)
        assert len(cards) == 4  # All rows with 2 columns
        assert ("Good row", "Good answer") in cards
        assert ("Another good row", "Another good answer") in cards
        assert ("", "Empty question") in cards
        assert ("Good question", "") in cards

    def test_load_cards_empty_file(self):
        """Test loading cards from empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("")  # Empty file
            temp_path = f.name

        try:
            with pytest.raises(SystemExit):
                load_cards(temp_path)
        finally:
            os.unlink(temp_path)


class TestRunRound:
    """Test the run_round function."""

    def test_run_round_basic(self):
        """Test a basic round with mocked user input."""
        cards = [("What is 2+2?", "4"), ("What is the capital of France?", "Paris")]

        with patch("click.prompt") as mock_prompt:
            mock_prompt.side_effect = ["4", "Paris"]  # Correct answers

            correct, incorrect = run_round(cards, confirm=False)

            assert len(correct) == 2
            assert len(incorrect) == 0
            assert correct == cards

    def test_run_round_with_incorrect_answers(self):
        """Test a round with some incorrect answers."""
        cards = [("What is 2+2?", "4"), ("What is the capital of France?", "Paris")]

        with patch("click.prompt") as mock_prompt:
            mock_prompt.side_effect = ["5", "London"]  # Incorrect answers

            correct, incorrect = run_round(cards, confirm=False)

            assert len(correct) == 0
            assert len(incorrect) == 2
            assert incorrect == cards

    def test_run_round_with_confirm_mode(self):
        """Test run_round with confirmation mode enabled."""
        cards = [("What is 2+2?", "4")]

        with patch("click.prompt") as mock_prompt:
            # First answer wrong, then correct confirmation
            mock_prompt.side_effect = ["5", "4"]

            correct, incorrect = run_round(cards, confirm=True)

            assert len(correct) == 0
            assert len(incorrect) == 1
            # Should have been called twice (initial answer + confirmation)
            assert mock_prompt.call_count == 2

    @patch("flash.cli.VoiceReader")
    def test_run_round_with_voice(self, mock_voice_reader_class):
        """Test run_round with voice functionality."""
        cards = [("Hello", "World")]
        mock_voice_reader = MagicMock()
        mock_voice_reader_class.return_value = mock_voice_reader

        with patch("click.prompt", return_value="World"):
            with patch("flash.cli.VOICE_AVAILABLE", True):
                correct, incorrect = run_round(
                    cards, confirm=False, voice_col=0, voice="onyx", language="english"
                )

                # Voice reader should be initialized and speak method called
                mock_voice_reader_class.assert_called_once()
                mock_voice_reader.speak.assert_called_once_with(
                    "Hello", "onyx", "english"
                )


class TestFlashCLI:
    """Test the main CLI command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.fixture_path = Path(__file__).parent / "fixtures" / "basic_cards.csv"

    def test_flash_basic_usage(self):
        """Test basic CLI usage."""
        with patch("flash.cli.run_round") as mock_run_round:
            mock_run_round.return_value = ([], [])  # No incorrect cards

            result = self.runner.invoke(flash, [str(self.fixture_path)])

            assert result.exit_code == 0
            mock_run_round.assert_called_once()

    def test_flash_with_shuffle_option(self):
        """Test CLI with shuffle option."""
        with patch("flash.cli.run_round") as mock_run_round:
            with patch("random.shuffle") as mock_shuffle:
                mock_run_round.return_value = ([], [])

                result = self.runner.invoke(
                    flash, [str(self.fixture_path), "--shuffle"]
                )

                assert result.exit_code == 0
                mock_shuffle.assert_called()

    def test_flash_with_custom_columns(self):
        """Test CLI with custom column specification."""
        multi_col_path = Path(__file__).parent / "fixtures" / "multi_column.csv"

        with patch("flash.cli.run_round") as mock_run_round:
            mock_run_round.return_value = ([], [])

            result = self.runner.invoke(
                flash, [str(multi_col_path), "--from", "1", "--to", "2"]
            )

            assert result.exit_code == 0

    def test_flash_invalid_column_indices(self):
        """Test CLI with invalid column indices."""
        result = self.runner.invoke(
            flash, [str(self.fixture_path), "--from", "-1", "--to", "1"]
        )

        assert result.exit_code == 1
        assert "Column indices must be non-negative" in result.output

    def test_flash_same_columns(self):
        """Test CLI when from and to columns are the same."""
        result = self.runner.invoke(
            flash, [str(self.fixture_path), "--from", "0", "--to", "0"]
        )

        assert result.exit_code == 1
        assert "Question and answer columns must be different" in result.output

    def test_flash_file_not_found(self):
        """Test CLI with non-existent file."""
        result = self.runner.invoke(flash, ["nonexistent.csv"])

        # Click returns exit code 2 for file not found errors
        assert result.exit_code == 2

    def test_flash_recursive_mode(self):
        """Test CLI with recursive mode."""
        with patch("flash.cli.run_round") as mock_run_round:
            # First round has incorrect cards, second round doesn't
            mock_run_round.side_effect = [
                ([], [("Q1", "A1")]),  # First round: 1 incorrect
                ([("Q1", "A1")], []),  # Second round: all correct
            ]

            result = self.runner.invoke(flash, [str(self.fixture_path), "--recursive"])

            assert result.exit_code == 0
            assert mock_run_round.call_count == 2
            assert "Congratulations" in result.output

    @patch.dict(os.environ, {}, clear=True)  # Clear environment
    def test_flash_voice_no_api_key(self):
        """Test CLI voice feature without API key."""
        # Mock all the confirm calls that might happen during voice validation
        with patch("click.confirm", return_value=True) as mock_confirm:
            with patch("flash.cli.run_round") as mock_run_round:
                mock_run_round.return_value = ([], [])  # No incorrect cards

                result = self.runner.invoke(
                    flash, [str(self.fixture_path), "--voice", "0"]
                )

                assert result.exit_code == 0
                assert "OPENAI_API_KEY" in result.output
                # Should have prompted to continue without voice
                mock_confirm.assert_called()


class TestEdgeCases:
    """Test various edge cases and error conditions."""

    def test_empty_csv_after_filtering(self):
        """Test CSV that becomes empty after column filtering."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("only_one_column\n")
            temp_path = f.name

        try:
            with pytest.raises(SystemExit):
                load_cards(temp_path, from_col=0, to_col=1)  # Column 1 doesn't exist
        finally:
            os.unlink(temp_path)

    def test_csv_with_quotes_and_commas(self):
        """Test CSV with quoted fields containing commas."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write('"What is 2+2, really?","4, obviously"\n')
            f.write('"Simple question","Simple answer"\n')
            temp_path = f.name

        try:
            cards = load_cards(temp_path)
            assert len(cards) == 2
            assert cards[0] == ("What is 2+2, really?", "4, obviously")
            assert cards[1] == ("Simple question", "Simple answer")
        finally:
            os.unlink(temp_path)
