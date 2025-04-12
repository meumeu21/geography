import os
from django.conf import settings

def get_countries_for_table():
    countries = []
    file_path = os.path.join(settings.BASE_DIR, "data", "countries.csv")
    
    with open(file_path, "r", encoding="utf-8") as f:
        next(f) 
        for line in f:
            country, capital, added_by, date_added = line.strip().split(";")
            countries.append({
                "country": country,
                "capital": capital,
                "added_by": added_by,
                "date_added": date_added or "-",
            })
    return countries


def add_country(new_country, new_capital, user, date_added):
    new_line = f"{new_country};{new_capital};{user};{date_added}"
    file_path = os.path.join(settings.BASE_DIR, "data", "countries.csv")
    
    with open(file_path, "r+", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]
        header = lines[0]
        existing_lines = lines[1:]
        
    updated_lines = existing_lines + [new_line]
    updated_lines.sort()
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        f.write("\n".join(updated_lines))


def get_countries_stats():
    db_countries = 0
    user_countries = 0
    
    file_path = os.path.join(settings.BASE_DIR, "data", "countries.csv")
    
    with open(file_path, "r", encoding="utf-8") as f:
        next(f)
        for line in f:
            _, _, added_by, _ = line.strip().split(";")
            if added_by == "db":
                db_countries += 1
            else:
                user_countries += 1
    
    total_countries = db_countries + user_countries
    return db_countries, user_countries, total_countries

def get_countries_count():
    try:
        with open("data/countries.csv", "r", encoding="utf-8") as f:
            return sum(1 for line in f) - 1 
    except FileNotFoundError:
        return 0
