def suggest_fertilizer(crop):
    suggestions = {
        "Paddy": "Use Urea and DAP in early stages.",
        "Maize": "Use Nitrogen-rich fertilizer.",
        "Wheat": "Apply Potassium-based fertilizer.",
        "Cotton": "Use phosphorus before flowering."
    }
    return suggestions.get(crop, "No suggestion available.")
