#!/usr/bin/env python3
"""
CLI interface for the Weather Outfit AI system.
"""
import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from weather_outfit_ai.config import config
from weather_outfit_ai.graph.graph import create_outfit_graph
from weather_outfit_ai.models.state import AgentState

app = typer.Typer(help="Weather Outfit AI - Get personalized outfit recommendations")
console = Console()


def validate_config():
    """Validate that required configuration is present."""
    try:
        config.validate()
    except ValueError as e:
        console.print(f"[red]Configuration Error: {e}[/red]")
        console.print("[yellow]Please check your .env file or environment variables.[/yellow]")
        raise typer.Exit(1)


def initialize_wardrobe():
    """Initialize and populate the wardrobe with items from CSV."""
    try:
        # Add the project root to Python path for imports
        import sys
        from pathlib import Path
        
        project_root = Path(__file__).parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Import here to avoid circular imports
        from utils.populate_wardrobe import populate_wardrobe_from_csv
        
        # Find the CSV file
        csv_file_path = Path("data/sample_wardrobe.csv")
        if not csv_file_path.exists():
            # Try relative to project root
            csv_file_path = project_root / "data" / "sample_wardrobe.csv"
        
        if not csv_file_path.exists():
            console.print("[yellow]⚠️  Warning: sample_wardrobe.csv not found. Wardrobe may be empty.[/yellow]")
            return
        
        console.print("[blue]🔄 Initializing wardrobe...[/blue]")
        
        # Populate wardrobe (will skip if already populated)
        populate_wardrobe_from_csv(str(csv_file_path))
        
        # Get final stats
        from weather_outfit_ai.services.wardrobe_service import WardrobeService
        wardrobe_service = WardrobeService()
        stats = wardrobe_service.get_wardrobe_stats()
        
        console.print(f"[green]✅ Wardrobe ready with {stats.get('total_items', 0)} items![/green]")
        
        # Show category breakdown
        if stats.get('categories'):
            categories_text = ", ".join([f"{cat}: {count}" for cat, count in stats['categories'].items()])
            console.print(f"[dim]   Categories: {categories_text}[/dim]")
            
    except Exception as e:
        console.print(f"[yellow]⚠️  Warning: Failed to initialize wardrobe: {e}[/yellow]")
        console.print("[dim]   The system will still work but may have limited clothing options.[/dim]")


async def run_graph_interaction(user_message: str, conversation_history: Optional[list] = None) -> dict:
    """Run the graph with user input and return the result."""
    # Create the graph
    graph = create_outfit_graph()
    
    # Initialize the agent state
    initial_state = AgentState(
        conversation_history=conversation_history or [],
        metadata={"user_message": user_message}
    )
    
    # Run the graph
    config_dict = {"configurable": {"thread_id": "cli-session"}}
    
    try:
        result = await graph.ainvoke(initial_state, config=config_dict)
        
        # Handle both dict and AgentState object returns
        if isinstance(result, dict):
            return {
                "success": True,
                "response": result.get("response", "No response available"),
                "location": result.get("location"),
                "weather_data": result.get("weather_data"),
                "final_recommendation": result.get("final_recommendation"),
                "errors": result.get("errors", []),
                "conversation_history": result.get("conversation_history", [])
            }
        else:
            # Handle AgentState object
            return {
                "success": True,
                "response": getattr(result, 'response', 'No response available'),
                "location": getattr(result, 'location', None),
                "weather_data": getattr(result, 'weather_data', None),
                "final_recommendation": getattr(result, 'final_recommendation', None),
                "errors": getattr(result, 'errors', []),
                "conversation_history": getattr(result, 'conversation_history', [])
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": "Sorry, I encountered an error processing your request."
        }


