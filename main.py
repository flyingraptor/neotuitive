from neotuitive.api.handler import NeoRiskListAPI
from neotuitive.db.repository import NeoRiskListDB
from neotuitive.data import DataLoader
from neotuitive.service import Neo
from neotuitive.visualizer import Show

if __name__ == "__main__":
    # Initialize components
    api = NeoRiskListAPI()
    db = NeoRiskListDB("near_earth_objects.db")
    loader = DataLoader(api, db)

    # Load data if needed - Stores them in sqlite database
    loader.initialize_storage()

    # Create service and visualization instancew
    neo_service = Neo(db)
    show = Show(neo_service)

    # Example - Show 10000 NEOs
    show.random3d(10000)