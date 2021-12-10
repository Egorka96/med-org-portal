from sw_logger.handlers import DbHandler as BaseDbHandler


class DbHandler(BaseDbHandler):
    @staticmethod
    def get_log_model():
        from core import models
        return models.Log

    def _emit_extra(self, log, record):
        from core import models

        if not hasattr(record, 'object'):
            return

        if hasattr(record, 'fk_object_id'):
            log.fk_object_id = record.fk_object_id

        if hasattr(record, 'http_request_get'):
            log.http_request_get = record.http_request_get
        if hasattr(record, 'http_request_post'):
            log.http_request_post = record.http_request_post