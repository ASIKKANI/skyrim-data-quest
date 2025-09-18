// backend/server.js
import express from "express";
import fetch from "node-fetch";
import cors from "cors";

const app = express();
app.use(cors());
app.use(express.json());

const PORT = 3000;
const GEMINI_API_KEY = "YOUR_KEY_HERE"; // Replace with your actual key
const GEMINI_URL = `https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generate?key=${GEMINI_API_KEY}`;

// Ask AI endpoint
app.post("/ask-ai", async (req, res) => {
  try {
    const { emailSubject = "", emailBody = "", question } = req.body;

    if (!question?.trim()) {
      return res.status(400).json({ answer: "❌ Question cannot be empty" });
    }

    // Call Gemini API
    const response = await fetch(GEMINI_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: `Email subject: ${emailSubject}\nEmail body: ${emailBody}\nQuestion: ${question}`,
        temperature: 0.2,
        maxOutputTokens: 300
      })
    });

    // Read the body only once
    const rawText = await response.text();

    let data;
    try {
      data = JSON.parse(rawText);
    } catch (parseErr) {
      console.error("Invalid JSON from Gemini API:", parseErr);
      console.error("Raw response:", rawText);
      return res.status(500).json({ answer: "❌ Gemini API returned invalid JSON" });
    }

    // Handle API errors
    if (!response.ok || data.error) {
      console.error("Gemini API error:", data.error || data);
      return res.status(500).json({
        answer: "❌ Gemini API error: " + (data.error?.message || "Unknown error")
      });
    }

    const answer = data?.candidates?.[0]?.output || "❌ No answer from AI";
    res.json({ answer });

  } catch (err) {
    console.error("Server error:", err);
    res.status(500).json({ answer: "❌ Failed to get AI response: " + err.message });
  }
});

// Start server
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
