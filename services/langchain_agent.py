from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Dict, Any, List
from config import settings

class LangChainAgent:
    def __init__(self, csv_service, vision_service, llm_service):
        self.csv_service = csv_service
        self.vision_service = vision_service
        self.llm_service = llm_service
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7
        )
        
        # Define tools
        self.tools = [
            Tool(
                name="AnalyzeCSV",
                func=self._analyze_csv_tool,
                description="Analyze CSV data and extract statistics. Input should be a CSV file path."
            ),
            Tool(
                name="AnalyzeImage",
                func=self._analyze_image_tool,
                description="Analyze an image and extract visual insights. Input should be an image file path."
            ),
            Tool(
                name="GenerateInsight",
                func=self._generate_insight_tool,
                description="Generate business insights from provided data summary. Input should be a data summary text."
            )
        ]
        
        # Create prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a business analytics agent. Your job is to:
1. Analyze CSV files and images provided
2. Extract key metrics and insights
3. Identify trends and correlations
4. Provide actionable recommendations

Use the available tools to gather information, then synthesize it into a comprehensive report."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        self.agent = create_openai_functions_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    
    def _analyze_csv_tool(self, csv_path: str) -> str:
        """Tool wrapper for CSV analysis"""
        try:
            result = self.csv_service.analyze_csv(csv_path)
            summary = f"CSV Analysis:\n"
            summary += f"Rows: {result['row_count']}, Columns: {result['column_count']}\n"
            summary += f"Columns: {', '.join(result['columns'])}\n"
            if result['numeric_summary']:
                summary += "Key Statistics:\n"
                for col, stats in result['numeric_summary'].items():
                    summary += f"  {col}: mean={stats.get('mean', 'N/A')}, range=[{stats.get('min', 'N/A')}, {stats.get('max', 'N/A')}]\n"
            return summary
        except Exception as e:
            return f"Error analyzing CSV: {str(e)}"
    
    def _analyze_image_tool(self, image_path: str) -> str:
        """Tool wrapper for image analysis"""
        try:
            result = self.vision_service.analyze_image(image_path)
            return f"Image Analysis:\nCaption: {result['caption']}\nDescription: {result['description']}"
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
    
    def _generate_insight_tool(self, data_summary: str) -> str:
        """Tool wrapper for insight generation"""
        try:
            prompt = f"Based on this data, provide 3 key business insights:\n{data_summary}"
            return self.llm_service.generate_text_completion(prompt)
        except Exception as e:
            return f"Error generating insights: {str(e)}"
    
    def process_report_request(self, csv_paths: List[str], image_paths: List[str], description: str) -> Dict[str, Any]:
        """
        Main method to process report generation using agent
        """
        try:
            # Build input for agent
            input_text = f"""Generate a comprehensive business report based on:
            
Description: {description}
CSV Files: {len(csv_paths)} files at {', '.join(csv_paths)}
Image Files: {len(image_paths)} files at {', '.join(image_paths)}

Analyze all files and create a structured report with metrics, trends, and recommendations."""
            
            # Execute agent
            result = self.agent_executor.invoke({"input": input_text})
            
            return {
                "success": True,
                "output": result.get("output", ""),
                "steps": "Agent completed analysis"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }