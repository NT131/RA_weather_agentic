#!/usr/bin/env python3
"""
Populate ChromaDB wardrobe with sample data from CSV file.
This script is designed to run in Docker containers or locally.

AI Generated :D
"""

import csv
import os
import sys
import time
from pathlib import Path

# Add the weather_outfit_ai package to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from weather_outfit_ai.models.schemas import PersonalClothingItem
from weather_outfit_ai.services.wardrobe_service import WardrobeService


def parse_list_field(field_value: str) -> list:
    """Parse comma-separated string into list, handling empty values."""
    if not field_value or field_value.strip() == "":
        return []
    return [item.strip() for item in field_value.split(",")]


def wait_for_chromadb(max_retries: int = 30, delay: int = 2):
    """Wait for ChromaDB to be available."""
    print("🔍 Waiting for ChromaDB to be available...")

    for attempt in range(max_retries):
        try:
            # Try to initialize the wardrobe service
            wardrobe_service = WardrobeService()
            # Test if we can get stats (this will fail if ChromaDB is not ready)
            wardrobe_service.get_wardrobe_stats()
            print("✅ ChromaDB is ready!")
            return wardrobe_service
        except Exception as e:
            if attempt < max_retries - 1:
                print(
                    f"⏳ ChromaDB not ready yet (attempt {attempt + 1}/{max_retries}): {e}"
                )
                time.sleep(delay)
            else:
                print(
                    f"❌ Failed to connect to ChromaDB after {max_retries} attempts: {e}"
                )
                raise

    raise Exception("ChromaDB is not available")


def populate_wardrobe_from_csv(csv_file_path: str):
    """Populate the wardrobe with data from a CSV file."""

    # Wait for ChromaDB to be available (important for Docker startup)
    wardrobe_service = wait_for_chromadb()

    # Check if wardrobe already has data
    try:
        stats = wardrobe_service.get_wardrobe_stats()
        if stats.get("total_items", 0) > 0:
            print(
                f"📦 Wardrobe already contains {stats['total_items']} items. Skipping population."
            )
            return
    except Exception as e:
        print(f"⚠️ Could not check wardrobe stats: {e}")

    print(f"📂 Reading wardrobe data from: {csv_file_path}")

    if not os.path.exists(csv_file_path):
        print(f"❌ CSV file not found: {csv_file_path}")
        return

    items_added = 0
    items_failed = 0

    try:
        with open(csv_file_path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            print("🔄 Processing clothing items...")

            for row_num, row in enumerate(
                reader, start=2
            ):  # Start at 2 since row 1 is header
                try:
                    # Parse the CSV row into a PersonalClothingItem
                    clothing_item = PersonalClothingItem(
                        name=row["name"].strip(),
                        category=row["category"].strip(),
                        subcategory=(
                            row["subcategory"].strip() if row["subcategory"] else None
                        ),
                        color=row["color"].strip(),
                        secondary_colors=parse_list_field(row["secondary_colors"]),
                        material=row["material"].strip(),
                        brand=row["brand"].strip() if row["brand"] else None,
                        size=row["size"].strip() if row["size"] else None,
                        description=row["description"].strip(),
                        warmth_level=(
                            int(row["warmth_level"]) if row["warmth_level"] else 2
                        ),
                        formality=int(row["formality"]) if row["formality"] else 3,
                        weather_suitability=parse_list_field(
                            row["weather_suitability"]
                        ),
                        season=parse_list_field(row["season"]),
                        tags=parse_list_field(row["tags"]),
                    )

                    # Add the item to the wardrobe
                    item_id = wardrobe_service.add_clothing_item(clothing_item)
                    print(f"✅ Added: {clothing_item.name} (ID: {item_id})")
                    items_added += 1

                except Exception as e:
                    print(f"❌ Failed to add item from row {row_num}: {e}")
                    print(f"   Row data: {row}")
                    items_failed += 1
                    continue

    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return

    print("\n🎉 Wardrobe population complete!")
    print(f"✅ Successfully added: {items_added} items")
    if items_failed > 0:
        print(f"❌ Failed to add: {items_failed} items")

    # Print final stats
    try:
        final_stats = wardrobe_service.get_wardrobe_stats()
        print("\n📊 Final wardrobe stats:")
        print(f"   Total items: {final_stats.get('total_items', 0)}")

        # Print breakdown by category if available
        if "categories" in final_stats:
            for category, count in final_stats["categories"].items():
                print(f"   {category.title()}: {count}")

    except Exception as e:
        print(f"⚠️ Could not retrieve final stats: {e}")


def main():
    """Main function to populate wardrobe from CSV."""

    # Determine CSV file path
    csv_file_path = os.getenv("WARDROBE_CSV_PATH", "data/sample_wardrobe.csv")

    # If running in Docker, the CSV should be in the data directory
    if not os.path.exists(csv_file_path):
        script_dir = Path(__file__).parent.parent  # Go up from utils/ to project root
        csv_file_path = script_dir / "data" / "sample_wardrobe.csv"

    print("🌤️ Weather Outfit AI - Wardrobe Population")
    print("=" * 50)

    try:
        populate_wardrobe_from_csv(str(csv_file_path))
    except KeyboardInterrupt:
        print("\n🛑 Population interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Population failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
