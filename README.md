# Neotuitive

A Python library for visualizing and analyzing Near-Earth Objects (NEOs) risk list, using data from ESA's Near-Earth Object Coordination Centre.

## Installation

```bash
pip install neotuitive
```

## Features

- Fetch and store NEO data from ESA's risk list (https://neo.ssa.esa.int/risk-list) using their API (https://neo.ssa.esa.int/computer-access)
- Visualize NEO orbits in 2D and 3D
- Intuitions about NEO which are in the risk list and their potential impact on Earth

## Quick Start

```python
from api.handler import NeoRiskListAPI
from db.repository import NeoRiskListDB
from data import DataLoader
from service import Neo
from visual import Show
from datetime import datetime, timedelta

if __name__ == "__main__":
    # Initialize components
    api = NeoRiskListAPI()
    db = NeoRiskListDB("near_earth_objects.db")
    loader = DataLoader(api, db)

    # Load data if needed - Stores them in sqlite database
    loader.initialize_storage()

    # Create service and visualization instance
    neo_service = Neo(db)
    show = Show(neo_service)

    # Example - Plot specific NEO orbit in 3D
    neo = neo_service.from_name("2024YR4")
    if neo:
        show.orbit_3D(neo.name, datetime.now())

```

