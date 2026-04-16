const express = require("express");
const app = express();

const PORT = process.env.PORT || 3000;
const API_KEY = process.env.API_KEY || "12345";

// Home route
app.get("/", (req, res) => {
    res.send("API is running ✅");
});

// Protected API route
app.get("/api", (req, res) => {
    const key = req.query.key;

    if (key !== API_KEY) {
        return res.status(401).send("Invalid API Key ❌");
    }

    res.json({
        status: "success",
        message: "API working 🔥"
    });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});