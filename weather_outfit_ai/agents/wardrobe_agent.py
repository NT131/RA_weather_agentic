import json

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

from weather_outfit_ai.models.schemas import PersonalClothingItem, WardrobeSelection
from weather_outfit_ai.models.state import AgentState
from weather_outfit_ai.prompts import Prompts
from weather_outfit_ai.services.wardrobe_service import WardrobeService


class WardrobeAgent:

    def __init__(self, llm: ChatOpenAI, wardrobe_service: WardrobeService):
        """
        Initialize the agentic wardrobe agent.

        Args:
            llm: OpenAI language model instance
            wardrobe_service: Service for accessing personal wardrobe
        """
        self.llm = llm
        self.wardrobe_service = wardrobe_service

        # Create optimized tools for the agent
        self.tools = self._create_tools()

        # Create smart query agent
        self.agent_executor = self._create_smart_query_agent()

    def _create_tools(self) -> list[Tool]:

        def smart_category_search_tool(query_and_category: str) -> str:
            """
            Search for items in a specific category using intelligent query.
            Format: 'query|category' where category is: top, bottom, footwear, outerwear, accessory
            """
            try:
                if "|" not in query_and_category:
                    return "Error: Please use format 'query|category'"

                query, category = query_and_category.split("|", 1)
                query = query.strip()
                category = category.strip().lower()

                items = self.wardrobe_service.semantic_search(query, limit=8)

                category_variants = (
                    [category, category + "s"]
                    if not category.endswith("s")
                    else [category, category[:-1]]
                )
                filtered_items = [
                    item
                    for item in items
                    if item.category.lower() in [c.lower() for c in category_variants]
                ][:5]

                return self._format_items_for_agent(
                    filtered_items, f"{category.title()} items for '{query}'"
                )

            except Exception as e:
                return f"Error in search: {e!s}"

        def get_wardrobe_stats_tool() -> str:
            """Get wardrobe statistics."""
            stats = self.wardrobe_service.get_wardrobe_stats()
            return json.dumps(stats, indent=2)

        return [
            Tool(
                name="smart_category_search",
                description="Search for clothing items in a specific category using intelligent queries. Use format 'your_intelligent_query|category'. Categories: top, bottom, footwear, outerwear, accessory. Construct queries based on weather, context, and formality needs.",
                func=smart_category_search_tool,
            ),
            Tool(
                name="get_wardrobe_stats",
                description="Get wardrobe statistics - use when user asks about inventory",
                func=get_wardrobe_stats_tool,
            ),
        ]

    def _create_smart_query_agent(self) -> AgentExecutor:

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", Prompts.wardrobe_agent()),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent, tools=self.tools, verbose=False, max_iterations=8
        )


    async def run(self, state: AgentState) -> AgentState:
        
        if not state.weather_data:
            return state

        weather = state.weather_data
        context = state.followup_context or "general outfit recommendation"

        agent_input = Prompts.wardrobe_agent_input(weather, context)

        result = await self.agent_executor.ainvoke({"input": agent_input})

        wardrobe_selection = await self._parse_agent_results(result["output"])
        state.wardrobe_selection = wardrobe_selection

        state.metadata.update(
            {
                "wardrobe_agent_reasoning": result["output"],
            }
        )
        return state


    async def _parse_agent_results(self, agent_output: str) -> WardrobeSelection:
        """
        Parse the agent's output and extract the found items into a structured selection.

        Args:
            agent_output: The agent's response with reasoning and tool results

        Returns:
            WardrobeSelection with categorized items
        """
        return WardrobeSelection(
            available_tops=self.wardrobe_service.filter_by_category("tops", limit=4),
            available_bottoms=self.wardrobe_service.filter_by_category("bottoms", limit=4),
            available_footwear=self.wardrobe_service.filter_by_category("footwear", limit=3),
            available_outerwear=self.wardrobe_service.filter_by_category("outerwear", limit=2),
            available_accessories=self.wardrobe_service.filter_by_category("accessories", limit=3),
            selection_reasoning=agent_output,
        )
        

    def _format_items_for_agent(
        self, items: list[PersonalClothingItem], title: str
    ) -> str:
        """Format items for the agent to understand"""
        if not items:
            return f"{title}: No items found"

        formatted_items = []
        for item in items:
            item_info = (
                f"• {item.name} ({item.subcategory}) - {item.material} in {item.color}"
            )

            if item.secondary_colors:
                item_info += f" with {', '.join(item.secondary_colors)}"

            item_info += (
                f" [Warmth: {item.warmth_level}/5, Formality: {item.formality}/5]"
            )

            formatted_items.append(item_info)

        return f"{title}:\n" + "\n".join(formatted_items)
