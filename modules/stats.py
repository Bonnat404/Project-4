def calculate_stats(products):
    if not products:
        return {"total_items": 0, "total_value": 0, "low_stock": 0}
        
    count = len(products)
    value = 0.0
    low = 0
    
    for p in products:
        try:
            # --- CORRECTION ICI ---
            # 1. On transforme en texte
            # 2. On remplace la virgule par un point
            # 3. On enlève le symbole '€' et '$' si jamais ils sont là
            # 4. On enlève les espaces vides
            raw_price = str(p['prix']).replace(',', '.').replace('€', '').replace('$', '').strip()
            
            prix = float(raw_price)
            qte = int(p['quantite'])
            
            value += prix * qte
            if qte < 5:
                low += 1
        except (ValueError, KeyError, TypeError):
            # Si la ligne est impossible à lire, on l'ignore silencieusement
            continue
    
    return {
        "total_items": count,
        "total_value": round(value, 2),
        "low_stock": low
    }