const express = require("express");
const router = express.Router();
const mongoose = require("mongoose");



const Inflacion = mongoose.model(
  "Inflacion",
  new mongoose.Schema({
    fecha:  String,
    valor:  Number,
    indice: Number,
    tipo:   String,
  }),
  "inflacion"
);

const CambioOficial = mongoose.model(
  "CambioOficial",
  new mongoose.Schema({
    fecha: String,
    valor: Number,
    tipo:  String,
  }),
  "cambio_oficial"
);

const CambioBlue = mongoose.model(
  "CambioBlue",
  new mongoose.Schema({
    blue_compra:    Number,
    blue_venta:     Number,
    ccl_venta:      Number,
    mep_venta:      Number,
    tipo:           String,
    fecha_registro: String,
  }),
  "cambio_blue"
);

const Empleo = mongoose.model(
  "Empleo",
  new mongoose.Schema({
    fecha:        String,
    desocupacion: Number,
    empleo:       Number,
    actividad:    Number,
    tipo:         String,
  }),
  "empleo"
);


router.get("/inflacion", async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 12;
    const datos = await Inflacion.find({}, { _id: 0 }).sort({ fecha: -1 }).limit(limit);
    res.json({ ok: true, total: datos.length, data: datos });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

router.get("/cambio-oficial", async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 12;
    const datos = await CambioOficial.find({}, { _id: 0 }).sort({ fecha: -1 }).limit(limit);
    res.json({ ok: true, total: datos.length, data: datos });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

router.get("/cambio-blue", async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 24;
    const datos = await CambioBlue.find({}, { _id: 0 }).sort({ fecha_registro: -1 }).limit(limit);
    res.json({ ok: true, total: datos.length, data: datos });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

router.get("/cambio-blue/ultimo", async (req, res) => {
  try {
    const dato = await CambioBlue.findOne({}, { _id: 0 }).sort({ fecha_registro: -1 });
    if (!dato) return res.status(404).json({ ok: false, error: "Sin datos" });
    res.json({ ok: true, data: dato });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

router.get("/empleo", async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 8;
    const datos = await Empleo.find({}, { _id: 0 }).sort({ fecha: -1 }).limit(limit);
    res.json({ ok: true, total: datos.length, data: datos });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

router.get("/resumen", async (req, res) => {
  try {
    const [inflacion, oficial, blue, empleo] = await Promise.all([
      Inflacion.findOne({}, { _id: 0 }).sort({ fecha: -1 }),
      CambioOficial.findOne({}, { _id: 0 }).sort({ fecha: -1 }),
      CambioBlue.findOne({}, { _id: 0 }).sort({ fecha_registro: -1 }),
      Empleo.findOne({}, { _id: 0 }).sort({ fecha: -1 }),
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