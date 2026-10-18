""" Run the Delivery Pipeline with one command
    steps: generate -> clean -> load => export.
    if a step fails, the pipeline will stop and ddo not next step
"""
import logging
import time

from src import load, config, generate, clean, export

logger = logging.getLogger("Delivery Pipeline")
STEPS = [
    ("generate", generate.run),
    ("clean", clean.run),
    ("load", load.run),
    ("export", export.run),
]

def main() -> None:
    logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)

    for name, run_step in STEPS:
        logger.info("Step started: %s", name)
        started_at = time.perf_counter()
        run_step()
        logger.info("Step finished: %s (%.1f s)", name, time.perf_counter() - started_at)

    logger.info("Pipeline finished successfully")

if __name__ == "__main__":
    main()
