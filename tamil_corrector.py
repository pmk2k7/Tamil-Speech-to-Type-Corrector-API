import re
from typing import Dict, Tuple, List

class TamilSpeechProcessor:
    """
    Tamil Speech-to-Text Post-Processor & Voice Command Parser.
    Converts spoken Tamil voice commands into punctuation marks and normalizes
    colloquial spoken Tamil (பேச்சுத் தமிழ்) into formal written Tamil (எழுத்துத் தமிழ்).
    """

    # Voice command punctuation mappings
    VOICE_COMMANDS: Dict[str, str] = {
        # Required user commands:
        "நிறுத்து": ".",
        "நிறுத்தற்குறி": ".",
        "முற்றுப்புள்ளி": ".",
        "தொடர்": ",",
        "காற்புள்ளி": ",",
        "கமா": ",",
        # Additional useful formatting voice commands:
        "புதிய வரி": "\n",
        "அடுத்த வரி": "\n",
        "கேள்விக்குறி": "?",
        "வினாக்குறி": "?",
        "வியப்புக்குறி": "!",
        "ஆச்சரியக்குறி": "!",
    }

    # Common Colloquial (Spoken) to Standard (Written) Tamil Dictionary
    SPOKEN_TO_WRITTEN_DICT: Dict[str, str] = {
        # Verbs - First Person Present/Future
        "வர்றேன்": "வருகிறேன்",
        "வரேன்": "வருகிறேன்",
        "போறேன்": "போகிறேன்",
        "பண்றேன்": "செய்கிறேன்",
        "பண்ணுறேன்": "செய்கிறேன்",
        "சொல்றேன்": "சொல்கிறேன்",
        "சொல்ரேன்": "சொல்கிறேன்",
        "பாக்குறேன்": "பார்க்கிறேன்",
        "பார்க்குறேன்": "பார்க்கிறேன்",
        "கேக்குறேன்": "கேட்கிறேன்",
        "கேட்குறேன்": "கேட்கிறேன்",
        "சாப்பிடுறேன்": "சாப்பிடுகிறேன்",
        "தூங்குறேன்": "தூங்குகிறேன்",
        "படிக்குறேன்": "படிக்கிறேன்",
        "படிக்கிறன்": "படிக்கிறேன்",
        "எழுதுறேன்": "எழுதுகிறேன்",
        "வாங்குறேன்": "வாங்குகிறேன்",
        "கொடுக்குறேன்": "கொடுக்கிறேன்",
        "பேசுறேன்": "பேசுகிறேன்",
        "ஓடுறேன்": "ஓடுகிறேன்",
        "சிரிக்குறேன்": "சிரிக்கிறேன்",
        "நினைக்குறேன்": "நினைக்கிறேன்",
        "இருக்கேன்": "இருக்கிறேன்",
        "இருக்கு": "இருக்கிறது",
        "இருக்குது": "இருக்கிறது",

        # Verbs - Third Person Plural/Honorific
        "வர்றாங்க": "வருகிறார்கள்",
        "போறாங்க": "போகிறார்கள்",
        "பண்றாங்க": "செய்கிறார்கள்",
        "சொல்றாங்க": "சொல்கிறார்கள்",
        "பாக்குறாங்க": "பார்க்கிறார்கள்",
        "கேக்குறாங்க": "கேட்கிறார்கள்",
        "இருக்காங்க": "இருக்கிறார்கள்",

        # Verbs - Past Tense Colloquial
        "வந்தாச்சு": "வந்துவிட்டது",
        "போயாச்சு": "போய்விட்டது",
        "பண்ணியாச்சு": "செய்துவிட்டது",
        "முடிஞ்சிருச்சு": "முடிந்துவிட்டது",
        "ஆயிடுச்சு": "ஆகிவிட்டது",
        "ஆகிடுச்சு": "ஆகிவிட்டது",

        # Colloquial Pronouns & Particles
        "நம்ம": "நாம்",
        "எங்க": "எங்கள்",
        "உங்க": "உங்கள்",
        "அவங்க": "அவர்கள்",
        "இவங்க": "இவர்கள்",
        "யாரு": "யார்",
        "என்னாச்சு": "என்ன ஆயிற்று",
        "ஏன்டா": "ஏன்",
        "இப்போ": "இப்போது",
        "அப்போ": "அப்போது",
        "எப்போ": "எப்போது",
        "இங்கே": "இங்கு",
        "அங்கே": "அங்கு",
        "எங்கே": "எங்கு",
        "கொஞ்சம்": "சற்று",
        "ரொம்ப": "மிகவும்",
        "நல்லா": "நன்றாக",
    }

    @classmethod
    def apply_voice_commands(cls, text: str) -> str:
        """
        Replaces spoken punctuation keywords like 'நிறுத்து' and 'தொடர்'
        with actual punctuation marks ('.', ',') and cleans up spacing.
        """
        if not text:
            return ""

        # Replace exact word matches or surrounded phrases for voice commands
        words = text.split()
        processed_words: List[str] = []

        for word in words:
            # Strip punctuation for matching keyword
            clean_word = re.sub(r'[^\w\s]', '', word)
            
            if clean_word in cls.VOICE_COMMANDS:
                punct = cls.VOICE_COMMANDS[clean_word]
                if processed_words and punct in [".", ",", "?", "!"]:
                    # Attach punctuation directly to the previous word
                    processed_words[-1] = processed_words[-1].rstrip() + punct
                elif punct == "\n":
                    processed_words.append("\n")
                else:
                    processed_words.append(punct)
            else:
                processed_words.append(word)

        result = " ".join(processed_words)
        
        # Clean up space before punctuation marks and newline formatting
        result = re.sub(r'\s+([\.,\?!])', r'\1', result)
        result = re.sub(r'\n\s+', '\n', result)
        result = re.sub(r' +', ' ', result)

        return result.strip()

    @classmethod
    def normalize_spoken_tamil(cls, text: str) -> str:
        """
        Replaces common spoken Tamil words with their standard written equivalents.
        """
        if not text:
            return ""

        words = text.split()
        normalized_words: List[str] = []

        for word in words:
            # Check for trailing punctuation attached to word
            match = re.match(r'^([\w]+)([\.,\?!]*)$', word)
            if match:
                base_word, punctuation = match.groups()
                written_equivalent = cls.SPOKEN_TO_WRITTEN_DICT.get(base_word, base_word)
                normalized_words.append(written_equivalent + punctuation)
            else:
                written_equivalent = cls.SPOKEN_TO_WRITTEN_DICT.get(word, word)
                normalized_words.append(written_equivalent)

        return " ".join(normalized_words)

    @classmethod
    def process_full(cls, raw_text: str, auto_correct_grammar: bool = True) -> Dict[str, str]:
        """
        Full post-processing pipeline:
        1. Parse voice punctuation commands ('நிறுத்து' -> '.', 'தொடர்' -> ',')
        2. Optionally normalize spoken Tamil words to formal written Tamil.
        """
        text_with_punctuation = cls.apply_voice_commands(raw_text)
        
        if auto_correct_grammar:
            final_text = cls.normalize_spoken_tamil(text_with_punctuation)
        else:
            final_text = text_with_punctuation

        return {
            "raw_input": raw_text,
            "processed_text": final_text,
            "punctuation_applied": text_with_punctuation != raw_text,
            "grammar_corrected": final_text != text_with_punctuation
        }
