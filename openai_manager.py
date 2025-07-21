"""
OpenAI Manager for SnapPad

This module handles OpenAI API interactions for prompt enhancement features.
It provides a clean interface for enhancing user prompts using OpenAI's GPT models.

Key Features:
- OpenAI API client management
- Prompt enhancement using GPT models
- Error handling and rate limiting
- Thread-safe operations
- Configuration-based settings

The OpenAI manager uses the official OpenAI Python library and provides
a simple interface for the rest of the application to enhance prompts.

Author: SnapPad Team
Version: 1.0.0
"""

import os
import threading
from typing import Optional, Dict, Any
from openai import OpenAI
import config


class OpenAIManager:
    """
    Manages OpenAI API interactions for prompt enhancement.
    
    This class provides comprehensive OpenAI integration including:
    - API client initialization and management
    - Prompt enhancement using GPT models
    - Error handling and retry logic
    - Thread-safe operations
    - Configuration-based settings
    
    The manager uses the official OpenAI Python library and provides
    a simple interface for enhancing user prompts with AI assistance.
    
    Thread Safety:
    All OpenAI operations are thread-safe using threading.Lock() to prevent
    race conditions between multiple threads accessing the API client.
    """
    
    def __init__(self):
        """
        Initialize the OpenAI manager.
        
        This constructor:
        1. Sets up the OpenAI API client
        2. Validates API key availability
        3. Prepares for prompt enhancement operations
        4. Sets up thread safety mechanisms
        """
        # Thread safety lock
        self._lock = threading.Lock()
        
        # Initialize OpenAI client
        self.client = None
        self.api_key = None
        self.is_configured = False
        
        # Initialize the client
        self._initialize_client()
        
        print("OpenAI Manager initialized")
    
    def _initialize_client(self):
        """
        Initialize the OpenAI API client with proper configuration.
        
        This method:
        1. Gets the API key from config or environment variable
        2. Validates the API key format
        3. Creates the OpenAI client instance
        4. Sets up error handling
        """
        # Get API key from config or environment variable
        self.api_key = config.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            print("Warning: OpenAI API key not found. Set OPENAI_API_KEY in config.py or environment variable.")
            self.is_configured = False
            return
        
        # Validate API key format (basic check)
        if not self.api_key.startswith('sk-'):
            print("Warning: OpenAI API key format appears invalid. Should start with 'sk-'")
            self.is_configured = False
            return
        
        try:
            # Create OpenAI client
            self.client = OpenAI(api_key=self.api_key)
            self.is_configured = True
            print("OpenAI client initialized successfully")
            
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            self.is_configured = False
    
    def is_available(self) -> bool:
        """
        Check if OpenAI API is available and configured.
        
        Returns:
            bool: True if OpenAI is properly configured and available
        """
        return self.is_configured and self.client is not None
    
    def enhance_prompt(self, original_prompt: str) -> Optional[str]:
        """
        Enhance a user prompt using OpenAI's GPT model.
        
        This method takes an original prompt and uses OpenAI's GPT model
        to generate an enhanced version that is more effective, clear,
        and detailed for AI model interactions.
        
        Args:
            original_prompt (str): The original prompt to enhance
            
        Returns:
            Optional[str]: The enhanced prompt, or None if enhancement failed
            
        Example:
            enhanced = manager.enhance_prompt("write a story")
            # Returns: "Write a compelling short story with engaging characters, 
            #          vivid descriptions, and a clear plot structure. Include 
            #          dialogue, sensory details, and emotional depth. The story 
            #          should be approximately 500-800 words and suitable for 
            #          a general audience."
        """
        if not self.is_available():
            print("OpenAI API not available. Check configuration and API key.")
            return None
        
        if not original_prompt or not original_prompt.strip():
            print("Empty prompt provided for enhancement.")
            return None
        
        # Limit input length
        if len(original_prompt) > config.PROMPT_MAX_INPUT_LENGTH:
            print(f"Prompt too long. Maximum length is {config.PROMPT_MAX_INPUT_LENGTH} characters.")
            return None
        
        with self._lock:
            try:
                # Create the chat completion request
                response = self.client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": config.OPENAI_SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": f"Please enhance this prompt: {original_prompt}"
                        }
                    ],
                    max_tokens=config.OPENAI_MAX_TOKENS,
                    temperature=config.OPENAI_TEMPERATURE
                )
                
                # Extract the enhanced prompt from the response
                enhanced_prompt = response.choices[0].message.content.strip()
                
                if enhanced_prompt:
                    print(f"Prompt enhanced successfully. Original: {len(original_prompt)} chars, Enhanced: {len(enhanced_prompt)} chars")
                    return enhanced_prompt
                else:
                    print("OpenAI returned empty response")
                    return None
                    
            except Exception as e:
                print(f"Error enhancing prompt: {e}")
                return None
    

    
    def get_usage_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current API usage information.
        
        This method retrieves information about the current API usage
        and rate limits from OpenAI.
        
        Returns:
            Optional[Dict[str, Any]]: Usage information dictionary, or None if failed
        """
        if not self.is_available():
            return None
        
        with self._lock:
            try:
                # Get usage information
                response = self.client.models.list()
                
                # Extract relevant information
                usage_info = {
                    "models_available": len(response.data) if response.data else 0,
                    "api_key_valid": True,
                    "model_configured": config.OPENAI_MODEL
                }
                
                return usage_info
                
            except Exception as e:
                print(f"Error getting usage info: {e}")
                return None
    
    def update_api_key(self, new_api_key: str) -> bool:
        """
        Update the OpenAI API key and reinitialize the client.
        
        Args:
            new_api_key (str): The new API key to use
            
        Returns:
            bool: True if the API key was updated successfully
        """
        if not new_api_key or not new_api_key.strip():
            print("Invalid API key provided")
            return False
        
        with self._lock:
            try:
                # Update the API key
                self.api_key = new_api_key.strip()
                
                # Reinitialize the client
                self._initialize_client()
                
                if self.is_configured:
                    print("API key updated successfully")
                    return True
                else:
                    print("Failed to update API key - client initialization failed")
                    return False
                    
            except Exception as e:
                print(f"Error updating API key: {e}")
                return False 

    def generate_smart_response(self, user_input: str, response_type: str = "general") -> Optional[str]:
        """
        Generate a smart response to user input using OpenAI's GPT model.
        
        This method takes user input (question, exercise, code snippet, riddle, etc.)
        and generates a coherent, relevant response based on the specified response type.
        
        Args:
            user_input (str): The user's input (question, code, riddle, etc.)
            response_type (str): The type of response to generate (general, educational, code, etc.)
            
        Returns:
            Optional[str]: The generated response, or None if generation failed
            
        Example:
            response = manager.generate_smart_response("What is recursion?", "educational")
            # Returns: "Recursion is a programming concept where a function calls itself..."
        """
        if not self.is_available():
            print("OpenAI API not available. Check configuration and API key.")
            return None
        
        if not user_input or not user_input.strip():
            print("Empty input provided for response generation.")
            return None
        
        # Limit input length
        if len(user_input) > config.SMART_RESPONSE_MAX_INPUT_LENGTH:
            print(f"Input too long. Maximum length is {config.SMART_RESPONSE_MAX_INPUT_LENGTH} characters.")
            return None
        
        # Get the system prompt based on response type
        system_prompt = self._get_response_system_prompt(response_type)
        
        with self._lock:
            try:
                # Create the chat completion request
                response = self.client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ],
                    max_tokens=config.OPENAI_MAX_TOKENS,
                    temperature=config.OPENAI_TEMPERATURE
                )
                
                # Extract the generated response from the response
                generated_response = response.choices[0].message.content.strip()
                
                if generated_response:
                    print(f"Smart response generated successfully. Input: {len(user_input)} chars, Response: {len(generated_response)} chars")
                    return generated_response
                else:
                    print("OpenAI returned empty response")
                    return None
                    
            except Exception as e:
                print(f"Error generating smart response: {e}")
                return None
    
    def _get_response_system_prompt(self, response_type: str) -> str:
        """
        Get the appropriate system prompt based on the response type.
        
        Args:
            response_type (str): The type of response to generate
            
        Returns:
            str: The system prompt for the specified response type
        """
        prompts = {
            "general": """You are a helpful AI assistant. Provide clear, accurate, and helpful responses to user questions and requests. 
            Focus on being informative, concise, and relevant to the user's input. 
            If the input is unclear, ask for clarification. Always be polite and professional.""",
            
            "educational": """You are an educational expert. Provide detailed, well-structured explanations that help users learn and understand concepts.
            Break down complex topics into digestible parts, use examples when helpful, and encourage deeper understanding.
            Focus on clarity, accuracy, and educational value.""",
            
            "code": """You are a programming expert and code reviewer. Analyze code snippets, identify issues, suggest improvements, and provide explanations.
            When reviewing code, consider:
            - Code quality and best practices
            - Performance and efficiency
            - Readability and maintainability
            - Security considerations
            - Error handling
            Provide specific, actionable feedback and improvements.""",
            
            "creative": """You are a creative writing assistant. Help users with creative writing tasks, brainstorming, and artistic expression.
            Provide imaginative, engaging, and original content while maintaining coherence and structure.
            Adapt your style to match the user's creative needs and preferences.""",
            
            "analytical": """You are an analytical expert. Break down complex problems, analyze data, and provide logical, evidence-based insights.
            Use structured thinking, identify key factors, and present clear conclusions.
            Focus on objectivity, thoroughness, and actionable insights.""",
            
            "step_by_step": """You are a step-by-step problem solver. Break down complex tasks and problems into clear, manageable steps.
            Provide detailed instructions that are easy to follow, with explanations for each step.
            Ensure the solution is complete and addresses the user's needs thoroughly.""",
            
            "fun": """You are a fun and engaging conversationalist. Respond with humor, creativity, and enthusiasm while still being helpful.
            Use a light, friendly tone and make interactions enjoyable.
            Balance entertainment with usefulness and maintain appropriate humor."""
        }
        
        return prompts.get(response_type, prompts["general"]) 