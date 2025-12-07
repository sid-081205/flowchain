import os
from spoon_ai.tools.base import BaseTool

class TradeRecommendationTool(BaseTool):
    name: str = "get_trade_recommendations"
    description: str = (
        "Retrieves the latest strategic trade recommendations from the prediction model. "
        "Use this tool when the user asks about: trade signals, predictions, what to buy/sell, "
        "market recommendations, ETH signals, BTC signals, or trading advice. "
        "Returns sentiment-based BUY/SELL signals with macro context analysis."
    )
    
    parameters: dict = {
        "type": "object",
        "properties": {},
        "required": []
    }

    async def execute(self):
        """
        Reads the final_trade_plan.txt file and returns its content.
        """
        # Assuming the file is at prediction_model/final_trade_plan.txt relative to project root
        # We need to find the project root from this file's location: src/tools/recommendation_tool.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
        plan_path = os.path.join(project_root, "prediction_model", "final_trade_plan.txt")
        
        try:
            if not os.path.exists(plan_path):
                return f"Error: Trade plan file not found at {plan_path}"
                
            with open(plan_path, "r") as f:
                content = f.read()
            
            # Add a helpful header for the agent
            return f"📈 **Current Trade Predictions:**\n\n{content}\n\n💡 *Interpret these signals considering current market conditions and your risk tolerance.*"
        except Exception as e:
            return f"Error reading trade plan: {str(e)}"
