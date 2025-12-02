#!/usr/bin/env python
"""Export OpenAPI spec from FastAPI app without running the server."""

import json
import sys
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.main import app


def export_spec(format: str = "both"):
    """Export the OpenAPI spec to .stainless/openapi.json and/or openapi.yaml
    
    Args:
        format: "json", "yaml", or "both"
    """
    spec = app.openapi()
    output_dir = Path(__file__).parent.parent / ".stainless"
    
    # Export JSON
    if format in ("json", "both"):
        json_path = output_dir / "openapi.json"
        with open(json_path, "w") as f:
            json.dump(spec, f, indent=2)
        print(f"✓ Exported OpenAPI spec to {json_path}")
    
    # Export YAML
    if format in ("yaml", "both"):
        if not HAS_YAML:
            print("⚠ PyYAML not installed. Run: uv add pyyaml")
            print("  Skipping YAML export.")
        else:
            yaml_path = output_dir / "openapi.yaml"
            with open(yaml_path, "w") as f:
                yaml.dump(spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            print(f"✓ Exported OpenAPI spec to {yaml_path}")
    
    print(f"  - {len(spec.get('paths', {}))} endpoints")
    print(f"  - {len(spec.get('components', {}).get('schemas', {}))} schemas")


if __name__ == "__main__":
    # Check for command line args
    format_arg = "both"
    if len(sys.argv) > 1:
        format_arg = sys.argv[1].lower()
        if format_arg not in ("json", "yaml", "both"):
            print("Usage: python export_openapi.py [json|yaml|both]")
            sys.exit(1)
    
    export_spec(format_arg)
