"""
An optional audio voice for flashcards powered by OpenAI's TTS API.
Requires an OPENAI_API_KEY environment variable.
"""

import hashlib
import os
import subprocess
import threading
from pathlib import Path

from openai import AuthenticationError, OpenAI

# Available voices in OpenAI's TTS API
AVAILABLE_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer", "coral"]
DEFAULT_VOICE = "onyx"
DEFAULT_MODEL = "gpt-4o-mini-tts"

# Language instructions in the target language where possible
LANGUAGE_INSTRUCTIONS = {
    "english": "Read this text in English.",
    "japanese": "この文章を日本語で読んでください。",  # Please read this text in Japanese
    "chinese": "请用中文阅读这段文字。",  # Please read this text in Chinese
    "korean": "이 텍스트를 한국어로 읽어주세요.",  # Please read this text in Korean
    "spanish": "Lee este texto en español.",  # Read this text in Spanish
    "french": "Lisez ce texte en français.",  # Read this text in French
    "german": "Lesen Sie diesen Text auf Deutsch.",  # Read this text in German
    "italian": "Leggi questo testo in italiano.",  # Read this text in Italian
    "russian": "Прочитайте этот текст на русском языке.",  # Read this text in Russian
    "portuguese": "Leia este texto em português.",  # Read this text in Portuguese
    "arabic": "اقرأ هذا النص باللغة العربية.",  # Read this text in Arabic
    "hindi": "इस पाठ को हिंदी में पढ़ें।",  # Read this text in Hindi
    "thai": "อ่านข้อความนี้เป็นภาษาไทย",  # Read this text in Thai
    "vietnamese": "Đọc văn bản này bằng tiếng Việt.",  # Read this text in Vietnamese
}


class VoiceReader:
    """Handles text-to-speech conversion for flashcards."""

    def __init__(self, cache_dir: str | None = None):
        """Initialize the voice reader.

        Args:
            cache_dir: Directory to store cached audio files. Defaults to ~/.flash
        """
        self.client = OpenAI()

        # Set up cache directory
        if cache_dir is None:
            self.cache_dir = Path.home() / ".flash"
        else:
            self.cache_dir = Path(cache_dir)

        self.cache_dir.mkdir(exist_ok=True, parents=True)

        # Track active audio threads
        self.active_playback_threads: list[threading.Thread] = []

    def get_audio_path(
        self, text: str, voice: str = DEFAULT_VOICE, language: str | None = None
    ) -> Path:
        """Get the path for an audio file, either from cache or newly generated.

        Args:
            text: The text to convert to speech
            voice: The voice to use (one of AVAILABLE_VOICES)
            language: Optional language to specify how text should be read

        Returns:
            Path to the audio file

        Raises:
            ValueError: If voice is not valid
            AuthenticationError: If OpenAI API key is missing or invalid
        """
        if voice not in AVAILABLE_VOICES:
            raise ValueError(
                f"Invalid voice. Choose from: {', '.join(AVAILABLE_VOICES)}"
            )

        # Normalize language if provided
        lang_key = language.lower() if language else None
        instructions = LANGUAGE_INSTRUCTIONS.get(lang_key, None) if lang_key else None

        # Create a hash of the content, voice and language instructions to use as filename
        # Include the actual instructions text in the hash, not just the language name
        hash_content = f"{text}:{voice}:{instructions or ''}"
        content_hash = hashlib.md5(hash_content.encode()).hexdigest()
        audio_path = self.cache_dir / f"{content_hash}.mp3"

        # Return path if cached version exists
        if audio_path.exists():
            return audio_path

        # Otherwise generate new audio file
        try:
            # Create API call with proper typing
            if instructions:
                with self.client.audio.speech.with_streaming_response.create(
                    model=DEFAULT_MODEL,
                    voice=voice,
                    input=text,
                    instructions=instructions,
                ) as response:
                    response.stream_to_file(audio_path)
            else:
                with self.client.audio.speech.with_streaming_response.create(
                    model=DEFAULT_MODEL,
                    voice=voice,
                    input=text,
                ) as response:
                    response.stream_to_file(audio_path)
            return audio_path
        except AuthenticationError as e:
            # Re-raise the original exception with additional context
            raise Exception(
                "OpenAI API authentication failed. Please check your API key."
            ) from e
        except Exception as e:
            # If there's an error, return None and print the error
            raise Exception(f"Error generating audio: {e}") from e

    def _play_audio_thread(self, audio_path: Path) -> None:
        """Thread function to play audio in the background.

        Args:
            audio_path: Path to the audio file to play
        """
        try:
            if not audio_path.exists():
                return

            # Use platform-specific commands to play audio
            if os.name == "posix":  # macOS, Linux
                if "darwin" in os.uname().sysname.lower():  # macOS
                    subprocess.run(
                        ["afplay", str(audio_path)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:  # Linux
                    try:
                        subprocess.run(
                            ["mpg123", str(audio_path)],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                    except FileNotFoundError:
                        subprocess.run(
                            ["aplay", str(audio_path)],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
            elif os.name == "nt":  # Windows
                # Use startfile on Windows, which is non-blocking
                os.startfile(audio_path)  # type: ignore[attr-defined]
        except Exception:
            # Silently fail in threads
            pass

    def play_audio(self, audio_path: Path) -> None:
        """Play an audio file in the background.

        This is platform-dependent and uses the appropriate command
        for the user's operating system.

        Args:
            audio_path: Path to the audio file to play
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Clean up completed threads
        self.active_playback_threads = [
            t for t in self.active_playback_threads if t.is_alive()
        ]

        # Create and start a new thread for playback
        thread = threading.Thread(
            target=self._play_audio_thread, args=(audio_path,), daemon=True
        )
        thread.start()

        # Keep track of the thread
        self.active_playback_threads.append(thread)

    def speak(
        self, text: str, voice: str = DEFAULT_VOICE, language: str | None = None
    ) -> None:
        """Convert text to speech and play it.

        Args:
            text: The text to speak
            voice: The voice to use
            language: Optional language to specify how text should be read

        Raises:
            Various exceptions that might occur during audio generation or playback
        """
        try:
            audio_path = self.get_audio_path(text, voice, language)
            self.play_audio(audio_path)
        except Exception as e:
            raise Exception(f"Error speaking text: {e}") from e
