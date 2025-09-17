
from langchain_openai import ChatOpenAI

from weather_outfit_ai.models.schemas import OutfitRecommendation, PersonalClothingItem
from weather_outfit_ai.models.state import AgentState
from weather_outfit_ai.prompts import Prompts


class DesignAgent:

    def __init__(self, llm: ChatOpenAI):
        """
        Initialize the design agent.

        Args:
            llm: OpenAI language model instance
        """
        self.llm = llm

    async def run(self, state: AgentState) -> AgentState:
        """Select the best outfit from available wardrobe items."""      
        if not state.weather_data:
            return state

        if not state.wardrobe_selection:
            return state

        weather = state.weather_data
        wardrobe_selection = state.wardrobe_selection
        context = state.followup_context or "general outfit"

        items_summary = self._build_items_summary(wardrobe_selection)
        prompt = Prompts.design_agent(weather, context, items_summary)

        response = await self.llm.ainvoke([{"role": "user", "content": prompt}])

        ai_response = response.content.strip()

        outfit_recommendation = self._parse_outfit_response(ai_response, wardrobe_selection)

        state.final_recommendation = outfit_recommendation

        return state


    def _build_items_summary(self, wardrobe) -> str:
        summary_parts = []

        categories = [
            ("TOPS", wardrobe.available_tops),
            ("BOTTOMS", wardrobe.available_bottoms),
            ("FOOTWEAR", wardrobe.available_footwear),
            ("OUTERWEAR", wardrobe.available_outerwear),
            ("ACCESSORIES", wardrobe.available_accessories),
        ]

        for category_name, items in categories:
            if items:
                items_list = []
                for item in items:
                    item_desc = f"{item.name} ({item.color} {item.material}, warmth:{item.warmth_level}/5, formality:{item.formality}/5)"
                    items_list.append(item_desc)

                summary_parts.append(
                    f"{category_name}:\n"
                    + "\n".join(f"- {item}" for item in items_list)
                )
            else:
                summary_parts.append(f"{category_name}:\n- None available")

        return "\n\n".join(summary_parts)

    def _parse_outfit_response(self, response: str, wardrobe) -> OutfitRecommendation:
        all_items = self._create_item_lookup(wardrobe)
        
        parts = response.strip().split("|")
        if len(parts) != 5:
            parts = ["None"] * 5 
            
        selected_top = self._find_item_by_name(parts[0], all_items)
        selected_bottom = self._find_item_by_name(parts[1], all_items)
        selected_footwear = self._find_item_by_name(parts[2], all_items)
        selected_outerwear = self._find_item_by_name(parts[3], all_items)
        
        selected_accessories = []
        if parts[4] and parts[4].lower() != "none":
            for acc_name in parts[4].split(","):
                acc_item = self._find_item_by_name(acc_name.strip(), all_items)
                if acc_item:
                    selected_accessories.append(acc_item)

        return OutfitRecommendation(
            selected_top=selected_top,
            selected_bottom=selected_bottom,
            selected_footwear=selected_footwear,
            selected_outerwear=selected_outerwear,
            selected_accessories=selected_accessories,
            outfit_description="Complete outfit selected from your wardrobe.",
            styling_advice="Wear with confidence!",
            weather_appropriateness="Suitable for current weather conditions.",
            formality_match="Appropriate for the occasion.",
        )


    def _create_item_lookup(self, wardrobe) -> dict:
        """Create lookup dictionary for quick item finding."""
        all_items = {}
        for items_list in [
            wardrobe.available_tops,
            wardrobe.available_bottoms,
            wardrobe.available_footwear,
            wardrobe.available_outerwear,
            wardrobe.available_accessories,
        ]:
            for item in items_list:
                all_items[item.name.lower()] = item
        return all_items



    def _find_item_by_name(
        self, name_text: str, all_items: dict
    ) -> PersonalClothingItem | None:
        if not name_text or name_text.lower() in ["none", "not needed", ""]:
            return None

        if name_text.lower() in all_items:
            return all_items[name_text.lower()]

        for item_name, item in all_items.items():
            if name_text.lower() in item_name or item_name in name_text.lower():
                return item

        return None
