from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = BASE_DIR / "credentials" / "credentials.json"
TOKEN_FILE = BASE_DIR / "credentials" / "token.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_FILE,
        SCOPES,
    )

    credentials = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(
        credentials.to_json(),
        encoding="utf-8",
    )

    print("Autorización de Gmail completada correctamente.")

if __name__ == "__main__":
    main()
