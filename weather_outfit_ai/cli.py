#!/usr/bin/env python3
"""
CLI interface for the Weather Outfit AI system.
"""
import asyncio
import sys
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
        return {
            "success": True,
            "response": result.response,
            "location": result.location,
            "weather_data": result.weather_data,
            "final_recommendation": result.final_recommendation,
            "errors": result.errors,
            "conversation_history": result.conversation_history
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
    if result.get("weather_data"):
        weather = result["weather_data"]
        weather_table = Table(title="Weather Information")
        weather_table.add_column("Property", style="cyan")
        weather_table.add_column("Value", style="white")
        
        weather_table.add_row("Location", weather.location or "N/A")
        weather_table.add_row("Temperature", f"{weather.temperature}°C" if weather.temperature else "N/A")
        weather_table.add_row("Feels Like", f"{weather.feels_like}°C" if weather.feels_like else "N/A")
        weather_table.add_row("Description", weather.description or "N/A")
        weather_table.add_row("Humidity", f"{weather.humidity}%" if weather.humidity else "N/A")
        weather_table.add_row("Wind Speed", f"{weather.wind_speed} km/h" if weather.wind_speed else "N/A")
        
        console.print(weather_table)
    
    # Display outfit details if available
    if result.get("final_recommendation"):
        outfit = result["final_recommendation"]
        outfit_table = Table(title="Outfit Details")
        outfit_table.add_column("Category", style="magenta")
        outfit_table.add_column("Item", style="white")
        
        if outfit.selected_top:
            outfit_table.add_row("Top", f"{outfit.selected_top.name} ({outfit.selected_top.color})")
        if outfit.selected_bottom:
            outfit_table.add_row("Bottom", f"{outfit.selected_bottom.name} ({outfit.selected_bottom.color})")
        if outfit.selected_footwear:
            outfit_table.add_row("Footwear", f"{outfit.selected_footwear.name} ({outfit.selected_footwear.color})")
        if outfit.selected_outerwear:
            outfit_table.add_row("Outerwear", f"{outfit.selected_outerwear.name} ({outfit.selected_outerwear.color})")
        if outfit.selected_accessories:
            accessories = ", ".join([f"{acc.name} ({acc.color})" for acc in outfit.selected_accessories])
            outfit_table.add_row("Accessories", accessories)
        
        console.print(outfit_table)


@app.command()
def chat():
    """Start an interactive chat session."""
    validate_config()
    
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
