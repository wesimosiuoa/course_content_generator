from flask import flash

def message(text, category="info"):
    """
    Centralized flash messaging function.
    
    Categories:
    success
    danger
    warning
    info
    """
    flash(text, category)
