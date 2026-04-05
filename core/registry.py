import logging
from contextlib import contextmanager
from typing import Optional

import psycopg2
import psycopg2.extras


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DocumentRegistry:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    @contextmanager
    def __conn(self):
        conn = psycopg2.connect(self.connection_string)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def register(
        self, sha256: str, filename: str, source_url: str = None
    ) -> Optional[str]:
        sql = """
            INSERT INTO documents (sha256, filename, source_url, status, queued_at)
            VALUES (%s, %s, %s, 'queued', NOW())
            ON CONFLICT (sha256) DO NOTHING
            RETURNING doc_id
        """
        row = None
        with self.__conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (sha256, filename, source_url))
                row = cur.fetchone()
        if row is None:
            logger.debug("Already registered sha256=%s", sha256[:12])
            return

        logger.info("Registered doc_id=%s filename=%s", row[0], filename)
        return row[0]

    def mark_processing(self, doc_id: str) -> None:
        sql = "UPDATE documents SET status = 'processing' WHERE doc_id = %s"
        with self.__conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (doc_id,))
        logger.info("Processing doc_id=%s", doc_id)

    def mark_done(self, doc_id: str) -> None:
        sql = "UPDATE documents SET status = 'done', extracted_at = NOW() WHERE doc_id = %s"
        with self.__conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (doc_id,))
        logger.info("Done doc_id=%s", doc_id)

    def mark_failed(self, doc_id: str, error: str) -> None:
        sql = "UPDATE documents SET status = 'failed', error = %s WHERE doc_id = %s"
        with self.__conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (error, doc_id))
        logger.warning("Failed doc_id=%s error=%s", doc_id, error)

    def is_registered(self, sha256: str) -> bool:
        sql = "SELECT 1 FROM documents WHERE sha256 = %s"
        with self.__conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (sha256,))
                return cur.fetchone() is not None

    def is_processed(self, sha256: str) -> bool:
        sql = "SELECT 1 FROM documents WHERE sha256 = %s AND status = 'done'"
        with self.__conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (sha256,))
                return cur.fetchone() is not None

    def get(self, doc_id: str) -> Optional[dict]:
        sql = "SELECT * FROM documents WHERE doc_id = %s"
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, (doc_id,))
                row = cur.fetchone()
        return dict(row) if row else None

    def summary(self) -> dict:
        sql = """
            SELECT status, COUNT(*) as count
            FROM documents
            GROUP BY status
        """
        with self.__conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        return {r["status"]: r["count"] for r in rows}
        # return {r[0]: r[1] for r in rows} #If not using RealDictCursor


if __name__ == "__main__":

    DSN = "postgresql://ingestion_user:ingestion_pass@localhost:5432/ingestion"
    registry = DocumentRegistry(DSN)
    id = registry.register("1357", "test3")
    registry.mark_processing("9c9b25bd-f7fe-41ae-aa65-e8950c32b1df")
    registry.mark_failed(
        "4e2f33c6-340a-48ec-8160-46c82c5828ca", "Failed to process the doc"
    )
    print(registry.is_registered("jdhkfdh"))
    print(registry.is_processed("1357"))
    print(registry.summary())
    print(registry.register("1357", "test3"))
