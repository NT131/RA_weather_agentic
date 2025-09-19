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
sys.path.insert(0, str(Path(__file__).parent.parent))

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


def count_csv_items(csv_file_path: str) -> int:
    """Count the number of items in the CSV file."""
    try:
        with open(csv_file_path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            return sum(1 for _ in reader)
    except Exception:
        return 0


def get_existing_item_names(wardrobe_service: WardrobeService) -> set:
    """Get the names of all existing items in the wardrobe."""
    try:
        all_items = wardrobe_service.list_all_items()
        return {item.name for item in all_items}
    except Exception:
        return set()


def get_csv_item_names(csv_file_path: str) -> set:
    """Get the names of all items in the CSV file."""
    try:
        csv_names = set()
        with open(csv_file_path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get("name"):
                    csv_names.add(row["name"].strip())
        return csv_names
    except Exception:
        return set()


def remove_items_not_in_csv(wardrobe_service: WardrobeService, csv_names: set, existing_names: set) -> int:
    """Remove items from wardrobe that are no longer in the CSV."""
    items_to_remove = existing_names - csv_names
    items_removed = 0
    
    if not items_to_remove:
        return 0
    
    print(f"🗑️  Found {len(items_to_remove)} items in wardrobe that are no longer in CSV:")
    for item_name in sorted(items_to_remove):
        print(f"   - {item_name}")
    
    try:
        # Get all items to find IDs for removal
        all_items = wardrobe_service.list_all_items()
        item_id_map = {item.name: item.id for item in all_items}
        
        for item_name in items_to_remove:
            if item_name in item_id_map:
                try:
                    if wardrobe_service.remove_clothing_item(item_id_map[item_name]):
                        print(f"✅ Removed: {item_name}")
                        items_removed += 1
                    else:
                        print(f"❌ Failed to remove: {item_name}")
                except Exception as e:
                    print(f"❌ Error removing {item_name}: {e}")
    
    except Exception as e:
        print(f"❌ Error during removal process: {e}")
    
    return items_removed


def populate_wardrobe_from_csv(csv_file_path: str, force_reload: bool = False, sync_mode: bool = False):
    """Populate the wardrobe with data from a CSV file.
    
    Args:
        csv_file_path: Path to the CSV file
        force_reload: If True, clear wardrobe and reload all items
        sync_mode: If True, synchronize wardrobe with CSV (add new, remove deleted)
    """

    # Wait for ChromaDB to be available (important for Docker startup)
    wardrobe_service = wait_for_chromadb()

    if not os.path.exists(csv_file_path):
        print(f"❌ CSV file not found: {csv_file_path}")
        return

    # Count items in CSV
    csv_item_count = count_csv_items(csv_file_path)
    if csv_item_count == 0:
        print(f"⚠️ No items found in CSV file: {csv_file_path}")
        return

    # Get CSV item names for comparison
    csv_names = get_csv_item_names(csv_file_path)

    # Check current wardrobe state
    try:
        stats = wardrobe_service.get_wardrobe_stats()
        current_item_count = stats.get("total_items", 0)
        
        if force_reload and current_item_count > 0:
            print(f"🗑️  Force reload: Clearing existing {current_item_count} items...")
            if wardrobe_service.clear_wardrobe():
                print("✅ Wardrobe cleared successfully")
                existing_names = set()
            else:
                print("❌ Failed to clear wardrobe")
                return
        elif current_item_count > 0:
            # Get existing item names for comparison
            existing_names = get_existing_item_names(wardrobe_service)
            
            if current_item_count == csv_item_count and existing_names == csv_names:
                print(f"📦 Wardrobe already contains {current_item_count} items (same as CSV). Skipping population.")
                return
            elif current_item_count < csv_item_count:
                print(f"📦 Wardrobe has {current_item_count} items, CSV has {csv_item_count}. Adding new items...")
            elif current_item_count > csv_item_count or existing_names != csv_names:
                if sync_mode:
                    print(f"🔄 Sync mode: Wardrobe has {current_item_count} items, CSV has {csv_item_count}.")
                    # Remove items not in CSV
                    items_removed = remove_items_not_in_csv(wardrobe_service, csv_names, existing_names)
                    if items_removed > 0:
                        print(f"�️  Removed {items_removed} items no longer in CSV")
                        # Update existing names after removal
                        existing_names = get_existing_item_names(wardrobe_service)
                else:
                    print(f"📦 Wardrobe has {current_item_count} items, CSV has {csv_item_count}.")
                    missing_in_csv = existing_names - csv_names
                    if missing_in_csv:
                        print(f"⚠️  Warning: {len(missing_in_csv)} items in wardrobe are not in CSV:")
                        for item_name in sorted(missing_in_csv):
                            print(f"   - {item_name}")
                        print("💡 Use --sync flag to automatically remove items not in CSV")
        else:
            existing_names = set()
        
    except Exception as e:
        print(f"⚠️ Could not check wardrobe stats: {e}")
        existing_names = set()

    print(f"📂 Reading wardrobe data from: {csv_file_path}")

    items_added = 0
    items_skipped = 0
    items_failed = 0

    try:
        with open(csv_file_path, encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            print("🔄 Processing clothing items...")

            for row_num, row in enumerate(
                reader, start=2
            ):  # Start at 2 since row 1 is header
                try:
                    item_name = row["name"].strip()
                    
                    # Skip if item already exists (unless force reload)
                    if not force_reload and item_name in existing_names:
                        items_skipped += 1
                        continue

                    # Parse the CSV row into a PersonalClothingItem
                    clothing_item = PersonalClothingItem(
                        name=item_name,
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

    print("\n🎉 Wardrobe population complete!")
    print(f"✅ Successfully added: {items_added} items")
    if items_skipped > 0:
        print(f"⏭️  Skipped existing: {items_skipped} items")
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
    import argparse

    parser = argparse.ArgumentParser(description="Populate wardrobe from CSV file")
    parser.add_argument("--force", "-f", action="store_true", 
                       help="Force reload all items, even if they already exist")
    parser.add_argument("--sync", "-s", action="store_true",
                       help="Sync wardrobe with CSV (add new items, remove items not in CSV)")
    parser.add_argument("--csv", type=str, 
                       help="Path to CSV file (default: data/sample_wardrobe.csv)")
    
    args = parser.parse_args()

    # Determine CSV file path
    csv_file_path = args.csv or os.getenv("WARDROBE_CSV_PATH", "data/sample_wardrobe.csv")

    # If running in Docker, the CSV should be in the data directory
    if not os.path.exists(csv_file_path):
        script_dir = Path(__file__).parent.parent  # Go up from utils/ to project root
        csv_file_path = script_dir / "data" / "sample_wardrobe.csv"

    print("🌤️ Weather Outfit AI - Wardrobe Population")
    print("=" * 50)
    
    if args.force:
        print("🔄 Force reload enabled - will reload all items")
    elif args.sync:
        print("🔄 Sync mode enabled - will add new items and remove items not in CSV")

    try:
        populate_wardrobe_from_csv(str(csv_file_path), force_reload=args.force, sync_mode=args.sync)
    except KeyboardInterrupt:
        print("\n🛑 Population interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Population failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
