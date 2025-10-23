from pathlib import Path
from typing import Optional
from log.handlers import GoogleSheetsHandler
import logging
import inspect
import config


def configure_logging(
    level: int = logging.INFO,
    logfile: Optional[Path] = None,
    console: bool = True,
    file_mode: str = "a",
    datefmt: str = "%Y-%m-%d %H:%M:%S",
    force: bool = True,
    app_name: Optional[str] = None,
) -> None:
    """
    Configure root logger handlers. Call this once in the application's
    entrypoint (not in library modules).

    If app_name is provided it will be shown in logs; otherwise the caller
    module name is inferred (falls back to caller filename when run as
    __main__).
    """

    # infer caller module name if not given
    if app_name is None:
        caller_frame = inspect.stack()[1].frame
        caller_mod = inspect.getmodule(caller_frame)
        if caller_mod and caller_mod.__name__ != "__main__":
            app_name = caller_mod.__name__
        else:
            # fallback to the caller filename (no package qualification)
            filepath = caller_frame.f_globals.get("__file__")
            if filepath:
                app_name = Path(filepath).stem
            else:
                app_name = "__main__"

    handlers = []
    if console:
        handlers.append(logging.StreamHandler())

    if logfile is None:
        logfile = config.LOG_DIR / f"{app_name}.log"

    handlers.append(logging.FileHandler(str(logfile), mode=file_mode))

    # use the inferred/app_name as a literal in the format so it shows the
    # module
    fmt = f"%(asctime)s %(levelname)s {app_name}: %(message)s"
    logging.basicConfig(
        level=level, format=fmt, datefmt=datefmt, handlers=handlers,
        force=force
    )

    gs = GoogleSheetsHandler(
        creds_json_path=str(config.GOOGLE_SHEET_CREDENTIALS_JSON),
        spreadsheet_key="1VYqr5SHX9Jxk-huHc831Chnxx-1VsZJlFs8on6I32XE",
        worksheet_name="logs",
        fmt=fmt
    )

    logging.getLogger().addHandler(gs)
