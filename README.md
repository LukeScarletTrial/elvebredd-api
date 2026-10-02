# 🐾 Adopt Me! Trade Value API Documentation

Welcome to the **Adopt Me! Trade Value API**.

This service provides real-time pet trade values across all potion variations — Regular, Neon, Mega, Fly/Ride, No-Potion, Ride-Only, and Fly-Only — extracted directly from Elvebredd market data.

## ⚡ Quick Start

### Base URL

```text
https://elvebredd-api.onrender.com
```

All responses are returned in **JSON** format.

---

# 📡 API Endpoints

## 1. Check API Status

Verify if the service is online.

* **Endpoint:** `GET /`

### cURL Example

```bash
curl -X GET "https://elvebredd-api.onrender.com/"
```

### Response Example

```json
{
  "status": "online",
  "endpoint": "/api/pets"
}
```

---

## 2. Get All Pets & Values

Retrieve the complete database of cached pet values.

* **Endpoint:** `GET /api/pets`

### cURL Example

```bash
curl -X GET "https://elvebredd-api.onrender.com/api/pets"
```

### Response Example

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

---

## 3. Get Specific Pet Value

Search for a single pet by name. Pet names are **case-insensitive**.

Make sure to URL-encode spaces using `%20`.

* **Endpoint:** `GET /api/pets/{pet_name}`

### cURL Example

```bash
curl -X GET "https://elvebredd-api.onrender.com/api/pets/Shadow%20Dragon"
```

### Response Example

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
```
