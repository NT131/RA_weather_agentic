#!/usr/bin/env python3
"""
Simple CLI script for Docker usage.
"""
import asyncio
import os
import sys

# Add the project root to Python path
sys.path.insert(0, '/app')

from weather_outfit_ai.config import config
from weather_outfit_ai.graph.graph import create_outfit_graph
from weather_outfit_ai.models.state import AgentState


async def run_outfit_recommendation(message: str):
    """Run a single outfit recommendation."""
    try:
        # Validate config
        config.validate()
        
        # Create graph
        graph = create_outfit_graph()
        
        # Initialize state
        initial_state = AgentState(
            conversation_history=[],
            metadata={"user_message": message}
        )
        
        # Run graph
        config_dict = {"configurable": {"thread_id": "docker-cli"}}
        result = await graph.ainvoke(initial_state, config=config_dict)
        
        # Print results
        print("\n" + "="*60)
        print("🌤️  WEATHER OUTFIT AI RECOMMENDATION")
        print("="*60)
        
        if result.response:
            print(f"\n📝 Response:\n{result.response}")
        
        if result.weather_data:
            weather = result.weather_data
            print(f"\n🌡️  Weather in {weather.location}:")
            print(f"   Temperature: {weather.temperature}°C (feels like {weather.feels_like}°C)")
            print(f"   Conditions: {weather.description}")
            print(f"   Humidity: {weather.humidity}%")
            print(f"   Wind: {weather.wind_speed} km/h")
        
        if result.final_recommendation and result.final_recommendation.selected_top:
            outfit = result.final_recommendation
            print(f"\n👕 Recommended Outfit:")
            if outfit.selected_top:
                print(f"   Top: {outfit.selected_top.name} ({outfit.selected_top.color})")
            if outfit.selected_bottom:
                print(f"   Bottom: {outfit.selected_bottom.name} ({outfit.selected_bottom.color})")
            if outfit.selected_footwear:
                print(f"   Footwear: {outfit.selected_footwear.name} ({outfit.selected_footwear.color})")
            if outfit.selected_outerwear:
                print(f"   Outerwear: {outfit.selected_outerwear.name} ({outfit.selected_outerwear.color})")
            if outfit.selected_accessories:
                accessories = ", ".join([f"{acc.name} ({acc.color})" for acc in outfit.selected_accessories])
                print(f"   Accessories: {accessories}")
        
        if result.errors:
            print(f"\n⚠️  Errors: {', '.join(result.errors)}")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python docker_cli.py \"Your outfit request message\"")
        print("Example: python docker_cli.py \"What should I wear in New York today for a business meeting?\"")
        sys.exit(1)
    
    message = " ".join(sys.argv[1:])
    asyncio.run(run_outfit_recommendation(message))


if __name__ == "__main__":
    main()
