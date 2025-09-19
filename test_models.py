#!/usr/bin/env python3
"""
Quick Model Testing Script

This script allows you to quickly test different OpenAI models 
without editing your .env file permanently.
"""

import os
import asyncio
from weather_outfit_ai.graph.graph import create_outfit_graph
from weather_outfit_ai.models.state import AgentState
from rich.console import Console

console = Console()

async def test_model(model_name: str, test_message: str = "What should I wear today in Paris?"):
    """Test a specific model with a simple request."""
    
    # Temporarily override the model
    original_model = os.environ.get("OPENAI_MODEL")
    os.environ["OPENAI_MODEL"] = model_name
    
    try:
        console.print(f"[bold cyan]Testing {model_name}...[/bold cyan]")
        
        # Create graph with new model
        app = create_outfit_graph()
        
        # Create initial state
        initial_state = AgentState(
            conversation_history=[],
            metadata={"user_message": test_message}
        )
        
        # Run the graph
        result = await app.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": f"test-{model_name}"}}
        )
        
        console.print(f"[green]✅ {model_name} responded successfully![/green]")
        console.print(f"Response preview: {result.response[:100]}...")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ {model_name} failed: {str(e)[:100]}...[/red]")
        return False
        
    finally:
        # Restore original model
        if original_model:
            os.environ["OPENAI_MODEL"] = original_model
        elif "OPENAI_MODEL" in os.environ:
            del os.environ["OPENAI_MODEL"]

async def main():
    """Test multiple models in sequence."""
    models_to_test = [
        "gpt-3.5-turbo",           # Best free tier option: 20 RPM
        "gpt-3.5-turbo-instruct",  # Cheapest overall
        "gpt-3.5-turbo-16k",       # Good for longer contexts
        "gpt-4o-mini"              # Current default but restrictive
    ]
    
    console.print("[bold]🧪 OpenAI Model Testing (Budget Focus)[/bold]")
    console.print("Testing models starting with most rate-limit friendly...\n")
    
    results = {}
    
    for model in models_to_test:
        try:
            success = await test_model(model)
            results[model] = success
            
            # Add delay between tests to avoid rate limits
            if model != models_to_test[-1]:  # Don't wait after last model
                console.print("⏳ Waiting 3 seconds to avoid rate limits...\n")
                await asyncio.sleep(3)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Testing interrupted by user[/yellow]")
            break
    
    # Show results summary
    console.print("\n[bold]Test Results Summary:[/bold]")
    for model, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        rate_info = ""
        if model == "gpt-3.5-turbo":
            rate_info = " (20 RPM free tier)"
        elif model == "gpt-4o-mini":
            rate_info = " (3 RPM free tier)"
        console.print(f"{model}{rate_info}: {status}")
    
    # Recommend best model
    successful_models = [model for model, success in results.items() if success]
    if successful_models:
        recommended = successful_models[0]  # First successful model
        console.print(f"\n[bold green]Recommended model: {recommended}[/bold green]")
        if recommended == "gpt-3.5-turbo":
            console.print("[green]This model has 20 requests/minute on free tier vs 3 for gpt-4o-mini![/green]")
        console.print(f"To use this model, add to your .env file:")
        console.print(f"OPENAI_MODEL={recommended}")
    else:
        console.print("\n[red]All models failed. Check your API key and rate limits.[/red]")

if __name__ == "__main__":
    asyncio.run(main())
