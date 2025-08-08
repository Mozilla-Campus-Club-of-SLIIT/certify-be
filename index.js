require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const app = express();
app.use(cors());
const PORT = process.env.PORT || 5000;

// MongoDB connection
mongoose
  .connect(process.env.MONGODB_URI)
  .then(async () => {
    console.log("Connected to MongoDB");
    // Auto-create sample collection if not exists
    const Certificate = require("./models/Certificate");
    const count = await Certificate.countDocuments();
    if (count === 0) {
      const { v4: uuidv4 } = require("uuid");
      await Certificate.create({
        credentialId: uuidv4(),
        name: "Sample User",
        course: "Sample Course",
        dateIssued: new Date(),
        issuer: "Certify Team",
      });
      console.log("Sample certificate inserted with unique credentialId.");
    }
  })
  .catch((err) => console.error("MongoDB connection error:", err));

app.get("/", (req, res) => {
  res.send("Hello, Certify!");
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
