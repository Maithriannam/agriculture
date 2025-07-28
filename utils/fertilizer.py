def suggest_fertilizer(crop):
    tips = {
        "Paddy": "Use Urea (N) and DAP before flowering",
        "Maize": "Use 125kg NPK per hectare (20:20:0)",
        "Wheat": "Apply 60:40:40 NPK kg/ha",
        "Cotton": "Use 100kg NPK (4:2:1) per acre"
    }
    return tips.get(crop, "No suggestion available")
