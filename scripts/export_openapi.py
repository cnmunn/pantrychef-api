#!/usr/bin/env python
"""Export OpenAPI spec from FastAPI app without running the server."""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.main import app

def export_spec():
    """Export the OpenAPI spec to .stainless/openapi.json"""
    spec = app.openapi()
    output_path = Path(__file__).parent.parent / ".stainless" / "openapi.json"
    
    with open(output_path, "w") as f:
        json.dump(spec, f, indent=2)
    
    print(f"✓ Exported OpenAPI spec to {output_path}")
    print(f"  - {len(spec.get('paths', {}))} endpoints")
    print(f"  - {len(spec.get('components', {}).get('schemas', {}))} schemas")

if __name__ == "__main__":
    export_spec()
