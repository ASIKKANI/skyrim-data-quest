const express = require("express");
const path = require("path");
const app = express();

// Serve everything inside frontend/ as static files
app.use(express.static(path.join(__dirname, "frontend")));

// Default route → send index.html
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "frontend", "index.html"));
});

app.listen(5000, () => {
  console.log("Website running at http://localhost:5000");
});

