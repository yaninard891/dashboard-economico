const express = require("express");
const router = express.Router();
const mongoose = require("mongoose");

const db = () => mongoose.connection.db;


router.get("/test", async (req, res) => {
  try {
    const colecciones = await db().listCollections().toArray();
    const inflacion = await db().collection("inflacion").find({}).limit(2).toArray();
    res.json({
      colecciones: colecciones.map(c => c.name),
      inflacion_muestra: inflacion
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});


router.get("/inflacion", async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 12;
    const datos = await db().collection("inflacion")
      .find({}, { projection: { _id: 0 } })
      .sort({ fecha: -1 })
      .limit(limit)
      .toArray();
    res.json({ ok: true, total: datos.length, data: datos });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});


router.get("/cambio-oficial", async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 12;
    const datos = await db().collection("cambio_oficial")
      .find({}, { projection: { _id: 0 } })
      .sort({ fecha: -1 })
      .limit(limit)
      .toArray();
    res.json({ ok: true, total: datos.length, data: datos });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});


router.get("/cambio-blue", async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 24;
    const datos = await db().collection("cambio_blue")
      .find({}, { projection: { _id: 0 } })
      .sort({ fecha_registro: -1 })
      .limit(limit)
      .toArray();
    res.json({ ok: true, total: datos.length, data: datos });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});


router.get("/cambio-blue/ultimo", async (req, res) => {
  try {
    const dato = await db().collection("cambio_blue")
      .findOne({}, { projection: { _id: 0 }, sort: { fecha_registro: -1 } });
    if (!dato) return res.status(404).json({ ok: false, error: "Sin datos" });
    res.json({ ok: true, data: dato });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});


router.get("/empleo", async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 8;
    const datos = await db().collection("empleo")
      .find({}, { projection: { _id: 0 } })
      .sort({ fecha: -1 })
      .limit(limit)
      .toArray();
    res.json({ ok: true, total: datos.length, data: datos });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});


router.get("/resumen", async (req, res) => {
  try {
    const [inflacion, oficial, blue, empleo] = await Promise.all([
      db().collection("inflacion").findOne({}, { projection: { _id: 0 }, sort: { fecha: -1 } }),
      db().collection("cambio_oficial").findOne({}, { projection: { _id: 0 }, sort: { fecha: -1 } }),
      db().collection("cambio_blue").findOne({}, { projection: { _id: 0 }, sort: { fecha_registro: -1 } }),
      db().collection("empleo").findOne({}, { projection: { _id: 0 }, sort: { fecha: -1 } }),
    ]);
    res.json({
      ok: true,
      data: {
        inflacion_ultimo: inflacion || null,
        oficial_ultimo:   oficial   || null,
        blue_actual:      blue      || null,
        empleo_ultimo:    empleo    || null,
      },
    });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

module.exports = router;