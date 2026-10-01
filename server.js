const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');

const app = express();
const PORT = process.env.PORT || 3000;
const SITE_URL = 'https://elvebredd.com/adopt-me-calculator';

// Enable CORS so frontend applications or other scripts can call this API directly
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
    next();
});

// In-memory cache store
let petCache = null;
let lastFetchTime = 0;
const CACHE_DURATION = 15 * 60 * 1000; // Cache data for 15 minutes

const extractValue = (block, key) => {
    const doubleQuoteMatch = block.match(new RegExp(`"${key}"\\s*:\\s*"?([\\d\\.,]+)"?`));
    if (doubleQuoteMatch) {
        return parseFloat(doubleQuoteMatch[1].replace(/,/g, '')) || 0;
    }
    const fallbackMatch = block.match(new RegExp(`"${key}"[^\\d]-([\\d\\.,]+)`));
    if (fallbackMatch) {
        return parseFloat(fallbackMatch[1].replace(/,/g, '')) || 0;
    }
    return 0;
};

const scrapeElvebredd = async () => {
    const { data: html } = await axios.get(SITE_URL, {
        headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    });

    const pets = {};
    const cleanHtml = html.replace(/\\/g, '');
    const chunks = cleanHtml.split('"image":');

    for (let i = 1; i < chunks.length; i++) {
        const block = chunks[i].substring(0, 2000);
        const nameMatch = block.match(/"name"\s*:\s*"(.-)"/) || block.match(/"name"\s*:\s*"([^"]+)"/);

        if (nameMatch && nameMatch[1]) {
            const name = nameMatch[1];
            if (!pets[name]) {
                pets[name] = {
                    regular: {
                        fr: extractValue(block, 'rvalue'),
                        np: extractValue(block, 'rvalue - nopotion'),
                        r: extractValue(block, 'rvalue - ride'),
                        f: extractValue(block, 'rvalue - fly')
                    },
                    neon: {
                        fr: extractValue(block, 'nvalue'),
                        np: extractValue(block, 'nvalue - nopotion'),
                        r: extractValue(block, 'nvalue - ride'),
                        f: extractValue(block, 'nvalue - fly')
                    },
                    mega: {
                        fr: extractValue(block, 'mvalue'),
                        np: extractValue(block, 'mvalue - nopotion'),
                        r: extractValue(block, 'mvalue - ride'),
                        f: extractValue(block, 'mvalue - fly')
                    }
                };
            }
        }
    }

    return pets;
};

const getOrUpdatePetData = async () => {
    const now = Date.now();
    if (petCache && (now - lastFetchTime < CACHE_DURATION)) {
        return petCache;
    }
    petCache = await scrapeElvebredd();
    lastFetchTime = now;
    return petCache;
};

// GET /api/pets - Get all pet values
app.get('/api/pets', async (req, res) => {
    try {
        const data = await getOrUpdatePetData();
        res.json({ success: true, count: Object.keys(data).length, pets: data });
    } catch (error) {
        res.status(500).json({ success: false, error: 'Failed to fetch pet values from Elvebredd' });
    }
});

// GET /api/pet/:name - Get values for a specific pet by name (case-insensitive)
app.get('/api/pet/:name', async (req, res) => {
    try {
        const data = await getOrUpdatePetData();
        const targetName = req.params.name.toLowerCase();
        
        const matchedKey = Object.keys(data).find(k => k.toLowerCase() === targetName);

        if (matchedKey) {
            res.json({ success: true, name: matchedKey, data: data[matchedKey] });
        } else {
            res.status(404).json({ success: false, error: 'Pet not found' });
        }
    } catch (error) {
        res.status(500).json({ success: false, error: 'Failed to fetch pet value' });
    }
});

// POST /api/calculate - Compare two sides of a trade
app.use(express.json());
app.post('/api/calculate', async (req, res) => {
    try {
        const { offer1, offer2 } = req.body;
        const data = await getOrUpdatePetData();

        const calculateSideTotal = (items) => {
            if (!Array.isArray(items)) return 0;
            return items.reduce((acc, item) => {
                const pet = Object.keys(data).find(k => k.toLowerCase() === (item.name || '').toLowerCase());
                if (!pet) return acc;

                const form = item.form || 'regular';
                const potion = item.potion || 'fr';
                const value = data[pet]?.[form]?.[potion] || 0;

                return acc + value;
            }, 0);
        };

        const val1 = calculateSideTotal(offer1);
        const val2 = calculateSideTotal(offer2);
        const diff = Math.abs(val1 - val2);

        let result = 'FAIR';
        const maxVal = Math.max(val1, 1);
        if (Math.abs(val1 - val2) / maxVal >= 0.08) {
            result = val1 > val2 ? 'LOSE' : 'WIN';
        }

        res.json({
            success: true,
            yourValue: val1,
            theirValue: val2,
            difference: diff,
            result: result
        });
    } catch (error) {
        res.status(500).json({ success: false, error: 'Failed to calculate trade status' });
    }
});

app.listen(PORT, () => {
    console.log(`Elvebredd API Server running on port ${PORT}`);
});
