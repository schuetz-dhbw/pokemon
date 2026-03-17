# ANSI-Escape-Codes für Terminal-Formatierung
ITALIC = "\033[3m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def info(text: str) -> str:
    """Formatiert einen Infotext (kursiv)"""
    return f"▶️ {ITALIC}{text}{RESET}"

def important(text: str) -> str:
    """Formatiert einen Infotext (kursiv)"""
    return f"⚠️ {BOLD}{text}{RESET}"