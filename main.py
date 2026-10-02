import os
import re
import cloudscraper
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Adopt Me Values API")

URL = "https://elvebredd.com/adopt-me-calculator"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://google.com",
    "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


def fetch_pet_data():
    try:
        scraper = cloudscraper.create_scraper(
            browser={
                "browser": "chrome",
                "platform": "windows",
                "mobile": False,
            }
        )
        scraper.headers.update(HEADERS)
        response = scraper.get(URL, timeout=15)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch data: {str(e)}"
        )

    pet_chunks = re.split(r'\\+"image\\+":', html_content)[1:]
    pets = []

    for chunk in pet_chunks:
        clean_chunk = chunk.replace("\\", "")
        name_match = re.search(r'"name":"(.*?)"', clean_chunk)
        if not name_match:
            continue
        name = name_match.group(1)

        def find_val(key):
            pattern = rf'"{re.escape(key)}"[^\d]*?([\d\.]+)'
            m = re.search(pattern, clean_chunk)
            return float(m.group(1)) if m else None

        reg_fr = find_val("rvalue")
        fallback_val = (
            find_val("value") or find_val("val") or find_val("price")
        )

        pets.append(
            {
                "name": name,
                "regular": {
                    "fr": reg_fr if reg_fr is not None else fallback_val,
                    "np": find_val("rvalue - nopotion"),
                    "r": find_val("rvalue - ride"),
                    "f": find_val("rvalue - fly"),
                },
                "neon": {
                    "fr": find_val("nvalue"),
                    "np": find_val("nvalue - nopotion"),
                    "r": find_val("nvalue - ride"),
                    "f": find_val("nvalue - fly"),
                },
                "mega": {
                    "fr": find_val("mvalue"),
                    "np": find_val("mvalue - nopotion"),
                    "r": find_val("mvalue - ride"),
                    "f": find_val("mvalue - fly"),
                },
            }
        )

    if not pets:
        raise HTTPException(status_code=500, detail="No pet data parsed")

    return pets


@app.get("/")
def home():
    return {"status": "online", "endpoint": "/api/pets"}


@app.get("/api/pets")
def get_pets():
    return fetch_pet_data()


@app.get("/api/pets/{pet_name}")
def get_single_pet(pet_name: str):
    pets = fetch_pet_data()
    for pet in pets:
        if pet["name"].lower() == pet_name.lower():
            return pet
    raise HTTPException(status_code=404, detail="Pet not found")
