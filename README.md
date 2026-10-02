# Adopt Me! Trade Value API Documentation

Welcome to the Adopt Me! Trade Value API. This service provides pet trade values across different potion variations using Elvebredd market data.

## Quick Start

### Base URL

```text
https://elvebredd-api.onrender.com
```

All responses are returned in JSON format.

## API Endpoints

### 1. Check API Status

Verify if the service is online.

**Endpoint:** `GET /`

**cURL Example:**

```bash
curl -X GET "https://elvebredd-api.onrender.com/"
```

**Response Example:**

```json
{
  "status": "online",
  "endpoint": "/api/pets"
}
```

### 2. Get All Pets and Values

Retrieve the complete database of cached pet values.

**Endpoint:** `GET /api/pets`

**cURL Example:**

```bash
curl -X GET "https://elvebredd-api.onrender.com/api/pets"
```

**Response Example:**

```json
[
  {
    "name": "Shadow Dragon",
    "regular": {
      "fr": 125.0,
      "np": 135.0,
      "r": 128.0,
      "f": 127.0
    },
    "neon": {
      "fr": 500.0,
      "np": 550.0,
      "r": 510.0,
      "f": 505.0
    },
    "mega": {
      "fr": 2000.0,
      "np": 2200.0,
      "r": 2050.0,
      "f": 2025.0
    }
  }
]
```

### 3. Get Specific Pet Value

Search for a single pet by name. Pet names are case-insensitive.

Spaces in the pet name should be URL-encoded using `%20`.

**Endpoint:** `GET /api/pets/{pet_name}`

**cURL Example:**

```bash
curl -X GET "https://elvebredd-api.onrender.com/api/pets/Shadow%20Dragon"
```

**Response Example:**

```json
{
  "name": "Shadow Dragon",
  "regular": {
    "fr": 125.0,
    "np": 135.0,
    "r": 128.0,
    "f": 127.0
  },
  "neon": {
    "fr": 500.0,
    "np": 550.0,
    "r": 510.0,
    "f": 505.0
  },
  "mega": {
    "fr": 2000.0,
    "np": 2200.0,
    "r": 2050.0,
    "f": 2025.0
  }
}
```

## Code Examples

### Roblox (Luau)

Integration example for Roblox Studio using `HttpService`:

```lua
local HttpService = game:GetService("HttpService")
local BASE_URL = "https://elvebredd-api.onrender.com"

local function getPetValue(petName)
    local encodedName = HttpService:UrlEncode(petName)
    local url = BASE_URL .. "/api/pets/" .. encodedName

    local success, response = pcall(function()
        return HttpService:GetAsync(url)
    end)

    if success then
        return HttpService:JSONDecode(response)
    else
        warn("Failed to fetch pet value: " .. tostring(response))
        return nil
    end
end

local shadow = getPetValue("Shadow Dragon")

if shadow then
    print(shadow.name .. " Regular FR Value: " .. tostring(shadow.regular.fr))
    print(shadow.name .. " Neon FR Value: " .. tostring(shadow.neon.fr))
    print(shadow.name .. " Mega FR Value: " .. tostring(shadow.mega.fr))
end
```

### JavaScript / Node.js

Example using `fetch`:

```javascript
const BASE_URL = "https://elvebredd-api.onrender.com";

async function fetchPet(petName) {
  try {
    const res = await fetch(
      `${BASE_URL}/api/pets/${encodeURIComponent(petName)}`
    );

    if (!res.ok) {
      throw new Error("Pet not found or API syncing");
    }

    const pet = await res.json();

    console.log(`${pet.name} (Regular FR):`, pet.regular.fr);
    console.log(`${pet.name} (Mega FR):`, pet.mega.fr);
  } catch (error) {
    console.error("Error fetching pet:", error);
  }
}

fetchPet("Frost Dragon");
```

### Python

Example using `requests`:

```python
import requests

BASE_URL = "https://elvebredd-api.onrender.com"

def get_pet(pet_name: str):
    response = requests.get(f"{BASE_URL}/api/pets/{pet_name}")

    if response.status_code == 200:
        return response.json()

    return None

pet = get_pet("Shadow Dragon")

if pet:
    print(f"{pet['name']} Regular FR: {pet['regular']['fr']}")
    print(f"{pet['name']} Mega FR: {pet['mega']['fr']}")
```

## Data Keys Reference

Each pet object contains three forms:

* `regular`
* `neon`
* `mega`

Each form contains the following potion status keys:

| Key  | Meaning    |
| ---- | ---------- |
| `fr` | Fly & Ride |
| `np` | No Potion  |
| `r`  | Ride Only  |
| `f`  | Fly Only   |

Example:

```json
{
  "regular": {
    "fr": 125.0,
    "np": 135.0,
    "r": 128.0,
    "f": 127.0
  }
}
```

`regular.fr` is the Regular Fly & Ride value.

`regular.np` is the Regular No-Potion value.

`regular.r` is the Regular Ride-Only value.

`regular.f` is the Regular Fly-Only value.


## Side Note:
this all started with me needing an api for a Roblox Script, for me to like calculate values directly without needing another window open since i had a tablet (still do) and doing thata te up too much ram. anyways, i looked through the whole internet, there was no value api in the internet and i made this one that atkes from elvebredd! Enjoy i guess.

