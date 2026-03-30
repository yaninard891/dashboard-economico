const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
require("dotenv").config();

const apiRoutes = require("./routes/api");

const app = express();
const PORT = process.env.PORT || 5000;
const MONGO_URI = process.env.MONGO_URI || "mongodb://localhost:27017/dashboard_economico";


app.use(cors());
app.use(express.json());


app.use("/api", apiRoutes);


app.get("/", (req, res) => {
  res.json({
    status: "ok",
    mensaje: "Dashboard Económico API corriendo",
    version: "1.0.0",
    endpoints: [
      "GET /api/inflacion",
      "GET /api/cambio-oficial",
      "GET /api/cambio-blue",
      "GET /api/cambio-blue/ultimo",
      "GET /api/empleo",
      "GET /api/resumen",
    ],
  });
});


mongoose
  .connect(MONGO_URI)
  .then(() => {
    console.log(`✓ MongoDB conectado → ${MONGO_URI}`);
    app.listen(PORT, () => {
      console.log(`✓ Servidor corriendo en http://localhost:${PORT}`);
      console.log(`  Probá: http://localhost:${PORT}/api/resumen`);
    });
  })
  .catch((err) => {
    console.error("Error al conectar MongoDB:", err.message);
    process.exit(1);
  });