def display_result(result: dict):
    """Display the result in a formatted way."""
    if not result["success"]:
        console.print(Panel(
            f"[red]Error: {result['error']}[/red]",
            title="Error",
            border_style="red"
        ))
        return
    
    # Display the main response
    console.print(Panel(
        result["response"],
        title="🤖 Outfit Recommendation",
        border_style="blue"
    ))
    
    # Display additional details if available
    if result.get("weather_data") and result["weather_data"]:
        weather = result["weather_data"]
        weather_table = Table(title="Weather Information")
        weather_table.add_column("Property", style="cyan")
        weather_table.add_column("Value", style="white")
        
        weather_table.add_row("Location", getattr(weather, 'location', 'N/A') or "N/A")
        weather_table.add_row("Temperature", f"{getattr(weather, 'temperature', 'N/A')}°C" if getattr(weather, 'temperature', None) else "N/A")
        weather_table.add_row("Feels Like", f"{getattr(weather, 'feels_like', 'N/A')}°C" if getattr(weather, 'feels_like', None) else "N/A")
        weather_table.add_row("Description", getattr(weather, 'description', 'N/A') or "N/A")
        weather_table.add_row("Humidity", f"{getattr(weather, 'humidity', 'N/A')}%" if getattr(weather, 'humidity', None) else "N/A")
        weather_table.add_row("Wind Speed", f"{getattr(weather, 'wind_speed', 'N/A')} km/h" if getattr(weather, 'wind_speed', None) else "N/A")
        
        console.print(weather_table)
    
    # Display outfit details if available
    if result.get("final_recommendation") and result["final_recommendation"]:
        outfit = result["final_recommendation"]
        outfit_table = Table(title="Outfit Details")
        outfit_table.add_column("Category", style="magenta")
        outfit_table.add_column("Item", style="white")
        
        if getattr(outfit, 'selected_top', None):
            top = outfit.selected_top
            outfit_table.add_row("Top", f"{getattr(top, 'name', 'Unknown')} ({getattr(top, 'color', 'Unknown')})")
        if getattr(outfit, 'selected_bottom', None):
            bottom = outfit.selected_bottom
            outfit_table.add_row("Bottom", f"{getattr(bottom, 'name', 'Unknown')} ({getattr(bottom, 'color', 'Unknown')})")
        if getattr(outfit, 'selected_footwear', None):
            footwear = outfit.selected_footwear
            outfit_table.add_row("Footwear", f"{getattr(footwear, 'name', 'Unknown')} ({getattr(footwear, 'color', 'Unknown')})")
        if getattr(outfit, 'selected_outerwear', None):
            outerwear = outfit.selected_outerwear
            outfit_table.add_row("Outerwear", f"{getattr(outerwear, 'name', 'Unknown')} ({getattr(outerwear, 'color', 'Unknown')})")
        if getattr(outfit, 'selected_accessories', None):
            accessories = ", ".join([f"{getattr(acc, 'name', 'Unknown')} ({getattr(acc, 'color', 'Unknown')})" for acc in outfit.selected_accessories])
            outfit_table.add_row("Accessories", accessories)
        
        console.print(outfit_table)


@app.command()
def chat():
    """Start an interactive chat session."""
    validate_config()
    initialize_wardrobe()
    
    console.print(Panel(
        "[bold blue]Welcome to Weather Outfit AI![/bold blue]\n\n"
        "I can help you with outfit recommendations based on weather and occasion.\n"
        "Type your request (e.g., 'What should I wear in New York today for a business meeting?')\n"
        "Type 'quit' or 'exit' to end the session.",
        title="🌤️ Weather Outfit AI",
        border_style="blue"
    ))
    
    conversation_history = []
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]")
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                console.print("[yellow]Thanks for using Weather Outfit AI! Stay stylish! 👕[/yellow]")
                break
            
            if not user_input.strip():
                console.print("[yellow]Please enter a valid message.[/yellow]")
                continue
            
            # Show thinking indicator
            with console.status("[bold blue]Thinking..."):
                result = asyncio.run(run_graph_interaction(user_input, conversation_history))
            
            # Update conversation history
            conversation_history.append(f"User: {user_input}")
            if result["success"] and result["response"]:
                conversation_history.append(f"Bot: {result['response']}")
            
            # Display result
            display_result(result)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Session interrupted. Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")


@app.command()
def recommend(
    message: str = typer.Argument(..., help="Your outfit request message"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Location for weather data"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Additional context (e.g., 'business meeting')")
):
    """Get a single outfit recommendation."""
    validate_config()
    initialize_wardrobe()
    
    # Enhance message with optional parameters
    if location:
        message = f"{message} in {location}"
    if context:
        message = f"{message} for {context}"
    
    console.print(f"[blue]Processing request: {message}[/blue]")
    
    with console.status("[bold blue]Getting your outfit recommendation..."):
        result = asyncio.run(run_graph_interaction(message))
    
    display_result(result)


@app.command()
def config_info():
    """Show current configuration information."""
    settings = config.get_all_settings()
    
    config_table = Table(title="Configuration Settings")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="white")
    
    for key, value in settings.items():
        config_table.add_row(key, str(value))
    
    console.print(config_table)


if __name__ == "__main__":
    app()
