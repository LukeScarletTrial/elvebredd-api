import asyncio
import json
import logging
import os
import re
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright

URL = "https://elvebredd.com/adopt-me-calculator"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "logs.txt")
DATA_FILE = os.path.join(SCRIPT_DIR, "pets_live_data.json")

logging.basicConfig(
    filename=LOG_FILE,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    encoding="utf-8",
)

cached_pets = []


def log(message, level="info"):
    print(message)
    if level == "error":
        logging.error(message)
    else:
        logging.info(message)


async def scrape_elvebredd():
    global cached_pets
    log("Launching headless browser to bypass Cloudflare...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720},
            )
            page = await context.new_page()

            log(f"Navigating to {URL}...")
            await page.goto(URL, wait_until="networkidle", timeout=60000)

            html_content = await page.content()
            await browser.close()

        log("Extracting pet data...")
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
            reg_np = find_val("rvalue - nopotion")
            reg_r = find_val("rvalue - ride")
            reg_f = find_val("rvalue - fly")

            fallback_val = (
                find_val("value") or find_val("val") or find_val("price")
            )

            pet_data = {
                "name": name,
                "regular": {
                    "fr": reg_fr if reg_fr is not None else fallback_val,
                    "np": reg_np,
                    "r": reg_r,
                    "f": reg_f,
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
            pets.append(pet_data)

        if pets:
            cached_pets = pets
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(pets, f, indent=4)
            log(f"✅ Downloaded and saved {len(pets)} items.")
        else:
            log("❌ Could not parse pet data from rendered page.", level="error")

    except Exception as e:
        log(f"Error scraping with Playwright: {e}", level="error")


async def background_refresher():
    while True:
        await scrape_elvebredd()
        await asyncio.sleep(3600)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                global cached_pets
                cached_pets = json.load(f)
            log("Loaded existing local cache on startup.")
        except Exception as e:
            log(f"Failed to read cached data: {e}", level="error")

    asyncio.create_task(background_refresher())
    yield


app = FastAPI(title="Adopt Me Values API", lifespan=lifespan)


@app.get("/")
def home():
    return {"status": "online", "endpoint": "/api/pets"}


@app.get("/api/pets")
def get_pets():
    if not cached_pets:
        raise HTTPException(
            status_code=503,
            detail="Data initial sync in progress. Please retry in a few seconds.",
        )
    return cached_pets


@app.get("/api/pets/{pet_name}")
def get_single_pet(pet_name: str):
    if not cached_pets:
        raise HTTPException(status_code=503, detail="Data sync in progress.")
    for pet in cached_pets:
        if pet["name"].lower() == pet_name.lower():
            return pet
    raise HTTPException(status_code=404, detail="Pet not found")
