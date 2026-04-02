import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import sys
import threading
import time
import math
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Import the SystemControlTab
from system_control import SystemControlTab

# Import the ModelManager
from model_manager import model_manager

# Set appearance mode and default color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Constants
APP_NAME = "BRIX"
APP_VERSION = "1.0"

class BreathingBackground(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs, highlightthickness=0)
        self.master = master
        self.configure(bg="#ffffff")
        
        # Animation parameters
        self.shapes = []
        self.colors = [
            "#FFD6E0", "#FFEFCF", "#D1F0E1", "#C7CEEA", "#E2F0CB",
            "#FFC3A0", "#D0E6A5", "#FFCCB6", "#A2D2FF", "#CDB4DB"
        ]
        self.create_shapes()
        self.animate()
    
    def create_shapes(self):
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        
        # Create several shapes with different colors
        for i in range(5):
            color = self.colors[i % len(self.colors)]
            x = width * (0.2 + 0.15 * i)
            y = height * (0.3 + 0.1 * i)
            size = min(width, height) * (0.2 + 0.05 * i)
            
            shape = self.create_oval(
                x - size/2, y - size/2, 
                x + size/2, y + size/2, 
                fill=color, outline="", tags=f"shape{i}"
            )
            
            self.shapes.append({
                "id": shape,
                "base_size": size,
                "x": x,
                "y": y,
                "phase": i * math.pi / 5  # Different starting phases
            })
    
    def animate(self):
        t = time.time()
        
        for shape in self.shapes:
            # Breathing effect - size oscillates
            scale = 1.0 + 0.1 * math.sin(t + shape["phase"])
            size = shape["base_size"] * scale
            
            # Update shape size
            self.coords(
                shape["id"],
                shape["x"] - size/2, shape["y"] - size/2,
                shape["x"] + size/2, shape["y"] + size/2
            )
        
        self.after(50, self.animate)  # Update every 50ms

class GlassMorphicFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            corner_radius=15,
            border_width=1,
            border_color="#E0E0E0",
            fg_color=("#FFFFFF", "#FFFFFF")
        )

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color="transparent")
        self.master = master
        self.on_login_success = on_login_success
        
        # Create breathing background
        self.background = BreathingBackground(self, width=600, height=400)
        self.background.pack(fill="both", expand=True)
        
        # Create login frame
        self.login_frame = GlassMorphicFrame(
            self.background,
            width=350,
            height=400,
        )
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # App logo/icon
        self.logo_label = ctk.CTkLabel(
            self.login_frame,
            text="🧠",
            font=ctk.CTkFont(size=48)
        )
        self.logo_label.place(relx=0.5, rely=0.12, anchor="center")
        
        # App title
        self.title_label = ctk.CTkLabel(
            self.login_frame,
            text="BRIX",
            font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"),
            text_color="#333333"
        )
        self.title_label.place(relx=0.5, rely=0.25, anchor="center")
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.login_frame,
            text="Bluerope Intelligence Exchange",
            font=ctk.CTkFont(family="Helvetica", size=14),
            text_color="#666666"
        )
        self.subtitle_label.place(relx=0.5, rely=0.32, anchor="center")
        
        # Username entry
        self.username_entry = ctk.CTkEntry(
            self.login_frame,
            width=250,
            height=40,
            corner_radius=8,
            placeholder_text="Username",
            border_color="#E0E0E0",
            fg_color="#F5F5F5"
        )
        self.username_entry.place(relx=0.5, rely=0.45, anchor="center")
        
        # Password entry
        self.password_entry = ctk.CTkEntry(
            self.login_frame,
            width=250,
            height=40,
            corner_radius=8,
            placeholder_text="Password",
            border_color="#E0E0E0",
            fg_color="#F5F5F5",
            show="•"
        )
        self.password_entry.place(relx=0.5, rely=0.58, anchor="center")
        
        # Login button
        self.login_button = ctk.CTkButton(
            self.login_frame,
            text="Login",
            width=250,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            fg_color="#4A6FDC",
            hover_color="#3A5FCC",
            command=self.login
        )
        self.login_button.place(relx=0.5, rely=0.72, anchor="center")
        
        # Version info
        self.version_label = ctk.CTkLabel(
            self.login_frame,
            text=f"{APP_NAME} v{APP_VERSION}",
            font=ctk.CTkFont(family="Helvetica", size=10),
            text_color="#999999"
        )
        self.version_label.place(relx=0.5, rely=0.9, anchor="center")
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Check credentials
        if username == "chandan" and password == "Chandan0929":
            self.on_login_success()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

class ChatTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Check if Ollama is available
        self.ai_available = self.check_ollama_available()
        
        # Chat display area
        self.chat_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="#F5F5F5",
            corner_radius=10,
            width=580,
            height=300
        )
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
        # Message input area
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=10, pady=5)
        
        self.message_input = ctk.CTkTextbox(
            self.input_frame,
            height=60,
            corner_radius=10,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#E0E0E0"
        )
        self.message_input.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="Send",
            width=80,
            height=40,
            corner_radius=10,
            fg_color="#4A6FDC",
            hover_color="#3A5FCC",
            command=self.send_message
        )
        self.send_button.pack(side="right")
        
        # Welcome message
        self.add_bot_message("Hello! I'm BRIX, your AI assistant. How can I help you today?")
    
    def check_ollama_available(self):
        try:
            # Try to connect to Ollama API
            response = requests.get("http://localhost:11434/api/tags")
            return response.status_code == 200
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            return False
    
    def query_ollama(self, prompt, model="mistral:instruct"):
        try:
            # Direct API call to Ollama
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt}
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
            else:
                return f"Error: Ollama returned status code {response.status_code}"
        except Exception as e:
            return f"Error querying Ollama: {str(e)}"
    
    def add_user_message(self, message):
        frame = ctk.CTkFrame(
            self.chat_frame,
            fg_color="#E1EBFF",
            corner_radius=10
        )
        frame.pack(fill="x", padx=10, pady=5, anchor="e")
        
        label = ctk.CTkLabel(
            frame,
            text=message,
            wraplength=400,
            justify="left",
            text_color="#333333"
        )
        label.pack(padx=10, pady=10)
        
        # Scroll to bottom
        self.chat_frame._parent_canvas.yview_moveto(1.0)
    
    def add_bot_message(self, message):
        frame = ctk.CTkFrame(
            self.chat_frame,
            fg_color="#FFFFFF",
            corner_radius=10
        )
        frame.pack(fill="x", padx=10, pady=5, anchor="w")
        
        label = ctk.CTkLabel(
            frame,
            text=message,
            wraplength=400,
            justify="left",
            text_color="#333333"
        )
        label.pack(padx=10, pady=10)
        
        # Scroll to bottom
        self.chat_frame._parent_canvas.yview_moveto(1.0)
        
        return frame
    
    def send_message(self):
        message = self.message_input.get("1.0", "end-1c").strip()
        if not message:
            return
        
        self.add_user_message(message)
        self.message_input.delete("1.0", "end")
        
        if self.ai_available:
            # Show typing indicator
            indicator_frame = self.add_bot_message("Thinking...")
            
            # Update UI
            self.update_idletasks()
            
            # Get model from settings
            model = None
            try:
                for widget in self.winfo_toplevel().winfo_children():
                    if hasattr(widget, 'main_app'):
                        model = widget.main_app.settings_tab.model_option.get()
                        break
            except:
                # Import model manager for default model
                from model_manager import model_manager
                model = model_manager.get_default_model()
            
            # Get response from Ollama in a separate thread to avoid freezing UI
            def get_response():
                # Use model manager for query
                from model_manager import model_manager
                response = model_manager.query_ollama(message, model)
                
                # Update UI in the main thread
                self.after(0, lambda: self.update_response(indicator_frame, response))
            
            threading.Thread(target=get_response, daemon=True).start()
        else:
            self.add_bot_message("AI functionality is not available. Please make sure Ollama is running.")
    
    def update_response(self, indicator_frame, response):
        # Remove typing indicator
        indicator_frame.destroy()
        
        # Add response
        self.add_bot_message(response)

class AgentTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Check if Ollama is available
        self.ai_available = self.check_ollama_available()
        
        # Agent creation section
        self.create_frame = GlassMorphicFrame(self)
        self.create_frame.pack(fill="x", padx=10, pady=10)
        
        self.title_label = ctk.CTkLabel(
            self.create_frame,
            text="Create AI Agent",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="#333333"
        )
        self.title_label.pack(padx=10, pady=(10, 5))
        
        # Agent name
        self.name_frame = ctk.CTkFrame(self.create_frame, fg_color="transparent")
        self.name_frame.pack(fill="x", padx=10, pady=5)
        
        self.name_label = ctk.CTkLabel(
            self.name_frame,
            text="Agent Name:",
            width=100,
            text_color="#333333"
        )
        self.name_label.pack(side="left")
        
        self.name_entry = ctk.CTkEntry(
            self.name_frame,
            placeholder_text="e.g., DataAnalyst",
            fg_color="#F5F5F5"
        )
        self.name_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Agent goal
        self.goal_frame = ctk.CTkFrame(self.create_frame, fg_color="transparent")
        self.goal_frame.pack(fill="x", padx=10, pady=5)
        
        self.goal_label = ctk.CTkLabel(
            self.goal_frame,
            text="Agent Goal:",
            width=100,
            text_color="#333333"
        )
        self.goal_label.pack(side="left", anchor="n")
        
        self.goal_entry = ctk.CTkTextbox(
            self.goal_frame,
            height=60,
            fg_color="#F5F5F5"
        )
        self.goal_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Create button
        self.create_button = ctk.CTkButton(
            self.create_frame,
            text="Create Agent",
            fg_color="#4A6FDC",
            hover_color="#3A5FCC",
            command=self.create_agent
        )
        self.create_button.pack(pady=10)
        
        # Agent interaction section
        self.interact_frame = GlassMorphicFrame(self)
        self.interact_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.agent_label = ctk.CTkLabel(
            self.interact_frame,
            text="No Agent Selected",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="#333333"
        )
        self.agent_label.pack(padx=10, pady=10)
        
        # Agent chat
        self.agent_chat = ctk.CTkScrollableFrame(
            self.interact_frame,
            fg_color="#F5F5F5",
            corner_radius=10
        )
        self.agent_chat.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Current agent
        self.current_agent = None
    
    def check_ollama_available(self):
        try:
            # Try to connect to Ollama API
            response = requests.get("http://localhost:11434/api/tags")
            return response.status_code == 200
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            return False
    
    def query_ollama(self, prompt, model="mistral:instruct"):
        try:
            # Direct API call to Ollama
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt}
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
            else:
                return f"Error: Ollama returned status code {response.status_code}"
        except Exception as e:
            return f"Error querying Ollama: {str(e)}"
    
    def create_agent(self):
        name = self.name_entry.get().strip()
        goal = self.goal_entry.get("1.0", "end-1c").strip()
        
        if not name or not goal:
            messagebox.showerror("Error", "Agent name and goal are required")
            return
        
        self.current_agent = {
            "name": name,
            "goal": goal
        }
        
        self.agent_label.configure(text=f"Agent: {name}")
        self.add_message(f"Agent '{name}' created with goal: {goal}")
        
        # Add input for agent interaction
        if hasattr(self, 'input_frame'):
            self.input_frame.destroy()
        
        self.input_frame = ctk.CTkFrame(self.interact_frame, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=10, pady=10)
        
        self.agent_input = ctk.CTkEntry(
            self.input_frame,
            placeholder_text=f"Ask {name}...",
            fg_color="#FFFFFF",
            height=40
        )
        self.agent_input.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.ask_button = ctk.CTkButton(
            self.input_frame,
            text="Ask",
            width=80,
            fg_color="#4A6FDC",
            hover_color="#3A5FCC",
            command=self.ask_agent
        )
        self.ask_button.pack(side="right")
    
    def add_message(self, message, is_user=False):
        frame = ctk.CTkFrame(
            self.agent_chat,
            fg_color="#E1EBFF" if is_user else "#FFFFFF",
            corner_radius=10
        )
        frame.pack(fill="x", padx=10, pady=5, anchor="e" if is_user else "w")
        
        label = ctk.CTkLabel(
            frame,
            text=message,
            wraplength=400,
            justify="left",
            text_color="#333333"
        )
        label.pack(padx=10, pady=10)
        
        # Scroll to bottom
        self.agent_chat._parent_canvas.yview_moveto(1.0)
        
        return frame
    
    def ask_agent(self):
        if not self.current_agent:
            return
        
        query = self.agent_input.get().strip()
        if not query:
            return
        
        self.add_message(query, is_user=True)
        self.agent_input.delete(0, "end")
        
        if self.ai_available:
            # Show typing indicator
            indicator_frame = self.add_message("Thinking...")
            
            # Update UI
            self.update_idletasks()
            
            # Create prompt for agent
            prompt = f"You are an AI agent named {self.current_agent['name']} with the following goal: {self.current_agent['goal']}\n\nUser query: {query}\n\nRespond as {self.current_agent['name']}:"
            
            # Get model from settings
            model = None
            try:
                for widget in self.winfo_toplevel().winfo_children():
                    if hasattr(widget, 'main_app'):
                        model = widget.main_app.settings_tab.model_option.get()
                        break
            except:
                model = model_manager.get_default_model()
            
            # Get response from Ollama in a separate thread to avoid freezing UI
            def get_response():
                response = model_manager.query_ollama(prompt, model)
                
                # Update UI in the main thread
                self.after(0, lambda: self.update_response(indicator_frame, response))
            
            threading.Thread(target=get_response, daemon=True).start()
        else:
            self.add_message("AI functionality is not available. Please make sure Ollama is running.")
    
    def update_response(self, indicator_frame, response):
        # Remove typing indicator
        indicator_frame.destroy()
        
        # Add response
        self.add_message(response)

class FileProcessingTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Check if Ollama is available
        self.ai_available = self.check_ollama_available()
        
        # File upload section
        self.upload_frame = GlassMorphicFrame(self)
        self.upload_frame.pack(fill="x", padx=10, pady=10)
        
        self.title_label = ctk.CTkLabel(
            self.upload_frame,
            text="Upload & Summarize File",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="#333333"
        )
        self.title_label.pack(padx=10, pady=(10, 5))
        
        self.upload_button = ctk.CTkButton(
            self.upload_frame,
            text="Upload File",
            width=200,
            height=40,
            corner_radius=8,
            fg_color="#4A6FDC",
            hover_color="#3A5FCC",
            command=self.upload_file
        )
        self.upload_button.pack(pady=10)
        
        self.file_info = ctk.CTkLabel(
            self.upload_frame,
            text="Supported formats: TXT, CSV, PDF",
            text_color="#666666"
        )
        self.file_info.pack(pady=(0, 10))
        
        # Results section
        self.results_frame = GlassMorphicFrame(self)
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.results_label = ctk.CTkLabel(
            self.results_frame,
            text="Results",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="#333333"
        )
        self.results_label.pack(padx=10, pady=10)
        
        self.results_text = ctk.CTkTextbox(
            self.results_frame,
            wrap="word",
            fg_color="#F5F5F5",
            corner_radius=8
        )
        self.results_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.results_text.configure(state="disabled")
    
    def check_ollama_available(self):
        try:
            # Try to connect to Ollama API
            response = requests.get("http://localhost:11434/api/tags")
            return response.status_code == 200
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            return False
    
    def query_ollama(self, prompt, model="mistral:instruct"):
        try:
            # Direct API call to Ollama
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt}
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
            else:
                return f"Error: Ollama returned status code {response.status_code}"
        except Exception as e:
            return f"Error querying Ollama: {str(e)}"
    
    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # Show processing message
        self.update_results(f"Processing {os.path.basename(file_path)}...")
        self.update_idletasks()
        
        if self.ai_available:
            try:
                # Read file content
                with open(file_path, 'r', errors='ignore') as f:
                    content = f.read()
                
                # Limit content size to avoid overwhelming Ollama
                if len(content) > 10000:
                    content = content[:10000] + "\n\n[Content truncated due to size...]\n"
                
                # Create prompt for summarization
                prompt = f"Please summarize the following document:\n\n{content}"
                
                # Get model from settings
                model = None
                try:
                    for widget in self.winfo_toplevel().winfo_children():
                        if hasattr(widget, 'main_app'):
                            model = widget.main_app.settings_tab.model_option.get()
                            break
                except:
                    model = model_manager.get_default_model()
                
                # Get summary from Ollama
                summary = model_manager.query_ollama(prompt, model)
                
                # Update results
                self.update_results(f"Summary of {os.path.basename(file_path)}:\n\n{summary}")
            except Exception as e:
                self.update_results(f"Error processing file: {str(e)}")
        else:
            self.update_results(f"AI functionality is not available. Please make sure Ollama is running.")
    
    def update_results(self, text):
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", text)
        self.results_text.configure(state="disabled")

class SpreadsheetTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Check if Ollama is available
        self.ai_available = self.check_ollama_available()
        
        # Store dataframe
        self.df = None
        
        # Spreadsheet input section
        self.input_frame = GlassMorphicFrame(self)
        self.input_frame.pack(fill="x", padx=10, pady=10)
        
        self.title_label = ctk.CTkLabel(
            self.input_frame,
            text="Analyze Spreadsheet",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="#333333"
        )
        self.title_label.pack(padx=10, pady=(10, 5))
        
        # Google Sheet input
        self.sheet_label = ctk.CTkLabel(
            self.input_frame,
            text="Google Sheet URL:",
            text_color="#333333"
        )
        self.sheet_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        self.sheet_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Paste Google Sheet link (anyone can view)",
            width=400,
            height=35,
            corner_radius=8,
            fg_color="#F5F5F5"
        )
        self.sheet_entry.pack(fill="x", padx=10, pady=(0, 5))
        
        self.load_sheet_button = ctk.CTkButton(
            self.input_frame,
            text="Load Google Sheet",
            width=150,
            height=35,
            corner_radius=8,
            fg_color="#4A6FDC",
            hover_color="#3A5FCC",
            command=self.load_google_sheet
        )
        self.load_sheet_button.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Excel upload
        self.excel_label = ctk.CTkLabel(
            self.input_frame,
            text="Or upload Excel file:",
            text_color="#333333"
        )
        self.excel_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.upload_excel_button = ctk.CTkButton(
            self.input_frame,
            text="Upload Excel File",
            width=150,
            height=35,
            corner_radius=8,
            fg_color="#4A6FDC",
            hover_color="#3A5FCC",
            command=self.upload_excel
        )
        self.upload_excel_button.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Data display and analysis section
        self.data_frame = GlassMorphicFrame(self)
        self.data_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.data_label = ctk.CTkLabel(
            self.data_frame,
            text="Data Preview",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="#333333"
        )
        self.data_label.pack(padx=10, pady=10)
        
        # Data preview
        self.data_text = ctk.CTkTextbox(
            self.data_frame,
            wrap="none",
            fg_color="#F5F5F5",
            corner_radius=8,
            height=150
        )
        self.data_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.data_text.configure(state="disabled")
        
        # Question input
        self.question_frame = ctk.CTkFrame(self.data_frame, fg_color="transparent")
        self.question_frame.pack(fill="x", padx=10, pady=10)
        
        self.question_entry = ctk.CTkEntry(
            self.question_frame,
            placeholder_text="Ask something about this data",
            height=35,
            corner_radius=8,
            fg_color="#F5F5F5"
        )
        self.question_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.ask_button = ctk.CTkButton(
            self.question_frame,
            text="Ask",
            width=80,
            height=35,
            corner_radius=8,
            fg_color="#4A6FDC",
            hover_color="#3A5FCC",
            command=self.ask_question
        )
        self.ask_button.pack(side="right")
        
        # Answer display
        self.answer_text = ctk.CTkTextbox(
            self.data_frame,
            wrap="word",
            fg_color="#F5F5F5",
            corner_radius=8,
            height=100
        )
        self.answer_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.answer_text.configure(state="disabled")
    
    def load_google_sheet(self):
        sheet_link = self.sheet_entry.get().strip()
        if not sheet_link:
            messagebox.showerror("Error", "Please enter a Google Sheet URL")
            return
        
        try:
            # Show loading message
            self.update_data_preview("Loading Google Sheet...")
            self.update_idletasks()
            
            # Extract file ID from the URL
            if "/d/" in sheet_link and "/" in sheet_link.split("/d/")[1]:
                file_id = sheet_link.split("/d/")[1].split("/")[0]
            else:
                messagebox.showerror("Error", "Invalid Google Sheet URL format")
                return
            
            # Create export URL
            export_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"
            
            # Download the sheet
            response = requests.get(export_url)
            if response.status_code != 200:
                messagebox.showerror("Error", f"Failed to download sheet: Status code {response.status_code}")
                return
            
            # Save to temp file
            os.makedirs("temp", exist_ok=True)
            temp_path = os.path.join("temp", "google_sheet.csv")
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            # Load with pandas
            self.df = pd.read_csv(temp_path)
            
            # Update preview
            preview = self.df.head(10).to_string(index=False)
            self.update_data_preview(preview)
            
            messagebox.showinfo("Success", "Google Sheet loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Google Sheet: {str(e)}")
    
    def upload_excel(self):
        file_path = filedialog.askopenfilename(
            title="Select Excel file",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # Show loading message
            self.update_data_preview("Loading spreadsheet...")
            self.update_idletasks()
            
            # Load file based on extension
            if file_path.endswith(".csv"):
                self.df = pd.read_csv(file_path)
            else:
                self.df = pd.read_excel(file_path)
            
            # Update preview
            preview = self.df.head(10).to_string(index=False)
            self.update_data_preview(preview)
            
            messagebox.showinfo("Success", "File loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            self.df = None
    
    def update_data_preview(self, text):
        self.data_text.configure(state="normal")
        self.data_text.delete("1.0", "end")
        self.data_text.insert("1.0", text)
        self.data_text.configure(state="disabled")
    
    def check_ollama_available(self):
        try:
            # Try to connect to Ollama API
            response = requests.get("http://localhost:11434/api/tags")
            return response.status_code == 200
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            return False
    
    def query_ollama(self, prompt, model="mistral:instruct"):
        try:
            # Direct API call to Ollama
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt}
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
            else:
                return f"Error: Ollama returned status code {response.status_code}"
        except Exception as e:
            return f"Error querying Ollama: {str(e)}"
    
    def ask_question(self):
        question = self.question_entry.get().strip()
        if not question:
            return
        
        # Show processing message
        self.update_answer("Analyzing...")
        self.update_idletasks()
        
        # Check if Ollama is available
        ai_available = self.check_ollama_available()
        
        if ai_available:
            try:
                # Get data preview as context
                data_preview = self.data_text.get("1.0", "end-1c")
                
                # Create prompt with data and question
                prompt = f"Here is some tabular data:\n\n{data_preview}\n\nQuestion: {question}\n\nAnswer:"
                
                # Get model from settings
                model = None
                try:
                    for widget in self.winfo_toplevel().winfo_children():
                        if hasattr(widget, 'main_app'):
                            model = widget.main_app.settings_tab.model_option.get()
                            break
                except:
                    model = model_manager.get_default_model()
                
                # Get answer from Ollama
                answer = model_manager.query_ollama(prompt, model)
                
                # Update answer display
                self.update_answer(answer)
            except Exception as e:
                self.update_answer(f"Error: {str(e)}")
        else:
            self.update_answer(f"AI functionality is not available. Please make sure Ollama is running.")
    
    def update_answer(self, text):
        self.answer_text.configure(state="normal")
        self.answer_text.delete("1.0", "end")
        self.answer_text.insert("1.0", text)
        self.answer_text.configure(state="disabled")

class WebSearchTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Check if Ollama is available
        self.ai_available = self.check_ollama_available()
        
        # Search input section
        self.search_frame = GlassMorphicFrame(self)
        self.search_frame.pack(fill="x", padx=10, pady=10)
        
        self.title_label = ctk.CTkLabel(
            self.search_frame,
            text="Web Search Agent",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="#333333"
        )
        self.title_label.pack(padx=10, pady=(10, 5))
        
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Enter your search query",
            height=40,
            corner_radius=8,
            fg_color="#F5F5F5"
        )
        self.search_entry.pack(fill="x", padx=10, pady=10)
        
        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="Search",
            width=150,
            height=40,
            corner_radius=8,
            fg_color="#4A6FDC",
            hover_color="#3A5FCC",
            command=self.search_web
        )
        self.search_button.pack(pady=(0, 10))
        
        # Results section
        self.results_frame = GlassMorphicFrame(self)
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.results_label = ctk.CTkLabel(
            self.results_frame,
            text="Search Results",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="#333333"
        )
        self.results_label.pack(padx=10, pady=10)
        
        self.results_text = ctk.CTkTextbox(
            self.results_frame,
            wrap="word",
            fg_color="#F5F5F5",
            corner_radius=8
        )
        self.results_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.results_text.configure(state="disabled")
    
    def check_ollama_available(self):
        try:
            # Try to connect to Ollama API
            response = requests.get("http://localhost:11434/api/tags")
            return response.status_code == 200
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            return False
    
    def query_ollama(self, prompt, model="mistral:instruct"):
        try:
            # Direct API call to Ollama
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt}
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
            else:
                return f"Error: Ollama returned status code {response.status_code}"
        except Exception as e:
            return f"Error querying Ollama: {str(e)}"
    
    def perform_web_search(self, query):
        try:
            # Simple web search using Google
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            headers = {"User-Agent": "Mozilla/5.0"}
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract search results
            results = []
            for div in soup.find_all("div", class_=["BNeawe s3v9rd AP7Wnd", "kCrYT"]):
                text = div.get_text()
                if text.strip():
                    results.append(text.strip())
            
            # Return the first few results
            return "\n\n".join(results[:5])
        except Exception as e:
            return f"Error performing web search: {str(e)}"
    
    def search_web(self):
        query = self.search_entry.get().strip()
        if not query:
            return
        
        # Show searching message
        self.update_results(f"Searching for: {query}...")
        self.update_idletasks()
        
        if self.ai_available:
            try:
                # Perform web search
                search_results = self.perform_web_search(query)
                
                # Create prompt with search results
                prompt = f"Web search results for '{query}':\n\n{search_results}\n\nPlease provide a helpful summary of these search results, answering the query: {query}"
                
                # Get model from settings
                model = None
                try:
                    for widget in self.winfo_toplevel().winfo_children():
                        if hasattr(widget, 'main_app'):
                            model = widget.main_app.settings_tab.model_option.get()
                            break
                except:
                    model = model_manager.get_default_model()
                
                # Get analysis from Ollama
                analysis = model_manager.query_ollama(prompt, model)
                
                # Update results
                self.update_results(f"Results for: {query}\n\n{analysis}")
            except Exception as e:
                self.update_results(f"Error: {str(e)}")
        else:
            self.update_results(f"AI functionality is not available. Please make sure Ollama is running.")
    
    def update_results(self, text):
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", text)
        self.results_text.configure(state="disabled")

class SheetMonitorTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Monitor setup section
        self.setup_frame = GlassMorphicFrame(self)
        self.setup_frame.pack(fill="x", padx=10, pady=10)
        
        self.title_label = ctk.CTkLabel(
            self.setup_frame,
            text="Google Sheet Monitor",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="#333333"
        )
        self.title_label.pack(padx=10, pady=(10, 5))
        
        self.info_label = ctk.CTkLabel(
            self.setup_frame,
            text="Monitor a Google Sheet for changes and get notifications",
            text_color="#666666"
        )
        self.info_label.pack(padx=10, pady=(0, 10))
        
        # Sheet URL input
        self.url_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        self.url_frame.pack(fill="x", padx=10, pady=5)
        
        self.url_label = ctk.CTkLabel(
            self.url_frame,
            text="Sheet URL:",
            width=100,
            text_color="#333333"
        )
        self.url_label.pack(side="left")
        
        self.url_entry = ctk.CTkEntry(
            self.url_frame,
            placeholder_text="Paste Google Sheet link (anyone with link can view)",
            fg_color="#F5F5F5"
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Check interval
        self.interval_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        self.interval_frame.pack(fill="x", padx=10, pady=5)
        
        self.interval_label = ctk.CTkLabel(
            self.interval_frame,
            text="Check every:",
            width=100,
            text_color="#333333"
        )
        self.interval_label.pack(side="left")
        
        self.interval_slider = ctk.CTkSlider(
            self.interval_frame,
            from_=10,
            to=120,
            number_of_steps=11,
            width=300
        )
        self.interval_slider.pack(side="left", padx=(5, 5))
        self.interval_slider.set(30)
        
        self.interval_value = ctk.CTkLabel(
            self.interval_frame,
            text="30 seconds",
            text_color="#333333"
        )
        self.interval_value.pack(side="left", padx=(5, 0))
        
        # Update interval value when slider changes
        self.interval_slider.configure(command=self.update_interval_value)
        
        # Start/stop buttons
        self.button_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_button = ctk.CTkButton(
            self.button_frame,
            text="Start Monitoring",
            width=150,
            height=40,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#43A047",
            command=self.start_monitoring
        )
        self.start_button.pack(side="left", padx=(0, 10))
        
        self.stop_button = ctk.CTkButton(
            self.button_frame,
            text="Stop Monitoring",
            width=150,
            height=40,
            corner_radius=8,
            fg_color="#F44336",
            hover_color="#E53935",
            command=self.stop_monitoring,
            state="disabled"
        )
        self.stop_button.pack(side="left")
        
        # Log section
        self.log_frame = GlassMorphicFrame(self)
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log_label = ctk.CTkLabel(
            self.log_frame,
            text="Monitoring Log",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="#333333"
        )
        self.log_label.pack(padx=10, pady=10)
        
        self.log_text = ctk.CTkTextbox(
            self.log_frame,
            wrap="word",
            fg_color="#F5F5F5",
            corner_radius=8
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Monitoring state
        self.monitoring = False
    
    def update_interval_value(self, value):
        seconds = int(value)
        self.interval_value.configure(text=f"{seconds} seconds")
    
    def start_monitoring(self):
        sheet_url = self.url_entry.get().strip()
        if not sheet_url:
            messagebox.showerror("Error", "Please enter a Google Sheet URL")
            return
        
        interval = int(self.interval_slider.get())
        
        # Update UI
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.monitoring = True
        
        # Add log entry
        self.add_log(f"Started monitoring {sheet_url} every {interval} seconds")
        self.add_log("This is a simulated monitoring service. To enable actual monitoring, install the required dependencies.")
    
    def stop_monitoring(self):
        self.monitoring = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.add_log("Monitoring stopped")
    
    def add_log(self, message):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n\n"
        
        self.log_text.insert("1.0", log_entry)

class SettingsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Settings content
        self.settings_frame = GlassMorphicFrame(self)
        self.settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.title_label = ctk.CTkLabel(
            self.settings_frame,
            text="Settings",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="#333333"
        )
        self.title_label.pack(padx=10, pady=10)
        
        # Theme setting
        self.theme_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.theme_frame.pack(fill="x", pady=10)
        
        self.theme_label = ctk.CTkLabel(
            self.theme_frame,
            text="Theme:",
            width=100,
            text_color="#333333"
        )
        self.theme_label.pack(side="left", padx=10)
        
        self.theme_option = ctk.CTkOptionMenu(
            self.theme_frame,
            values=["Light", "Dark", "System"],
            width=200,
            fg_color="#F5F5F5",
            button_color="#4A6FDC",
            button_hover_color="#3A5FCC",
            dropdown_fg_color="#FFFFFF",
            dropdown_hover_color="#F0F0F0",
            dropdown_text_color="#333333",
            text_color="#333333",
            command=self.change_theme
        )
        self.theme_option.pack(side="left", padx=10)
        self.theme_option.set("Light")
        
        # Notifications setting
        self.notif_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.notif_frame.pack(fill="x", pady=10)
        
        self.notif_label = ctk.CTkLabel(
            self.notif_frame,
            text="Notifications:",
            width=100,
            text_color="#333333"
        )
        self.notif_label.pack(side="left", padx=10)
        
        self.notif_switch = ctk.CTkSwitch(
            self.notif_frame,
            text="Enabled",
            progress_color="#4A6FDC",
            button_color="#FFFFFF",
            button_hover_color="#F5F5F5",
            fg_color="#E0E0E0",
            text_color="#333333"
        )
        self.notif_switch.pack(side="left", padx=10)
        self.notif_switch.select()
        
        # AI Model setting
        self.model_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.model_frame.pack(fill="x", pady=10)
        
        self.model_label = ctk.CTkLabel(
            self.model_frame,
            text="AI Model:",
            width=100,
            text_color="#333333"
        )
        self.model_label.pack(side="left", padx=10)
        
        # Import model manager
        from model_manager import model_manager
        
        # Get model list from manager
        model_list = model_manager.get_model_list()
        
        self.model_option = ctk.CTkOptionMenu(
            self.model_frame,
            values=model_list,
            width=200,
            fg_color="#F5F5F5",
            button_color="#4A6FDC",
            button_hover_color="#3A5FCC",
            dropdown_fg_color="#FFFFFF",
            dropdown_hover_color="#F0F0F0",
            dropdown_text_color="#333333",
            text_color="#333333",
            command=self.test_model_availability
        )
        self.model_option.pack(side="left", padx=10)
        
        # Add refresh button
        self.refresh_button = ctk.CTkButton(
            self.model_frame,
            text="↻",  # Refresh symbol
            width=40,
            height=28,
            corner_radius=8,
            fg_color="#4CAF50",
            hover_color="#43A047",
            command=self.refresh_models
        )
        self.refresh_button.pack(side="left", padx=5)
        
        # Set default model based on availability
        self.model_option.set(model_manager.get_default_model())
        
        # Available models display
        self.available_models_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.available_models_frame.pack(fill="x", pady=5)
        
        self.available_models_text = ctk.CTkTextbox(
            self.available_models_frame,
            height=100,
            corner_radius=8,
            fg_color="#F5F5F5",
            text_color="#333333"
        )
        self.available_models_text.pack(fill="x", padx=10, pady=5)
        self.available_models_text.insert("1.0", model_manager.list_available_models())
        self.available_models_text.configure(state="disabled")
        
        # Save button
        self.save_button = ctk.CTkButton(
            self.settings_frame,
            text="Save Settings",
            fg_color="#4A6FDC",
            hover_color="#3A5FCC",
            command=self.save_settings
        )
        self.save_button.pack(pady=20)
    
    def change_theme(self, theme):
        if theme == "Light":
            ctk.set_appearance_mode("light")
        elif theme == "Dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("system")
    
    def test_model_availability(self, model):
        # Import model manager
        from model_manager import model_manager
        model_manager.test_model_availability(model)
    
    def refresh_models(self):
        # Import model manager
        from model_manager import model_manager
        
        # Refresh available models
        model_manager.refresh_available_models()
        
        # Update the model list
        model_list = model_manager.get_model_list()
        self.model_option.configure(values=model_list)
        
        # Update the available models text
        self.available_models_text.configure(state="normal")
        self.available_models_text.delete("1.0", "end")
        self.available_models_text.insert("1.0", model_manager.list_available_models())
        self.available_models_text.configure(state="disabled")
        
        # Show a message
        messagebox.showinfo("Models Refreshed", "Available models have been refreshed.")
    
    def save_settings(self):
        # Test if the selected model is available
        from model_manager import model_manager
        model = self.model_option.get()
        model_manager.test_model_availability(model)
        
        # Refresh available models list
        model_manager.refresh_available_models()
        
        messagebox.showinfo("Settings", "Settings saved successfully")

class MainApp(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.master = master
        
        # Create breathing background
        self.background = BreathingBackground(self, width=800, height=600)
        self.background.pack(fill="both", expand=True)
        
        # Create main content frame
        self.content_frame = GlassMorphicFrame(
            self.background,
            width=700,
            height=500,
        )
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # App header
        self.header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent", height=60)
        self.header_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        self.logo_label = ctk.CTkLabel(
            self.header_frame,
            text="🧠",
            font=ctk.CTkFont(size=28)
        )
        self.logo_label.pack(side="left")
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="BRIX",
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
            text_color="#333333"
        )
        self.title_label.pack(side="left", padx=(5, 0))
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Bluerope Intelligence Exchange",
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color="#666666"
        )
        self.subtitle_label.pack(side="left", padx=(10, 0))
        
        # Create tabview
        self.tabview = ctk.CTkTabview(
            self.content_frame,
            corner_radius=10,
            fg_color=("#F5F5F5", "#F5F5F5"),
            segmented_button_fg_color=("#E0E0E0", "#E0E0E0"),
            segmented_button_selected_color=("#4A6FDC", "#4A6FDC"),
            segmented_button_selected_hover_color=("#3A5FCC", "#3A5FCC"),
            segmented_button_unselected_color=("#F5F5F5", "#F5F5F5"),
            segmented_button_unselected_hover_color=("#EAEAEA", "#EAEAEA"),
            text_color=("#333333", "#333333")
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add tabs
        self.tab_system = self.tabview.add("System Control")
        self.tab_chat = self.tabview.add("Chat")
        self.tab_files = self.tabview.add("Files")
        self.tab_sheets = self.tabview.add("Spreadsheets")
        self.tab_search = self.tabview.add("Web Search")
        self.tab_agents = self.tabview.add("AI Agents")
        self.tab_monitor = self.tabview.add("Sheet Monitor")
        self.tab_settings = self.tabview.add("Settings")
        
        # Initialize tabs
        self.system_tab = SystemControlTab(self.tab_system)
        self.system_tab.pack(fill="both", expand=True)
        
        self.chat_tab = ChatTab(self.tab_chat)
        self.chat_tab.pack(fill="both", expand=True)
        
        self.files_tab = FileProcessingTab(self.tab_files)
        self.files_tab.pack(fill="both", expand=True)
        
        self.sheets_tab = SpreadsheetTab(self.tab_sheets)
        self.sheets_tab.pack(fill="both", expand=True)
        
        self.search_tab = WebSearchTab(self.tab_search)
        self.search_tab.pack(fill="both", expand=True)
        
        self.agent_tab = AgentTab(self.tab_agents)
        self.agent_tab.pack(fill="both", expand=True)
        
        self.monitor_tab = SheetMonitorTab(self.tab_monitor)
        self.monitor_tab.pack(fill="both", expand=True)
        
        self.settings_tab = SettingsTab(self.tab_settings)
        self.settings_tab.pack(fill="both", expand=True)

class App:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title(f"{APP_NAME} - Bluerope Intelligence Exchange")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        self.root.minsize(800, 600)
        
        # Center window
        self.center_window()
        
        # Show login screen
        self.show_login()
    
    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - 900) // 2
        y = (screen_height - 700) // 2
        
        self.root.geometry(f"900x700+{x}+{y}")
    
    def show_login(self):
        # Clear any existing frames
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create and show login screen
        self.login_screen = LoginScreen(self.root, self.show_main_app)
        self.login_screen.pack(fill="both", expand=True)
    
    def show_main_app(self):
        # Clear login screen
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create and show main app
        self.main_app = MainApp(self.root)
        self.main_app.pack(fill="both", expand=True)
        
        # Set System Control as the default tab
        self.main_app.tabview.set("System Control")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()