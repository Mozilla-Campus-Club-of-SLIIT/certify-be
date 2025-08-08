const mongoose = require("mongoose");

const certificateSchema = new mongoose.Schema({
  credentialId: { type: String, required: true, unique: true },
  name: { type: String, required: true },
  course: { type: String, required: true },
  dateIssued: { type: Date, required: true },
  issuer: { type: String, required: true },
  
});

const Certificate = mongoose.model("Certificate", certificateSchema);

module.exports = Certificate;
