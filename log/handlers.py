import logging
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime, timezone


class GoogleSheetsHandler(logging.Handler):
    """
    Logging handler that appends log records to a Google Sheet.
    Uses a service-account JSON key file.
    """
    def __init__(
            self, creds_json_path: str, spreadsheet_key: str,
            worksheet_name: str = None, fmt: str = None
    ):
        super().__init__()
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(
            creds_json_path, scopes=scopes
        )
        client = gspread.authorize(creds)
        self.sh = client.open_by_key(spreadsheet_key)
        if worksheet_name:
            self.ws = self.sh.worksheet(worksheet_name)
        else:
            self.ws = self.sh.sheet1

        # Ensure the worksheet has a header row; create one if the first row
        # is empty
        header = [
            "date", "time", "level", "module", "function",
            "line number", "message"
        ]

        try:
            first_row = self.ws.row_values(1)

        except Exception:
            first_row = []

        first_row_empty = len(first_row) == 0
        first_row_is_all_blank = all(
            (not str(v).strip()) for v in first_row[: len(header)]
        )
        if first_row_empty or first_row_is_all_blank:
            try:
                # write header starting at A1
                self.ws.update("A1", [header])
            except Exception:
                # best-effort: ignore failures (network/quotas) so logging
                # still proceeds
                pass

        if fmt:
            self.setFormatter(logging.Formatter(fmt))

    def emit(self, record: logging.LogRecord):
        try:
            timestamp = datetime.fromtimestamp(record.created, timezone.utc)
            row = [
                timestamp.date().isoformat(),
                timestamp.time().isoformat(),
                record.levelname,
                record.filename,
                record.funcName,
                record.lineno,
                record.getMessage(),
            ]
            # append_row is simple; consider batch writes for higher throughput
            self.ws.append_row(row, value_input_option="RAW")
        except Exception:
            self.handleError(record)
