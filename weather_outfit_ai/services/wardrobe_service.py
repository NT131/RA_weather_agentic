
import json
import uuid
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings

from weather_outfit_ai.models.schemas import PersonalClothingItem


class WardrobeService:
    """Wardrobe service with only essential functionality."""

    def __init__(self, db_path: str | None = None):
        """Initialize the wardrobe service with ChromaDB."""
        if db_path is None:
            db_path = str(Path.cwd() / "wardrobe_db")

        self.client = chromadb.PersistentClient(
            path=db_path, settings=Settings(anonymized_telemetry=False)
        )

        self.collection = self.client.get_or_create_collection(
            name="wardrobe",
            metadata={"description": "Personal clothing items with semantic search"},
        )

    def add_clothing_item(self, item: PersonalClothingItem) -> str:
        """Add a clothing item to the wardrobe vector database."""
        if not item.id:
            item.id = str(uuid.uuid4())

        searchable_document = self._create_searchable_document(item)
        metadata = self._create_item_metadata(item)

        self.collection.add(
            ids=[item.id], documents=[searchable_document], metadatas=[metadata]
        )

        return item.id

    def remove_clothing_item(self, item_id: str) -> bool:
        """Remove a clothing item from the wardrobe."""
        try:
            self.collection.delete(ids=[item_id])
            return True
        except Exception:
            return False

    def clear_wardrobe(self) -> bool:
        """Clear all items from the wardrobe."""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name="wardrobe")
            self.collection = self.client.get_or_create_collection(
                name="wardrobe",
                metadata={"description": "Personal clothing items with semantic search"},
            )
            return True
        except Exception:
            return False

    def list_all_items(self) -> list[PersonalClothingItem]:
        """List all clothing items in the wardrobe."""
        try:
            result = self.collection.get()
            items = []
            for i in range(len(result["ids"])):
                item = self._result_to_clothing_item(result, i)
                if item:
                    items.append(item)
            return items
        except Exception:
            return []

    def semantic_search(self, query: str, limit: int = 20) -> list[PersonalClothingItem]:
        """Perform semantic search on wardrobe items."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                include=["metadatas", "documents", "distances"],
            )

            items = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    item = self._result_to_clothing_item(results, i, is_search=True)
                    if item:
                        items.append(item)

            return items
        except Exception:
            return []

    def filter_by_category(self, category: str, limit: int = 50) -> list[PersonalClothingItem]:
        """Filter items by category."""
        category_query = f"{category} clothing items"
        all_results = self.semantic_search(category_query, limit=limit * 2)

        return [
            item for item in all_results if item.category.lower() == category.lower()
        ][:limit]

    def get_wardrobe_stats(self) -> dict[str, Any]:
        """Get statistics about the wardrobe."""
        all_items = self.list_all_items()

        if not all_items:
            return {"total_items": 0, "categories": {}, "colors": {}, "materials": {}}

        categories = {}
        colors = {}
        materials = {}

        for item in all_items:
            categories[item.category] = categories.get(item.category, 0) + 1
            colors[item.color] = colors.get(item.color, 0) + 1
            for color in item.secondary_colors:
                colors[color] = colors.get(color, 0) + 1
            materials[item.material] = materials.get(item.material, 0) + 1

        return {
            "total_items": len(all_items),
            "categories": categories,
            "colors": colors,
            "materials": materials,
        }

    def _create_searchable_document(self, item: PersonalClothingItem) -> str:
        """Create a rich searchable document for vector embedding."""
        parts = [
            f"{item.name} - {item.subcategory} {item.category}",
            f"Made of {item.material} in {item.color}",
            item.description,
            f"Primary color: {item.color}",
            f"Colors: {', '.join([item.color, *item.secondary_colors])}",
            f"Suitable for: {', '.join(item.weather_suitability)}",
            f"Best seasons: {', '.join(item.season)}",
            f"Warmth level: {item.warmth_level}/5",
            f"Formality: {item.formality}/5",
            f"Tags: {', '.join(item.tags)}",
        ]

        if item.brand:
            parts.append(f"Brand: {item.brand}")

        return " | ".join(filter(None, parts))

    def _create_item_metadata(self, item: PersonalClothingItem) -> dict[str, Any]:
        """Create comprehensive metadata for filtering."""
        return {
            "name": item.name,
            "category": item.category,
            "subcategory": item.subcategory,
            "material": item.material,
            "color": item.color,
            "secondary_colors": json.dumps(item.secondary_colors),
            "warmth_level": item.warmth_level,
            "formality": item.formality,
            "weather_suitability": json.dumps(item.weather_suitability),
            "season": json.dumps(item.season),
            "brand": item.brand or "",
            "size": item.size or "",
            "tags": json.dumps(item.tags),
        }

    def _result_to_clothing_item(self, result: dict, index: int, is_search: bool = False) -> PersonalClothingItem | None:
        """Convert ChromaDB result to PersonalClothingItem."""
        try:
            if is_search:
                metadata = result["metadatas"][0][index]
                item_id = result["ids"][0][index]
                document = result["documents"][0][index]
            else:
                metadata = result["metadatas"][index]
                item_id = result["ids"][index]
                document = result["documents"][index]

            return PersonalClothingItem(
                id=item_id,
                name=metadata["name"],
                category=metadata["category"],
                subcategory=metadata["subcategory"],
                material=metadata["material"],
                color=metadata["color"],
                secondary_colors=json.loads(metadata.get("secondary_colors", "[]")),
                warmth_level=metadata["warmth_level"],
                formality=metadata["formality"],
                weather_suitability=json.loads(metadata["weather_suitability"]),
                season=json.loads(metadata["season"]),
                brand=metadata.get("brand") or None,
                size=metadata.get("size") or None,
                description=document,
                tags=json.loads(metadata.get("tags", "[]")),
            )
        except Exception:
            return None
