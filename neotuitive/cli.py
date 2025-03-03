from typing import Optional
import argparse

from .service import Neo
from .db.repository import NeoRiskListDB

class Terminal:
    """Handles command-line interface operations."""
    
    def __init__(self, neo_service: Optional[Neo] = None):
        """
        Initialize Terminal with optional Neo service.
        
        Args:
            neo_service: Neo service instance, if None creates a new one
        """
        if neo_service is None:
            db = NeoRiskListDB()
            neo_service = Neo(db)
        self.neo_service = neo_service

    def search_neo(self, search_term: str, page: int = 1, page_size: int = 10):
        """
        Search for NEOs by name and print results to terminal.
        
        Args:
            search_term: Search term for NEO name
            page: Page number (default: 1)
            page_size: Results per page (default: 10)
        """
        try:
            neos = self.neo_service.search(search_term, page, page_size)
            
            if not neos:
                print(f"No NEOs found matching '{search_term}'")
                return
            
            print(f"\nFound {len(neos)} NEOs matching '{search_term}':\n")
            
            for neo in neos:
                print("-" * 80)
                print(f"Name: {neo.name}")
                print(f"Diameter: {neo.diameter:.1f} meters")
                print(f"Velocity: {neo.velocity:.1f} km/s")
                print(f"Impact Probability (max): {neo.ip_max:.6f}")
                print(f"Palermo Scale (max): {neo.ps_max:.2f}")
                print(f"Torino Scale: {neo.ts}")
                print()
                
        except Exception as e:
            print(f"Error searching for NEOs: {str(e)}")


def main():
    """Entry point for command-line interface."""
    parser = argparse.ArgumentParser(description="Search for Near-Earth Objects")
    parser.add_argument("search", help="Search term for NEO name")
    parser.add_argument("--page", type=int, default=1, help="Page number")
    parser.add_argument("--size", type=int, default=10, help="Results per page")
    
    args = parser.parse_args()
    
    terminal = Terminal()
    terminal.search_neo(args.search, args.page, args.size)


if __name__ == "__main__":
    main() 