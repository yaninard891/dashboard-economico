

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timezone
import logging



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),                          # consola
        logging.FileHandler("auto_fetch.log", encoding="utf-8"),  # archivo
    ]
)
log = logging.getLogger(__name__)


def fetch_rapido():
   
    log.info(" fetch_rapido iniciado...")
    try:
        from apis import obtener_tipo_cambio_blue
        from guardar_mongo import conectar, guardar_cambio_blue, crear_indices

        blue = obtener_tipo_cambio_blue()
        if blue:
            db = conectar()
            crear_indices(db)
            guardar_cambio_blue(db, blue)
            log.info(f" fetch_rapido OK — blue=${blue.get('blue_venta')} CCL=${blue.get('ccl_venta')}")
        else:
            log.warning("fetch_rapido: sin datos de blue")

    except Exception as e:
        log.error(f" fetch_rapido falló: {e}")


def fetch_completo():
    
    log.info(" fetch_completo iniciado...")
    try:
        from apis import obtener_todos_los_datos
        from guardar_mongo import guardar_todo

        datos = obtener_todos_los_datos()
        guardar_todo(datos)
        log.info(" fetch_completo OK")

    except Exception as e:
        log.error(f" fetch_completo falló: {e}")



def iniciar_scheduler():
    scheduler = BlockingScheduler(timezone="America/Argentina/Buenos_Aires")

    
    scheduler.add_job(
        fetch_completo,
        trigger=IntervalTrigger(hours=24),
        id="fetch_completo",
        name="Fetch completo (inflación + oficial + blue + empleo)",
        next_run_time=datetime.now(timezone.utc),   # corre inmediatamente al iniciar
    )


    scheduler.add_job(
        fetch_rapido,
        trigger=IntervalTrigger(hours=1),
        id="fetch_rapido",
        name="Fetch rápido (dólar blue / CCL / MEP)",
    )

    log.info("=" * 50)
    log.info("  Dashboard Económico — Auto Fetch iniciado")
    log.info("  fetch_completo : cada 24 horas")
    log.info("  fetch_rapido   : cada 1 hora")
    log.info("  Zona horaria   : America/Argentina/Buenos_Aires")
    log.info("  Logs           : auto_fetch.log")
    log.info("  Ctrl+C para detener")
    log.info("=" * 50)

    try:
        scheduler.start()
    except KeyboardInterrupt:
        log.info("Scheduler detenido por el usuario.")
        scheduler.shutdown()



if __name__ == "__main__":
    iniciar_scheduler()
