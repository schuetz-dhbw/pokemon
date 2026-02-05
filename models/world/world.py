from dataclasses import dataclass, field
from typing import Dict

from models.world.location import Location

@dataclass
class World:
    """ Container für alle Orte (Locations) in der Spielwelt """
    locations: Dict[str, Location] = field(default_factory=dict)
    starting_location: str = "city_alabastia"

    def get_location(self, location_id: str) -> Location | None:
        """ Hilfsmethode um eine Location über ihre ID erhalten """
        return self.locations.get(location_id)

    def add_location(self, location: Location) -> None:
        """ Location zur Welt hinzufügen """
        self.locations[location.id] = location