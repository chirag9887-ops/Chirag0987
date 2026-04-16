const express = require("express");
const app = express();

const PORT = process.env.PORT || 3000;

// 👉 yahan apni key set karo
const API_KEY = process.env.API_KEY;

// Home route
app.get("/", (req, res) => {
    res.send("API is running ✅");
});

// Protected route
app.get("/api", (req, res) => {
    const key = req.query.key;

    if (key !== API_KEY) {
        return res.status(401).send("Invalid API Key ❌");
    }

    res.json({
        status: "success",
        message: "Access granted 🔥"
    });
});

app.listen(PORT, () => {
    console.log("Server running");
});