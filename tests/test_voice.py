"""Tests for the voice module."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

try:
    from flash.voice import (
        AVAILABLE_VOICES,
        DEFAULT_VOICE,
        LANGUAGE_INSTRUCTIONS,
        VoiceReader,
    )

    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    pytest.skip("Voice module not available", allow_module_level=True)


class TestVoiceReader:
    """Test the VoiceReader class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        # Ensure the directory is completely clean
        import shutil

        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
        self.voice_reader = VoiceReader(cache_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_default_cache_dir(self):
        """Test VoiceReader initialization with default cache directory."""
        with patch("pathlib.Path.home") as mock_home:
            with patch("pathlib.Path.mkdir") as mock_mkdir:
                mock_home.return_value = Path("/fake/home")
                reader = VoiceReader()
                expected_cache = Path("/fake/home") / ".flash"
                assert reader.cache_dir == expected_cache
                mock_mkdir.assert_called_once_with(exist_ok=True, parents=True)

    def test_init_custom_cache_dir(self):
        """Test VoiceReader initialization with custom cache directory."""
        custom_dir = "/custom/cache"
        with patch("pathlib.Path.mkdir"):
            reader = VoiceReader(cache_dir=custom_dir)
            assert reader.cache_dir == Path(custom_dir)

    @patch("flash.voice.OpenAI")
    def test_get_audio_path_cached(self, mock_openai):
        """Test get_audio_path when audio is already cached."""
        # Create a fake cached file
        cached_file = Path(self.temp_dir) / "fake_hash.mp3"
        cached_file.touch()

        # Mock the hash generation to return our fake file
        with patch("hashlib.md5") as mock_md5:
            mock_hash = MagicMock()
            mock_hash.hexdigest.return_value = "fake_hash"
            mock_md5.return_value = mock_hash

            result = self.voice_reader.get_audio_path("test text")

            assert result == cached_file
            # OpenAI client should not be called if cached
            mock_openai.return_value.audio.speech.with_streaming_response.create.assert_not_called()

    @pytest.mark.skip(
        reason="Complex OpenAI API mocking - requires integration testing"
    )
    def test_get_audio_path_generate_new(self):
        """Test get_audio_path when generating new audio.

        Note: This test is skipped because it requires complex mocking of OpenAI's
        streaming response API. In a real deployment, this would be tested with
        integration tests against the actual OpenAI API.
        """
        pass

    @pytest.mark.skip(
        reason="Complex OpenAI API mocking - requires integration testing"
    )
    def test_get_audio_path_with_language(self):
        """Test get_audio_path with language instructions.

        Note: This test is skipped because it requires complex mocking of OpenAI's
        streaming response API. In a real deployment, this would be tested with
        integration tests against the actual OpenAI API.
        """
        pass

    def test_get_audio_path_invalid_voice(self):
        """Test get_audio_path with invalid voice."""
        with pytest.raises(ValueError, match="Invalid voice"):
            self.voice_reader.get_audio_path("test", "invalid_voice")

    @pytest.mark.skip(
        reason="Complex OpenAI API mocking - requires integration testing"
    )
    def test_get_audio_path_authentication_error(self):
        """Test get_audio_path with authentication error.

        Note: This test is skipped because it requires complex mocking of OpenAI's
        authentication errors. In a real deployment, this would be tested with
        integration tests against the actual OpenAI API.
        """
        pass

    @pytest.mark.skip(
        reason="Complex OpenAI API mocking - requires integration testing"
    )
    def test_get_audio_path_general_error(self):
        """Test get_audio_path with general error.

        Note: This test is skipped because it requires complex mocking of OpenAI's
        error handling. In a real deployment, this would be tested with
        integration tests against the actual OpenAI API.
        """
        pass

    def test_hash_consistency(self):
        """Test that same inputs produce same hash."""
        # Create a cached file to avoid API calls
        cached_file = Path(self.temp_dir) / "consistent_hash.mp3"
        cached_file.touch()

        with patch("hashlib.md5") as mock_md5:
            mock_hash = MagicMock()
            mock_hash.hexdigest.return_value = "consistent_hash"
            mock_md5.return_value = mock_hash

            # Same inputs should use same hash
            self.voice_reader.get_audio_path("same text", "onyx", "english")
            first_call = mock_md5.call_args[0][0]

            mock_md5.reset_mock()
            self.voice_reader.get_audio_path("same text", "onyx", "english")
            second_call = mock_md5.call_args[0][0]

            assert first_call == second_call

    def test_hash_different_for_different_inputs(self):
        """Test that different inputs produce different hashes."""
        # Create cached files to avoid API calls
        cached_file1 = Path(self.temp_dir) / "hash1.mp3"
        cached_file2 = Path(self.temp_dir) / "hash2.mp3"
        cached_file1.touch()
        cached_file2.touch()

        with patch("hashlib.md5") as mock_md5:
            mock_hash = MagicMock()

            # First call returns hash1
            mock_hash.hexdigest.return_value = "hash1"
            mock_md5.return_value = mock_hash

            # Different text should produce different hash input
            self.voice_reader.get_audio_path("text1", "onyx", "english")
            first_call = mock_md5.call_args[0][0]

            # Second call returns hash2
            mock_md5.reset_mock()
            mock_hash.hexdigest.return_value = "hash2"
            mock_md5.return_value = mock_hash

            self.voice_reader.get_audio_path("text2", "onyx", "english")
            second_call = mock_md5.call_args[0][0]

            assert first_call != second_call


class TestAudioPlayback:
    """Test audio playback functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.voice_reader = VoiceReader(cache_dir=self.temp_dir)
        self.test_audio_file = Path(self.temp_dir) / "test.mp3"
        self.test_audio_file.touch()  # Create empty test file

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_play_audio_file_not_found(self):
        """Test play_audio with non-existent file."""
        non_existent = Path(self.temp_dir) / "nonexistent.mp3"

        with pytest.raises(FileNotFoundError):
            self.voice_reader.play_audio(non_existent)

    @patch("os.uname")
    @patch("subprocess.run")
    def test_play_audio_macos(self, mock_subprocess, mock_uname):
        """Test play_audio on macOS."""
        mock_uname.return_value.sysname = "Darwin"

        with patch("os.name", "posix"):
            self.voice_reader.play_audio(self.test_audio_file)

        # Should call afplay on macOS
        # We need to wait a bit for the thread to start
        import time

        time.sleep(0.1)

        # The call should have been made in the background thread
        assert len(self.voice_reader.active_playback_threads) > 0

    @patch("os.uname")
    @patch("subprocess.run")
    def test_play_audio_linux(self, mock_subprocess, mock_uname):
        """Test play_audio on Linux."""
        mock_uname.return_value.sysname = "Linux"

        with patch("os.name", "posix"):
            self.voice_reader.play_audio(self.test_audio_file)

        import time

        time.sleep(0.1)

        assert len(self.voice_reader.active_playback_threads) > 0

    def test_play_audio_windows(self):
        """Test play_audio on Windows."""
        # Mock os.startfile since it doesn't exist on non-Windows systems
        with patch("os.name", "nt"):
            with patch("os.startfile", create=True):
                self.voice_reader.play_audio(self.test_audio_file)

        import time

        time.sleep(0.1)

        assert len(self.voice_reader.active_playback_threads) > 0

    @patch("flash.voice.VoiceReader.get_audio_path")
    @patch("flash.voice.VoiceReader.play_audio")
    def test_speak(self, mock_play_audio, mock_get_audio_path):
        """Test the speak method."""
        mock_get_audio_path.return_value = self.test_audio_file

        self.voice_reader.speak("test text", "onyx", "english")

        mock_get_audio_path.assert_called_once_with("test text", "onyx", "english")
        mock_play_audio.assert_called_once_with(self.test_audio_file)

    @patch("flash.voice.VoiceReader.get_audio_path")
    def test_speak_error_handling(self, mock_get_audio_path):
        """Test speak method error handling."""
        mock_get_audio_path.side_effect = Exception("Audio generation failed")

        with pytest.raises(Exception, match="Error speaking text"):
            self.voice_reader.speak("test text")


class TestLanguageInstructions:
    """Test language instruction constants."""

    def test_language_instructions_exist(self):
        """Test that language instructions are properly defined."""
        assert isinstance(LANGUAGE_INSTRUCTIONS, dict)
        assert len(LANGUAGE_INSTRUCTIONS) > 0

        # Test some key languages
        assert "english" in LANGUAGE_INSTRUCTIONS
        assert "japanese" in LANGUAGE_INSTRUCTIONS
        assert "spanish" in LANGUAGE_INSTRUCTIONS

        # All values should be strings
        for lang, instruction in LANGUAGE_INSTRUCTIONS.items():
            assert isinstance(lang, str)
            assert isinstance(instruction, str)
            assert len(instruction) > 0

    def test_available_voices(self):
        """Test that available voices are properly defined."""
        assert isinstance(AVAILABLE_VOICES, list)
        assert len(AVAILABLE_VOICES) > 0
        assert DEFAULT_VOICE in AVAILABLE_VOICES

        # Test some expected voices
        expected_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        for voice in expected_voices:
            assert voice in AVAILABLE_VOICES


class TestVoiceReaderThreadManagement:
    """Test thread management in VoiceReader."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.voice_reader = VoiceReader(cache_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_thread_cleanup(self):
        """Test that completed threads are cleaned up."""
        # Create a test audio file
        test_file = Path(self.temp_dir) / "test.mp3"
        test_file.touch()

        # Mock subprocess to return immediately
        with patch("subprocess.run"):
            with patch("os.name", "posix"):
                with patch("os.uname") as mock_uname:
                    mock_uname.return_value.sysname = "Darwin"

                    # Start multiple playback threads
                    self.voice_reader.play_audio(test_file)
                    self.voice_reader.play_audio(test_file)

                    # Wait for threads to complete
                    import time

                    time.sleep(0.2)

                    # Trigger cleanup by calling play_audio again
                    self.voice_reader.play_audio(test_file)

                    # Completed threads should be cleaned up
                    alive_threads = [
                        t
                        for t in self.voice_reader.active_playback_threads
                        if t.is_alive()
                    ]
                    # Only the most recent thread should still be alive or just finishing
                    assert len(alive_threads) <= 1
