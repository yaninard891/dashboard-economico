import { useEffect, useState } from "react";
import axios from "axios";
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, Title, Tooltip, Legend, Filler
} from "chart.js";
import { Bar, Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, Title, Tooltip, Legend, Filler
);

const API = "http://localhost:5000/api";
const fmt = (n) => n?.toLocaleString("es-AR", { minimumFractionDigits: 1, maximumFractionDigits: 2 }) ?? "—";
const fmtPeso = (n) => n ? `$${n.toLocaleString("es-AR")}` : "—";

export default function Dashboard() {
  const [resumen, setResumen]     = useState(null);
  const [inflacion, setInflacion] = useState([]);
  const [oficial, setOficial]     = useState([]);
  const [empleo, setEmpleo]       = useState([]);
  const [loading, setLoading]     = useState(true);

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/resumen`),
      axios.get(`${API}/inflacion?limit=12`),
      axios.get(`${API}/cambio-oficial?limit=12`),
      axios.get(`${API}/empleo?limit=8`),
    ]).then(([r, inf, of, emp]) => {
      setResumen(r.data.data);
      setInflacion([...inf.data.data].reverse());
      setOficial([...of.data.data].reverse());
      setEmpleo([...emp.data.data].reverse());
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="loading">
      <div className="spinner" />
      <p>Cargando datos económicos...</p>
    </div>
  );

  const blue   = resumen?.blue_actual;
  const infUlt = resumen?.inflacion_ultimo;
  const ofUlt  = resumen?.oficial_ultimo;
  const empUlt = resumen?.empleo_ultimo;

  const inflacionChart = {
    labels: inflacion.map(d => d.fecha),
    datasets: [{
      label: "Inflación mensual %",
      data: inflacion.map(d => d.valor),
      backgroundColor: inflacion.map(d =>
        d.valor > 10 ? "rgba(239,68,68,0.8)" :
        d.valor > 5  ? "rgba(251,146,60,0.8)" :
                       "rgba(34,197,94,0.8)"
      ),
      borderRadius: 6,
      borderSkipped: false,
    }]
  };

  const cambioChart = {
    labels: oficial.map(d => d.fecha),
    datasets: [{
      label: "Dólar Oficial",
      data: oficial.map(d => d.valor),
      borderColor: "#3b82f6",
      backgroundColor: "rgba(59,130,246,0.1)",
      tension: 0.4,
      fill: true,
      pointRadius: 4,
      pointBackgroundColor: "#3b82f6",
    }]
  };

  const empleoChart = {
    labels: empleo.map(d => d.fecha),
    datasets: [
      {
        label: "Desocupación %",
        data: empleo.map(d => d.desocupacion),
        borderColor: "#ef4444",
        backgroundColor: "rgba(239,68,68,0.1)",
        tension: 0.4,
        fill: true,
        pointRadius: 4,
      },
      {
        label: "Empleo %",
        data: empleo.map(d => d.empleo),
        borderColor: "#22c55e",
        backgroundColor: "rgba(34,197,94,0.1)",
        tension: 0.4,
        fill: true,
        pointRadius: 4,
      }
    ]
  };

  const optsBar = {
    responsive: true,
    plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => ` ${fmt(ctx.raw)}%` } } },
    scales: {
      y: { grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8" } },
      x: { grid: { display: false }, ticks: { color: "#94a3b8" } }
    }
  };

  const optsLine = {
    responsive: true,
    plugins: { legend: { labels: { color: "#94a3b8" } } },
    scales: {
      y: { grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8" } },
      x: { grid: { display: false }, ticks: { color: "#94a3b8" } }
    }
  };

  return (
    <div className="dashboard">
      <header className="header">
        <div className="header-left">
          <h1>Dashboard <span>Económico</span></h1>
          <p>PAIS: Argentina--- Datos en tiempo real</p>
        </div>
        <div className="header-right">
          <span className="badge">Actualizados</span>
        </div>
      </header>

      <section className="cards">
        <div className="card card-blue">
          <p className="card-label">Dólar Blue</p>
          <p className="card-value">{fmtPeso(blue?.blue_venta)}</p>
          <p className="card-sub">Compra {fmtPeso(blue?.blue_compra)}</p>
        </div>
        <div className="card card-green">
          <p className="card-label">Dólar Oficial</p>
          <p className="card-value">{fmtPeso(ofUlt?.valor)}</p>
          <p className="card-sub">{ofUlt?.fecha}</p>
        </div>
        <div className="card card-ccl">
          <p className="card-label">CCL</p>
          <p className="card-value">{fmtPeso(blue?.ccl_venta)}</p>
          <p className="card-sub">MEP {fmtPeso(blue?.mep_venta)}</p>
        </div>
        <div className="card card-red">
          <p className="card-label">Inflación</p>
          <p className="card-value">{fmt(infUlt?.valor)}%</p>
          <p className="card-sub">{infUlt?.fecha}</p>
        </div>
        <div className="card card-purple">
          <p className="card-label">Desocupación</p>
          <p className="card-value">{fmt(empUlt?.desocupacion)}%</p>
          <p className="card-sub">Empleo {fmt(empUlt?.empleo)}%</p>
        </div>
      </section>

      <section className="charts">
        <div className="chart-card">
          <h2>Inflación Mensual</h2>
          <p className="chart-sub">Variación % IPC — últimos 12 meses</p>
          <Bar data={inflacionChart} options={optsBar} />
        </div>
        <div className="chart-card">
          <h2>Tipo de Cambio Oficial</h2>
          <p className="chart-sub">Dólar BNA vendedor — últimos 12 meses</p>
          <Line data={cambioChart} options={optsLine} />
        </div>
        <div className="chart-card chart-wide">
          <h2>Mercado Laboral</h2>
          <p className="chart-sub">Tasas EPH — últimos trimestres</p>
          <Line data={empleoChart} options={optsLine} />
        </div>
      </section>
    </div>
  );
}