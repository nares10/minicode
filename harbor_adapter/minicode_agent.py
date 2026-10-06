"""
Harbor adapter for minicode agent.
This allows minicode to be evaluated using the Harbor framework.
"""

from pathlib import Path
import os
import logging

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext


class MinicodeAgent(BaseAgent):
    """Harbor adapter for the minicode terminal coding agent."""
    
    SUPPORTS_ATIF = False  # Set to True if minicode supports ATIF trajectory format
    
    @staticmethod
    def name() -> str:
        return "minicode"
    
    def version(self) -> str | None:
        return "1.0.0"
    
    async def setup(self, environment: BaseEnvironment) -> None:
        """
        Install and configure minicode in the environment.
        
        This method:
        1. Installs minicode and its dependencies
        2. Sets up the .env file with the GEMINI_API_KEY
        3. Configures the model to use
        """
        self.logger.info("Setting up minicode agent...")
        
        # Install minicode from local path or remote
        # Adjust the path to where minicode is located
        minicode_path = os.getenv("MINICODE_PATH", "/minicode")
        
        self.logger.info(f"Installing minicode from {minicode_path}")
        await environment.exec(f"pip install -e {minicode_path}")
        
        # Install dependencies
        self.logger.info("Installing dependencies...")
        await environment.exec("pip install python-dotenv google-genai")
        
        # Set up .env file with API key and model configuration
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable must be set")
        
        model = os.getenv("MODEL", "gemini-3.1-flash-lite")
        
        self.logger.info("Configuring .env file...")
        await environment.exec(f"echo 'GEMINI_API_KEY={gemini_api_key}' > .env")
        await environment.exec(f"echo 'MODEL={model}' >> .env")
        
        self.logger.info("Minicode setup complete")
    
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """
        Run minicode on the given task instruction.
        
        Args:
            instruction: The task instruction to complete
            environment: The Harbor environment to execute in
            context: The agent context to populate with results
        """
        self.logger.info(f"Running minicode with instruction: {instruction[:100]}...")
        
        # Execute minicode with the instruction
        # Using --yolo flag to skip approval prompts in automated evaluation
        result = await environment.exec(
            f"python -m minicode.cli --yolo -p '{instruction}'",
            timeout=600  # 10 minute timeout for complex tasks
        )
        
        # Populate context with execution results
        context.stdout = result.stdout
        context.stderr = result.stderr
        context.exit_code = result.exit_code
        
        # Add metadata for Harbor's evaluation
        context.metadata = {
            "agent": "minicode",
            "model": self.model_name or os.getenv("MODEL", "gemini-3.1-flash-lite"),
            "instruction": instruction,
        }
        
        self.logger.info(f"Minicode execution complete. Exit code: {result.exit_code}")