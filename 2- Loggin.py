# =====================================================================
# 1. LOGGING
# =====================================================================
RUTA_LOG = Path(__file__).parent / "logs" / "software_fj.log"


def obtener_logger() -> logging.Logger:
    logger = logging.getLogger("software_fj")
    if not logger.handlers:
        RUTA_LOG.parent.mkdir(exist_ok=True)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(RUTA_LOG, mode="a", encoding="utf-8")
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s"))
        logger.addHandler(handler)
    return logger


log = obtener_logger()
