import requests
import json
import tkinter.messagebox as messagebox

class ModelManager:
    def __init__(self):
        self.available_models = []
        self.default_model = "mistral:instruct"
        self.fallback_models = ["mistral:instruct", "gemma:2b", "llama2", "gemma3:3b"]
        self.refresh_available_models()
    
    def refresh_available_models(self):
        """Get the list of available models from Ollama"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                # Parse the response - handle different API versions
                data = response.json()
                if "models" in data:
                    # Newer API format
                    self.available_models = [model["name"] for model in data["models"]]
                elif isinstance(data, list):
                    # Older API format
                    self.available_models = [model["name"] for model in data]
                else:
                    # Unknown format
                    print("Unknown API response format")
                    self.available_models = []
                
                # If we found models, return success
                if self.available_models:
                    print(f"Available models: {', '.join(self.available_models)}")
                    return True
                return False
            return False
        except Exception as e:
            print(f"Error getting available models: {e}")
            self.available_models = []
            return False
    
    def get_model_list(self):
        """Get a list of models to display in the UI"""
        # Default models to always show in dropdown
        default_models = ["mistral:instruct", "llama2", "gemma:2b", "gemma:7b", "gemma3:3b"]
        
        # Add any additional available models
        model_list = default_models.copy()
        for model in self.available_models:
            if model not in model_list:
                model_list.append(model)
        
        return model_list
    
    def get_default_model(self):
        """Get the best default model based on availability"""
        if "mistral:instruct" in self.available_models:
            return "mistral:instruct"
        elif len(self.available_models) > 0:
            return self.available_models[0]
        else:
            return "mistral:instruct"
    
    def test_model_availability(self, model):
        """Test if a model is available and show warning if not"""
        try:
            # Test if the selected model is available
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": "test"},
                timeout=2  # Short timeout for quick check
            )
            
            if response.status_code == 404:
                messagebox.showwarning(
                    "Model Not Available", 
                    f"The model '{model}' is not available on this system.\n\n" +
                    "This may be because you're on a dual-boot system and the model is only installed on your other OS.\n\n" +
                    "The app will automatically fall back to an available model when needed."
                )
                return False
            return True
        except Exception:
            # Ignore connection errors during testing
            return False
    
    def get_best_available_model(self, requested_model):
        """Get the best available model, falling back if necessary"""
        if requested_model in self.available_models:
            return requested_model
        
        # Try fallback models in order
        for fallback in self.fallback_models:
            if fallback in self.available_models:
                print(f"Model {requested_model} not available, using {fallback} instead")
                return fallback
        
        # If no fallbacks are available, return the requested model anyway
        # (the query will fail, but with a clear error message)
        return requested_model
    
    def list_available_models(self):
        """Get a formatted string listing all available models"""
        self.refresh_available_models()
        
        if not self.available_models:
            return "No models available. Please make sure Ollama is running."
        
        return "Available models:\n" + "\n".join([f"- {model}" for model in self.available_models])
    
    def query_ollama(self, prompt, model=None):
        """Query Ollama with fallback handling"""
        if model is None:
            model = self.get_default_model()
        
        # Get the best available model
        best_model = self.get_best_available_model(model)
        
        try:
            # Direct API call to Ollama
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": best_model, "prompt": prompt}
            )
            
            if response.status_code == 200:
                # Extract the response text
                result = ""
                for line in response.text.strip().split("\n"):
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            result += data["response"]
                return result
            elif response.status_code == 404:
                # Model not found error - refresh available models and try ANY available model
                self.refresh_available_models()
                
                if len(self.available_models) > 0:
                    # Try with the first available model
                    any_model = self.available_models[0]
                    print(f"Model '{best_model}' not found. Trying with '{any_model}' instead.")
                    
                    # Try again with the first available model
                    try:
                        response = requests.post(
                            "http://localhost:11434/api/generate",
                            json={"model": any_model, "prompt": prompt}
                        )
                        
                        if response.status_code == 200:
                            # Extract the response text
                            result = ""
                            for line in response.text.strip().split("\n"):
                                if line:
                                    data = json.loads(line)
                                    if "response" in data:
                                        result += data["response"]
                            return f"[Using model: {any_model}] " + result
                    except Exception:
                        pass
                
                # If we get here, we couldn't find any working model
                error_msg = f"Error: Model '{best_model}' not found. This may be because you're on a dual-boot system and the model is only installed on your other OS. Please select a different model in Settings."
                print(error_msg)
                return error_msg
            else:
                return f"Error: Ollama returned status code {response.status_code}"
        except Exception as e:
            return f"Error querying Ollama: {str(e)}"

# Create a singleton instance
model_manager = ModelManager()