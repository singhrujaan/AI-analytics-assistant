# project4/test_imports.py
# Quick check that all packages are available

print("Testing imports...")

try:
    import pandas as pd
    print("✓ pandas", pd.__version__)
except ImportError as e:
    print("✗ pandas:", e)

try:
    import matplotlib
    print("✓ matplotlib", matplotlib.__version__)
except ImportError as e:
    print("✗ matplotlib:", e)

try:
    import sklearn
    print("✓ scikit-learn", sklearn.__version__)
except ImportError as e:
    print("✗ scikit-learn:", e)

try:
    import numpy as np
    print("✓ numpy", np.__version__)
except ImportError as e:
    print("✗ numpy:", e)

try:
    from qdrant_client import QdrantClient
    print("✓ qdrant-client")
except ImportError as e:
    print("✗ qdrant-client:", e)

try:
    from anthropic import Anthropic
    print("✓ anthropic")
except ImportError as e:
    print("✗ anthropic:", e)

try:
    import fastapi
    print("✓ fastapi", fastapi.__version__)
except ImportError as e:
    print("✗ fastapi:", e)

try:
    import uvicorn
    print("✓ uvicorn")
except ImportError as e:
    print("✗ uvicorn:", e)

print("\nAll done.")