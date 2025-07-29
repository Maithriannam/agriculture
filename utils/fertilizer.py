def suggest_fertilizer(crop):
    tips = {
        "Paddy": "Use Urea & Potash-rich fertilizer every 2 weeks.",
        "Maize": "Apply NPK (20:20:0) for early growth.",
        "Wheat": "Use DAP and Zinc once every 3 weeks.",
        "Cotton": "Spray micronutrients and compost mix regularly."
    }
    return tips.get(crop, "Use balanced NPK fertilizer based on soil test.")


