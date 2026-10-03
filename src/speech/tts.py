"""
Speech Synthesis Module (Edge-TTS Neural Voice)
Provides zero-cost, high-fidelity neural voice synthesis.
Saves audio output to static audio cache or test run folders.
"""

import os
import asyncio
from pathlib import Path
import edge_tts


class VoiceSynthesizer:
    DEFAULT_VOICE = "en-US-JennyNeural"

    def __init__(self, voice: str = None, output_dir: str = "src/web/static/audio"):
        self.voice = voice or os.getenv("TTS_VOICE", self.DEFAULT_VOICE)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def synthesize(self, text: str, output_path: str = None) -> str:
        """
        Synthesizes text into high-fidelity neural audio.
        Returns the relative or absolute path of the generated audio file.
        """
        if not output_path:
            # Generate deterministic hash for caching
            import hashlib
            text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()[:12]
            output_file = self.output_dir / f"tts_{text_hash}.mp3"
        else:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

        if output_file.exists():
            return str(output_file)

        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(str(output_file))
        return str(output_file)

    def synthesize_sync(self, text: str, output_path: str = None) -> str:
        """
        Synchronous helper for scripts and tests.
        """
        return asyncio.run(self.synthesize(text, output_path))


if __name__ == "__main__":
    synth = VoiceSynthesizer()
    out = synth.synthesize_sync("Hello, welcome to ApexCare Health Insurance. How can I help you today?")
    print(f"Generated test audio at: {out}")
