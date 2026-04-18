"""
啟動開發 server 用這個：
  python3 start_server.py
"""
from dotenv import load_dotenv
load_dotenv()

import os
os.environ.setdefault("PORT", "5001")

from app import create_app
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f"\n✅ TravelWise backend running at http://localhost:{port}")
    print(f"📖 Swagger UI: http://localhost:{port}/api/docs\n")
    app.run(host="0.0.0.0", port=port, debug=False)
