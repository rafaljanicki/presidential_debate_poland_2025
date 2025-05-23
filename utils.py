import os

def load_persona(persona_file_path: str) -> str:
    """Loads a candidate's persona from a text file."""
    if not os.path.exists(persona_file_path):
        print(f"Warning: Persona file not found at {persona_file_path}. Using empty persona.")
        return "You are a helpful AI assistant."
    try:
        with open(persona_file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error loading persona from {persona_file_path}: {e}. Using empty persona.")
        return "You are a helpful AI assistant." 