import os
from dotenv import load_dotenv
from app import create_app


def run() -> None:
    load_dotenv()
    app = create_app()

    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "0") == "1")


if __name__ == "__main__":
    run()
