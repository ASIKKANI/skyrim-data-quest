const express = require('express');
const cors = require('cors');
const libmime = require('libmime');
const app = express();
app.use(cors());
app.use(express.json());

app.post('/ask-ai', (req, res) => {
  let { question, emailSubject, emailBody } = req.body;
  emailSubject = libmime.decodeWords(emailSubject || '');
  res.json({ answer: `AI says: "${question}" about "${emailSubject}"` });
});

app.listen(3000, () => console.log('AI server running on port 3000'));