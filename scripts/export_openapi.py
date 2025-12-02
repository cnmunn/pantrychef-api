import json
import sys
from pathlib import Path

# Add project root to path so we can import the app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


def export_openapi_schema(filename: str = ".stainless/openapi.json"):
    """Export the FastAPI OpenAPI schema to a JSON file for Stainless SDK generation."""
    schema = app.openapi()
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(schema, f, indent=2)
    print(f"OpenAPI schema exported to {filename}")

if __name__ == "__main__":
    export_openapi_schema()