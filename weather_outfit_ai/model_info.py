#!/usr/bin/env python3
"""
OpenAI Model Information and Rate Limits

This module provides information about different OpenAI models to help users
choose the best model for their needs based on rate limits and capabilities.
"""

from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from weather_outfit_ai.config import config

console = Console()

# Model information with approximate rate limits (may vary by account type)
MODEL_INFO: Dict[str, Dict[str, Any]] = {
    "gpt-3.5-turbo-instruct": {
        "description": "Legacy completion model, very fast and cheap",
        "cost": "Lowest",
        "rpm_free": 20,      # Higher limits for older models
        "tpm_free": 150000,
        "rpm_paid": 20000,
        "tpm_paid": 4000000,
        "best_for": ["High-volume tasks", "Simple completions", "Rate limit testing"]
    },
    "gpt-3.5-turbo-16k": {
        "description": "Older GPT-3.5 with 16k context, very affordable",
        "cost": "Very Low",
        "rpm_free": 20,
        "tpm_free": 180000,
        "rpm_paid": 10000,
        "tpm_paid": 1000000,
        "best_for": ["Long conversations", "Document processing", "Budget projects"]
    },
    "gpt-3.5-turbo": {
        "description": "Current GPT-3.5, fast and capable",
        "cost": "Low",
        "rpm_free": 20,      # Much higher than gpt-4o-mini
        "tpm_free": 120000,
        "rpm_paid": 10000,
        "tpm_paid": 1000000,
        "best_for": ["General chat", "Simple reasoning", "Production use"]
    },
    "gpt-4o-mini": {
        "description": "Fast, efficient model for simple tasks",
        "cost": "Low-Medium",
        "rpm_free": 3,      # Very restrictive on free tier
        "tpm_free": 100000,
        "rpm_paid": 5000,
        "tpm_paid": 200000,
        "best_for": ["Development", "Testing", "Basic tasks"]
    },
    "gpt-4": {
        "description": "Original GPT-4, reliable and capable",
        "cost": "High",
        "rpm_free": 3,
        "tpm_free": 10000,
        "rpm_paid": 5000,
        "tpm_paid": 300000,
        "best_for": ["Complex reasoning", "High-quality outputs"]
    },
    "gpt-4o": {
        "description": "Latest GPT-4 model with enhanced capabilities",
        "cost": "Medium-High",
        "rpm_free": 3,
        "tpm_free": 30000,
        "rpm_paid": 5000,
        "tpm_paid": 800000,
        "best_for": ["Complex reasoning", "Creative tasks", "Production use"]
    },
    "gpt-4-turbo": {
        "description": "High-performance model for complex tasks",
        "cost": "High",
        "rpm_free": 3,
        "tpm_free": 30000,
        "rpm_paid": 5000,
        "tpm_paid": 800000,
        "best_for": ["Advanced reasoning", "Code generation", "Analysis"]
    }
}

def show_model_info():
    """Display a table with model information and rate limits."""
    table = Table(title="OpenAI Model Information & Rate Limits")
    
    table.add_column("Model", style="bold cyan")
    table.add_column("Description", style="white")
    table.add_column("Cost", style="green")
    table.add_column("Free RPM", style="yellow")
    table.add_column("Free TPM", style="yellow")
    table.add_column("Paid RPM", style="bright_green")
    table.add_column("Paid TPM", style="bright_green")
    table.add_column("Best For", style="blue")
    
    for model_name, info in MODEL_INFO.items():
        # Highlight current model
        model_style = "bold red" if model_name == config.OPENAI_MODEL else "cyan"
        current_marker = " ← CURRENT" if model_name == config.OPENAI_MODEL else ""
        
        table.add_row(
            f"{model_name}{current_marker}",
            info["description"],
            info["cost"],
            str(info["rpm_free"]),
            f"{info['tpm_free']:,}",
            f"{info['rpm_paid']:,}",
            f"{info['tpm_paid']:,}",
            ", ".join(info["best_for"]),
            style=model_style if model_name == config.OPENAI_MODEL else None
        )
    
    console.print(table)
    
    console.print("\n[bold]Rate Limit Notes:[/bold]")
    console.print("• RPM = Requests Per Minute")
    console.print("• TPM = Tokens Per Minute") 
    console.print("• Free tier limits apply to accounts without payment methods")
    console.print("• Paid tier limits apply to accounts with payment methods added")
    console.print("• Limits may vary based on your account history and usage")

def get_model_recommendations():
    """Get model recommendations based on use case."""
    console.print("\n[bold]Model Recommendations:[/bold]")
    
    recommendations = [
        ("💰 Absolute Cheapest", "gpt-3.5-turbo-instruct", "Lowest cost, highest free tier limits"),
        ("🚀 Best Free Tier Experience", "gpt-3.5-turbo", "20 RPM vs 3 RPM for newer models"),
        ("📚 Long Documents", "gpt-3.5-turbo-16k", "16k context window, very affordable"),
        ("🧪 Development & Testing", "gpt-3.5-turbo", "Much better rate limits than gpt-4o-mini"),
        ("💬 General Chat & Simple Tasks", "gpt-3.5-turbo", "Best balance of cost and capability"),
        ("🎯 Production Applications", "gpt-4o", "Most capable current model"),
        ("🧠 Complex Reasoning", "gpt-4-turbo", "Best for advanced cognitive tasks")
    ]
    
    for use_case, model, reason in recommendations:
        console.print(f"{use_case}: [bold cyan]{model}[/bold cyan] - {reason}")
    
    console.print("\n[bold yellow]💡 Pro Tip:[/bold yellow]")
    console.print("If you're hitting rate limits with gpt-4o-mini on the free tier,")
    console.print("switch to [bold cyan]gpt-3.5-turbo[/bold cyan] for 20 RPM instead of 3 RPM!")

def show_current_config():
    """Show current configuration."""
    console.print(f"\n[bold]Current Configuration:[/bold]")
    console.print(f"Model: [bold cyan]{config.OPENAI_MODEL}[/bold cyan]")
    console.print(f"Temperature: [bold yellow]{config.OPENAI_TEMPERATURE}[/bold yellow]")
    
    if config.OPENAI_MODEL in MODEL_INFO:
        info = MODEL_INFO[config.OPENAI_MODEL]
        console.print(f"Cost Level: [bold green]{info['cost']}[/bold green]")
        console.print(f"Best For: [bold blue]{', '.join(info['best_for'])}[/bold blue]")

def main():
    """Main function to display model information."""
    console.print("[bold]🤖 OpenAI Model Selection Guide[/bold]", style="bright_blue")
    
    show_current_config()
    show_model_info()
    get_model_recommendations()
    
    console.print(f"\n[bold]To change model:[/bold]")
    console.print("1. Edit your .env file")
    console.print("2. Set OPENAI_MODEL to your preferred model")
    console.print("3. Restart the application")
    console.print("\nExample: OPENAI_MODEL=gpt-3.5-turbo")

if __name__ == "__main__":
    main()
