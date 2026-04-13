const express = require("express");
const app = express();

app.use(express.json());

// Fake DB (memory)
let keys = [
    { key: "venomx123", expiry: "2026-12-31" }
];

// Check API
app.get("/api", (req, res) => {
    const userKey = req.query.key;

    const found = keys.find(k => k.key === userKey);

    if (!found) {
        return res.json({ status: "error", message: "Invalid Key ❌" });
    }

    const today = new Date().toISOString().split("T")[0];

    if (today > found.expiry) {
        return res.json({ status: "expired", message: "Key Expired ⛔" });
    }

    res.json({ status: "success", message: "Access Granted ✅" });
});

// Generate Key
app.get("/generate", (req, res) => {
    const newKey = "key_" + Math.random().toString(36).substring(2, 10);

    const expiry = "2026-12-31";

    keys.push({ key: newKey, expiry });

    res.json({ key: newKey, expiry });
});

app.listen(3000, () => console.log("Server running on port 3000"));