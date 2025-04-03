import os
from requests import Session

app_session = Session()
app_session.headers["User-Agent"] = "waves-forecast/1.0.0"

IS_DEVELOPMENT_MODE = os.environ.get("IS_DEVELOPMENT") in ("1", "True", "true")
