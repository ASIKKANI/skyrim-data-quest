const express = require("express");
const path = require("path");
const app = express();

// serve static files from "public" folder
app.use(express.static(path.join(__dirname, "public")));

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.listen(5000, () => {
  console.log("Website running at http://localhost:5000");
});
