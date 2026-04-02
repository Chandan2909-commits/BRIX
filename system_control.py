import customtkinter as ctk
import os
import subprocess
import threading
import time
import re
import json
import requests
from pathlib import Path
from tkinter import messagebox, filedialog
import pyautogui
import pyperclip
from telegram import Bot  # For Telegram API

# Import custom modules
from browser_control import browser_control
from system_settings import system_settings

class SystemControlTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#1e1e1e")
        
        # Load configuration
        self.config = self.load_config()
        
        # Check if Ollama is available
        self.ai_available = self.check_ollama_available()
        
        # Configure grid for centering
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="#252526", corner_radius=12)
        self.main_container.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        # Configure rows with appropriate weights
        # Row 0 is shared between welcome_frame and os_control_frame (they're never shown together)
        self.main_container.grid_rowconfigure(0, weight=1, minsize=400)  # Primary content area
        self.main_container.grid_rowconfigure(1, weight=0)  # Options frame
        
        # Welcome section
        self.welcome_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.welcome_frame.grid(row=0, column=0, padx=40, pady=(40, 20), sticky="ew")
        
        self.welcome_label = ctk.CTkLabel(
            self.welcome_frame,
            text="System Control",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color="#ffffff"
        )
        self.welcome_label.pack(pady=(0, 5))
        
        self.subtitle_label = ctk.CTkLabel(
            self.welcome_frame,
            text="Choose your action below",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#cccccc"
        )
        self.subtitle_label.pack()
        
        # Action buttons frame
        self.options_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.options_frame.grid(row=1, column=0, padx=40, pady=20)
        
        # Button style
        button_style = {
            "width": 180,
            "height": 60,
            "corner_radius": 8,
            "font": ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            "border_width": 0
        }
        
        # AI Agents button
        self.agents_button = ctk.CTkButton(
            self.options_frame,
            text="AI Agents",
            **button_style,
            fg_color="#0078d4",
            hover_color="#106ebe",
            command=self.switch_to_agents
        )
        self.agents_button.pack(pady=8, fill="x")
        
        # Generate Essay button
        self.essay_button = ctk.CTkButton(
            self.options_frame,
            text="Generate Essay",
            **button_style,
            fg_color="#ff6b35",
            hover_color="#e55a2b",
            command=self.generate_essay_ui
        )
        self.essay_button.pack(pady=8, fill="x")
        
        # OS Control button
        self.os_control_button = ctk.CTkButton(
            self.options_frame,
            text="OS Control",
            **button_style,
            fg_color="#4caf50",
            hover_color="#45a049",
            command=self.show_os_control
        )
        self.os_control_button.pack(pady=8, fill="x")
        
        # OS Control frame (initially hidden)
        self.os_control_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.os_control_frame.grid_columnconfigure(0, weight=1)
        # Configure row weights for proper layout
        self.os_control_frame.grid_rowconfigure(0, weight=0)  # Input frame
        self.os_control_frame.grid_rowconfigure(1, weight=1)  # Output frame (expandable)
        self.os_control_frame.grid_rowconfigure(2, weight=0)  # Quick actions frame
        self.os_control_frame.grid_rowconfigure(3, weight=0)  # Back button
        
        # Command input area
        self.input_frame = ctk.CTkFrame(self.os_control_frame, fg_color="transparent")
        self.input_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(20, 10))
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.command_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Enter command...",
            height=42,
            corner_radius=6,
            fg_color="#3e3e42",
            border_width=0,
            text_color="#ffffff",
            placeholder_text_color="#858585",
            font=ctk.CTkFont(family="Consolas", size=13)
        )
        self.command_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.command_entry.bind("<Return>", lambda event: self.execute_command())
        
        # Submit button
        self.submit_button = ctk.CTkButton(
            self.input_frame,
            text="Run",
            width=60,
            height=42,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#0078d4",
            hover_color="#0063b1",
            text_color="#ffffff",
            command=self.execute_command
        )
        self.submit_button.grid(row=0, column=1, sticky="e")
        
        # Output area
        self.output_frame = ctk.CTkFrame(self.os_control_frame, fg_color="transparent")
        self.output_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=(10, 20))
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(0, weight=1)

        self.output_text = ctk.CTkTextbox(
            self.output_frame,
            height=280,
            corner_radius=6,
            fg_color="#1e1e1e",
            text_color="#cccccc",
            border_width=0,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.output_text.grid(row=0, column=0, sticky="nsew")
        
        # Quick actions
        self.quick_actions_frame = ctk.CTkFrame(self.os_control_frame, fg_color="transparent")
        self.quick_actions_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 10))
        
        quick_commands = [
            ("Gmail Auto-Reply", "open gmail and reply to first 10 messages"),
            ("Gmail Reply 20", "open gmail and reply to first 20 messages"),
            ("Setup Gmail API", "setup gmail api"),
            ("Generate Essay", "generate essay"),
            ("Open Notepad", "open notepad"),
            ("Open Chrome", "open chrome"),
            ("Download VS Code", "download vscode"),
            ("Download Chrome", "download chrome"),
            ("Download Firefox", "download firefox")
        ]
        
        # Configure grid for quick actions frame
        for i in range(3):  # 3 columns
            self.quick_actions_frame.grid_columnconfigure(i, weight=1)
        
        # Create buttons in a 3x3 grid
        for i, (text, command) in enumerate(quick_commands):
            row = i // 3  # Integer division to determine row
            col = i % 3   # Modulo to determine column
            
            btn = ctk.CTkButton(
                self.quick_actions_frame,
                text=text,
                width=120,
                height=32,
                corner_radius=4,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                fg_color="#3e3e42",
                hover_color="#4e4e52",
                text_color="#cccccc",
                command=lambda cmd=command: self.set_command(cmd)
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        # Back button
        self.back_button = ctk.CTkButton(
            self.os_control_frame,
            text="← Back",
            width=80,
            height=32,
            corner_radius=4,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#3e3e42",
            hover_color="#4e4e52",
            text_color="#cccccc",
            command=self.show_welcome
        )
        self.back_button.grid(row=3, column=0, sticky="w", padx=40, pady=(10, 20))
        
        # Store reference to parent for tab switching
        self.parent = parent
        
        # Add initial message to output
        if self.ai_available:
            self.add_output("System Control ready. Enter a command to get started.")
        else:
            self.add_output("System Control ready. Note: AI functionality is not available. Commands will be processed using basic pattern matching.")
    
    def check_ollama_available(self):
        """Check if Ollama is available"""
        # Use model manager to check availability
        from model_manager import model_manager
        return model_manager.refresh_available_models()
    
    def query_ollama(self, prompt, model="mistral:instruct"):
        """Query the Ollama API"""
        # Use model manager for query
        from model_manager import model_manager
        return model_manager.query_ollama(prompt, model)
    
    def generate_essay_ui(self):
        """Show UI for generating essays with LLM"""
        # Create a new window for essay generation
        essay_window = ctk.CTkToplevel(self)
        essay_window.title("Generate Content")
        essay_window.geometry("520x480")
        essay_window.transient(self)
        essay_window.grab_set()
        essay_window.configure(fg_color="#252526")
        
        # Center the window
        essay_window.geometry("+{}+{}".format(
            int(essay_window.winfo_screenwidth()/2 - 260),
            int(essay_window.winfo_screenheight()/2 - 240)
        ))
        
        # Main container
        main_frame = ctk.CTkFrame(essay_window, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Generate Content",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(pady=(0, 25))
        
        # Input fields container
        inputs_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        inputs_frame.pack(fill="x")
        
        # Topic input
        topic_label = ctk.CTkLabel(inputs_frame, text="Topic", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"))
        topic_label.pack(anchor="w", pady=(0, 5))
        
        topic_entry = ctk.CTkEntry(
            inputs_frame, 
            height=36,
            fg_color="#3e3e42",
            border_width=0,
            text_color="#ffffff",
            placeholder_text="Enter topic or prompt...",
            placeholder_text_color="#858585",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        topic_entry.pack(fill="x", pady=(0, 15))
        
        # Two column layout for word count and filename
        fields_frame = ctk.CTkFrame(inputs_frame, fg_color="transparent")
        fields_frame.pack(fill="x", pady=(0, 15))
        fields_frame.grid_columnconfigure(0, weight=1)
        fields_frame.grid_columnconfigure(1, weight=1)
        
        # Word count
        word_count_label = ctk.CTkLabel(fields_frame, text="Word Count", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"))
        word_count_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        word_count_var = ctk.StringVar(value="150")
        word_count_entry = ctk.CTkEntry(
            fields_frame,
            height=36,
            fg_color="#3e3e42",
            border_width=0,
            text_color="#ffffff",
            textvariable=word_count_var,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        word_count_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        
        # Filename
        filename_label = ctk.CTkLabel(fields_frame, text="Filename", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"))
        filename_label.grid(row=0, column=1, sticky="w")
        
        filename_entry = ctk.CTkEntry(
            fields_frame,
            height=36,
            fg_color="#3e3e42",
            border_width=0,
            text_color="#ffffff",
            placeholder_text="my-essay",
            placeholder_text_color="#858585",
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        filename_entry.grid(row=1, column=1, sticky="ew")
        
        # Location
        location_label = ctk.CTkLabel(inputs_frame, text="Save Location", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"))
        location_label.pack(anchor="w", pady=(0, 5))
        
        location_frame = ctk.CTkFrame(inputs_frame, fg_color="transparent")
        location_frame.pack(fill="x", pady=(0, 20))
        
        location_var = ctk.StringVar(value=os.path.join(os.path.expanduser("~"), "Documents"))
        location_entry = ctk.CTkEntry(
            location_frame,
            height=36,
            fg_color="#3e3e42",
            border_width=0,
            text_color="#ffffff",
            textvariable=location_var,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        location_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        def browse_location():
            folder = filedialog.askdirectory()
            if folder:
                location_var.set(folder)
        
        browse_btn = ctk.CTkButton(
            location_frame, 
            text="Browse",
            width=80,
            height=36,
            corner_radius=4,
            fg_color="#0078d4",
            hover_color="#106ebe",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            command=browse_location
        )
        browse_btn.pack(side="right")
        
        # Action buttons
        def generate_and_save():
            topic = topic_entry.get().strip()
            word_count = word_count_var.get().strip()
            filename = filename_entry.get().strip()
            location = location_var.get().strip()
            
            if not topic or not word_count or not filename or not location:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            try:
                word_count_int = int(word_count)
                if word_count_int <= 0:
                    raise ValueError("Word count must be positive")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid word count")
                return
            
            if not os.path.exists(location):
                messagebox.showerror("Error", "Selected location does not exist")
                return
            
            # Close the window and generate the content
            essay_window.destroy()
            self.generate_essay_content(topic, word_count_int, filename, location)
        
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        generate_btn = ctk.CTkButton(
            buttons_frame,
            text="Generate",
            height=36,
            corner_radius=4,
            fg_color="#0078d4",
            hover_color="#106ebe",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=generate_and_save
        )
        generate_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            height=36,
            corner_radius=4,
            fg_color="#3e3e42",
            hover_color="#4e4e52",
            text_color="#cccccc",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=essay_window.destroy
        )
        cancel_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
    
    def type_text_live(self, text, delay=0.05):
        """Type text character by character using pyautogui"""
        try:
            # Open Notepad
            self.add_output("📝 Opening Notepad for live typing...")
            subprocess.Popen(['notepad.exe'])
            time.sleep(2)  # Wait for Notepad to open
            
            # Type the text character by character
            self.add_output("⌨️ Starting live typing animation...")
            pyautogui.typewrite(text, interval=delay)
            
            # Wait a moment before saving
            time.sleep(1)
            
            # Save the file using Ctrl+S
            pyautogui.hotkey('ctrl', 's')
            time.sleep(1)
            
            return True
        except Exception as e:
            self.add_output(f"❌ Error during live typing: {str(e)}")
            return False

    def generate_essay_content(self, topic, word_count, filename, location):
        """Generate essay content using LLM and save to file with live typing"""
        if not self.ai_available:
            self.add_output("AI functionality not available. Cannot generate content.")
            return
        
        self.add_output(f"🤖 Generating {word_count}-word content about: {topic}")
        
        # Create prompt for LLM
        prompt = f"""
        Write a well-structured piece of content about the following topic:
        
        Topic: {topic}
        
        Requirements:
        - Approximately {word_count} words
        - Clear and coherent writing
        - Well-organized structure with introduction, body, and conclusion
        - Engaging and informative
        - Save this as plain text format
        
        Please provide only the content, without any additional formatting or metadata.
        """
        
        try:
            # Generate content using LLM
            content = self.query_ollama(prompt)
            
            if content.startswith("Error"):
                self.add_output(f"❌ Failed to generate content: {content}")
                return
            
            # Ensure filename has .txt extension
            if not filename.lower().endswith('.txt'):
                filename += '.txt'
            
            # Create full file path
            file_path = os.path.join(location, filename)
            
            # Save the content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.add_output(f"✅ Content generated successfully!")
            self.add_output(f"📊 Word count: ~{len(content.split())} words")
            
            # Ask user if they want to see live typing
            if messagebox.askyesno("Live Preview", "Would you like to see the text being typed in Notepad?"):
                # Run live typing in a separate thread to avoid blocking UI
                def live_typing_thread():
                    success = self.type_text_live(content, delay=0.03)
                    if success:
                        # After typing, save the file to the specified location
                        pyperclip.copy(file_path)  # Copy file path to clipboard
                        time.sleep(0.5)
                        pyautogui.hotkey('ctrl', 'l')  # Focus address bar
                        time.sleep(0.2)
                        pyautogui.hotkey('ctrl', 'v')  # Paste file path
                        time.sleep(0.2)
                        pyautogui.press('enter')  # Navigate to location
                        time.sleep(0.5)
                        pyautogui.typewrite(filename)  # Type filename
                        time.sleep(0.2)
                        pyautogui.press('enter')  # Save
                        
                        self.add_output(f"🎯 Live typing completed and saved to: {file_path}")
                    else:
                        # Fallback to just opening the file
                        os.startfile(file_path)
                        self.add_output(f"📁 File opened: {file_path}")
                
                threading.Thread(target=live_typing_thread, daemon=True).start()
            else:
                # Just open the file normally
                os.startfile(file_path)
                self.add_output(f"📁 File opened: {file_path}")
                
        except Exception as e:
            self.add_output(f"❌ Error generating content: {str(e)}")
    
    def show_welcome(self):
        """Show the welcome screen with options"""
        self.os_control_frame.grid_forget()
        self.welcome_frame.grid(row=0, column=0, padx=40, pady=(40, 20), sticky="ew")
        self.options_frame.grid(row=1, column=0, padx=40, pady=20)
    
    def show_os_control(self):
        """Show the OS control interface"""
        self.welcome_frame.grid_forget()
        self.options_frame.grid_forget()
        self.os_control_frame.grid(row=0, column=0, sticky="nsew")
    
    def switch_to_agents(self):
        """Switch to the AI Agents tab"""
        # Find the main app's tabview and switch to the AI Agents tab
        try:
            # Navigate up to find the main app
            main_app = self.winfo_toplevel()
            
            # Access the tabview and set it to the AI Agents tab
            for widget in main_app.winfo_children():
                if hasattr(widget, 'tabview'):
                    widget.tabview.set("AI Agents")
                    return
            
            self.add_output("Could not find the AI Agents tab.")
        except Exception as e:
            self.add_output(f"Error switching tabs: {str(e)}")
    
    def set_command(self, command):
        """Set a command in the entry field and execute it"""
        self.command_entry.delete(0, "end")
        self.command_entry.insert(0, command)
        # Execute the command immediately
        self.execute_command()
    
    def add_output(self, text):
        """Add text to the output area"""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", f"{text}\n\n")
        self.output_text.see("end")
        self.output_text.configure(state="disabled")
    
    def execute_command(self):
        """Parse and execute the user's command"""
        command = self.command_entry.get().strip()
        if not command:
            return
        
        self.add_output(f"> {command}")
        
        # Run command processing in a separate thread to keep UI responsive
        threading.Thread(target=self.process_command, args=(command,), daemon=True).start()
    
    def process_command(self, command):
        """Process and execute the command"""
        command = command.lower()
        
        try:
            # If AI is available, use it for natural language understanding
            if self.ai_available:
                self.add_output("Processing with AI...")
                
                # Create a prompt for the LLM to parse the command
                prompt = f"""
                You are an AI assistant that helps control a Windows computer. Parse the following command and identify the sequence of actions to take.
                
                Command: "{command}"
                
                If this is a single action, respond with a JSON object in this format:
                {{
                    "action": "open_app", // one of: open_app, close_app, list_files, run_command, search_files, unknown
                    "target": "notepad", // the application, file, or location
                    "parameters": {{}} // any additional parameters like shell type for run_command
                }}
                
                If this is a sequence of actions (chain of events), respond with a JSON array of steps like:
                [
                  {{
                    "action": "open_app", 
                    "target": "notepad"
                  }},
                  {{
                    "action": "write_text", 
                    "content": "Hello World"
                  }},
                  {{
                    "action": "save_file", 
                    "filename": "note.txt", 
                    "path": "Downloads"
                  }},
                  {{
                    "action": "open_app", 
                    "target": "telegram"
                  }},
                  {{
                    "action": "send_message", 
                    "recipient": "John", 
                    "message": "Check this!", 
                    "file": "note.txt"
                  }}
                ]
                
                Supported actions: open_app, close_app, list_files, run_command, search_files, write_text, save_file, send_message, gmail_reply, unknown.
                
                Only respond with the JSON object or array, nothing else.
                """
                
                # Query the LLM
                response = self.query_ollama(prompt)
                
                try:
                    # Parse the JSON response
                    parsed = json.loads(response)
                    
                    # Check if it's a chain of events (list) or single action
                    if isinstance(parsed, list):
                        # It's a chain of events
                        if len(parsed) > 5:  # Safety limit
                            if not messagebox.askyesno("Confirm", f"This command will execute {len(parsed)} steps. Continue?"):
                                self.add_output("Chain execution cancelled.")
                                return
                        
                        self.add_output(f"Executing chain of {len(parsed)} steps...")
                        for i, step in enumerate(parsed):
                            self.add_output(f"Step {i+1}/{len(parsed)}: {step.get('action', 'unknown')}")
                            self.execute_step(step)
                            time.sleep(1)  # Brief pause between steps for stability
                        self.add_output("Chain execution complete!")
                    else:
                        # It's a single action
                        # Execute the command based on the parsed action
                        if parsed["action"] == "open_app":
                            self.open_target(parsed["target"])
                        
                        elif parsed["action"] == "close_app":
                            self.close_application(parsed["target"])
                        
                        elif parsed["action"] == "list_files":
                            self.list_files(parsed["target"])
                        
                        elif parsed["action"] == "run_command":
                            shell = parsed.get("parameters", {}).get("shell", "cmd")
                            self.run_shell_command(parsed["target"], shell)
                        
                        elif parsed["action"] == "search_files":
                            location = parsed.get("parameters", {}).get("location", "downloads")
                            file_type = parsed.get("parameters", {}).get("file_type", "*")
                            self.search_files(location, file_type)
                        
                        elif parsed["action"] == "write_text":
                            self.write_text(parsed.get("content", ""))
                            
                        elif parsed["action"] == "save_file":
                            self.save_file(parsed.get("filename", "untitled.txt"), parsed.get("path"))
                            
                        elif parsed["action"] == "send_message":
                            self.send_telegram_message(parsed.get("recipient"), parsed.get("message"), parsed.get("file"))
                        
                        else:  # unknown or unsupported action
                            # Fall back to regex pattern matching
                            self.process_command_with_regex(command)
                
                except (json.JSONDecodeError, KeyError) as e:
                    # If JSON parsing fails, fall back to regex pattern matching
                    self.add_output(f"AI parsing failed, falling back to pattern matching.")
                    self.process_command_with_regex(command)
            
            else:  # AI not available
                # Use regex pattern matching
                self.process_command_with_regex(command)
        
        except Exception as e:
            self.add_output(f"Error: {str(e)}")
    
    def process_command_with_regex(self, command):
        """Process command using regex pattern matching"""
        # Check for multi-step commands (chains)
        chain_steps = self.parse_chain_command(command)
        if chain_steps:
            self.add_output(f"Executing chain of {len(chain_steps)} steps...")
            for i, step in enumerate(chain_steps):
                self.add_output(f"Step {i+1}/{len(chain_steps)}: {step['action']}")
                self.execute_step(step)
            self.add_output("Chain execution complete!")
            return
        
        # Command patterns for single commands
        open_pattern = r"open\s+(.+)"
        close_pattern = r"close\s+(.+)"
        list_files_pattern = r"(?:list|show)\s+(?:files|documents)\s+(?:in|on)\s+(.+)"
        run_cmd_pattern = r"run\s+(.+)\s+in\s+(cmd|powershell)"
        search_web_pattern = r"(?:search|google|youtube)\s+(?:for\s+)?(.+)"
        brightness_pattern = r"(?:set|adjust)\s+brightness\s+(?:to\s+|by\s+)?([+-]?\d+)(%?)"
        volume_pattern = r"(?:set|adjust)\s+volume\s+(?:to\s+|by\s+)?([+-]?\d+)(%?)"
        gmail_reply_pattern = r"(?:open\s+gmail|check\s+gmail|reply\s+to\s+emails|calibrate\s+gmail|setup\s+gmail\s+api)(?:\s+and\s+reply\s+to\s+(?:first\s+)?(\d+)\s+(?:emails|messages))?"
        generate_essay_pattern = r"(?:generate|create|write)\s+(?:essay|content|text)(?:\s+about\s+(.+))?"
        download_pattern = r"(?:download|get|install)\s+(.+)"
        visual_download_pattern = r"(?:visually|auto)\s+download\s+(.+)"
        
        # Open application or file
        if match := re.match(open_pattern, command):
            target = match.group(1).strip()
            # Check if it's a browser
            if target.lower() in ["chrome", "edge", "firefox", "browser"]:
                success, message = browser_control.open_browser(target.lower())
                self.add_output(message)
            else:
                self.open_target(target)
        
        # Close application
        elif match := re.match(close_pattern, command):
            app = match.group(1).strip()
            self.close_application(app)
        
        # List files in directory
        elif match := re.match(list_files_pattern, command):
            location = match.group(1).strip()
            self.list_files(location)
        
        # Run command in CMD or PowerShell
        elif match := re.match(run_cmd_pattern, command):
            cmd = match.group(1).strip()
            shell = match.group(2).strip()
            self.run_shell_command(cmd, shell)
        
        # Search web
        elif match := re.match(search_web_pattern, command):
            query = match.group(1).strip()
            success, message = browser_control.search_in_browser(query)
            self.add_output(message)
        
        # Adjust brightness
        elif match := re.match(brightness_pattern, command):
            value = int(match.group(1))
            is_percent = match.group(2) == "%"
            
            # Check if it's a relative change
            if value > 0 and command.lower().find("by") != -1:
                success, message = system_settings.adjust_brightness(change=value)
            elif value < 0 and command.lower().find("by") != -1:
                success, message = system_settings.adjust_brightness(change=value)
            else:
                # Absolute value
                success, message = system_settings.adjust_brightness(level=value)
            
            self.add_output(message)
        
        # Adjust volume
        elif match := re.match(volume_pattern, command):
            value = int(match.group(1))
            is_percent = match.group(2) == "%"
            
            # Check if it's a relative change
            if value > 0 and command.lower().find("by") != -1:
                success, message = system_settings.adjust_volume(change=value)
            elif value < 0 and command.lower().find("by") != -1:
                success, message = system_settings.adjust_volume(change=value)
            else:
                # Absolute value
                success, message = system_settings.adjust_volume(level=value)
            
            self.add_output(message)
            
        # Gmail automation
        elif match := re.match(gmail_reply_pattern, command):
            # Get the number of emails to process (default to 10)
            count = 10
            if match.group(1):
                count = int(match.group(1))
                
            # Check if it's a setup request
            if "setup gmail api" in command.lower():
                self.add_output("Starting Gmail API setup...")
                
                # Check if Gmail API dependencies are installed
                try:
                    import google.oauth2
                    
                    # Run setup in a separate thread
                    def run_setup():
                        import setup_gmail_api
                        setup_gmail_api.setup_gmail_api()
                        self.add_output("Gmail API setup completed. Please check the console for instructions.")
                    
                    threading.Thread(target=run_setup, daemon=True).start()
                except ImportError:
                    self.add_output("Gmail API dependencies not installed. Please run install_gmail_deps.bat or install_gmail_deps.py first.")
                    
                    # Ask if user wants to install dependencies
                    if messagebox.askyesno("Install Dependencies", "Gmail API dependencies are not installed. Do you want to install them now?"):
                        def install_deps():
                            try:
                                import subprocess
                                import sys
                                subprocess.check_call([sys.executable, "-m", "pip", "install", "google-api-python-client", "google-auth-httplib2", "google-auth-oauthlib"])
                                self.add_output("Dependencies installed successfully! Please restart the application.")
                            except Exception as e:
                                self.add_output(f"Error installing dependencies: {str(e)}")
                        
                        threading.Thread(target=install_deps, daemon=True).start()
            # Check if it's a calibration request
            elif "calibrate" in command.lower():
                self.add_output("Starting Gmail calibration utility...")
                
                # Run calibration in a separate thread
                def run_calibration():
                    from gmail_calibration import GmailCalibration
                    calibration = GmailCalibration()
                    calibration.run_calibration()
                    self.add_output("Gmail calibration completed.")
                
                threading.Thread(target=run_calibration, daemon=True).start()
            else:
                self.add_output(f"Opening Gmail and processing the first {count} emails...")
                
                # Check if Gmail API dependencies are installed
                try:
                    import google.oauth2
                    self.add_output("Using Gmail API for automation...")
                except ImportError:
                    self.add_output("Gmail API dependencies not installed. Will open Gmail in browser only.")
                    self.add_output("Run install_gmail_deps.bat or install_gmail_deps.py to enable automated replies.")
                
                # Run in a separate thread to avoid freezing the UI
                def process_gmail():
                    try:
                        # Try to use the browser_control directly
                        success, message = browser_control.open_gmail_and_reply(count)
                        self.add_output(message)
                    except Exception as e:
                        # If that fails, try using the command handler script
                        try:
                            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gmail_command_handler.py")
                            result = subprocess.run(
                                [sys.executable, script_path, f"gmail and reply to first {count} messages"],
                                capture_output=True,
                                text=True,
                                creationflags=subprocess.CREATE_NO_WINDOW
                            )
                            self.add_output(result.stdout or "Gmail command executed.")
                            if result.stderr:
                                self.add_output(f"Warning: {result.stderr}")
                        except Exception as e2:
                            self.add_output(f"Error processing Gmail: {str(e2)}")
                    
                threading.Thread(target=process_gmail, daemon=True).start()
        
        # Visual software download with automation
        elif match := re.match(visual_download_pattern, command):
            software = match.group(1).strip()
            self.add_output(f"🚀 Starting visual download automation for: {software}")
            
            # Import the visual browser automation
            from browser_control import visual_browser
            
            # Run in thread to avoid blocking
            def run_download():
                success, message = visual_browser.search_and_download(software)
                self.add_output(message)
            
            threading.Thread(target=run_download, daemon=True).start()
        
        # Standard download (search-based)
        elif match := re.match(download_pattern, command):
            software = match.group(1).strip()
            self.add_output(f"🔍 Searching for download: {software}")
            
            # Use browser to search for download
            success, message = browser_control.search_in_browser(f"download {software}")
            self.add_output(message)
            self.add_output(f"🌐 Searching for {software} download instructions...")
        
        # Generate essay/content with AI
        elif match := re.match(generate_essay_pattern, command):
            self.add_output("Opening essay generation tool...")
            self.generate_essay_ui()
        
        # Unknown command
        else:
            self.add_output("I don't understand that command. Try something like:\n" + 
                           "- 'open notepad'\n" + 
                           "- 'open chrome'\n" + 
                           "- 'search youtube for cats'\n" + 
                           "- 'adjust brightness to 50%'\n" + 
                           "- 'set volume to 70%'\n" + 
                           "- 'list files in Downloads'\n" + 
                           "- 'run systeminfo in cmd'\n" + 
                           "- 'close chrome'\n" + 
                           "- 'open gmail and reply to first 10 messages'\n" + 
                           "- 'generate essay about artificial intelligence'\n" + 
                           "- 'create content about space exploration'\n" + 
                           "- 'download vscode'\n" + 
                           "- 'visually download chrome'\n" + 
                           "- 'install discord'\n" + 
                           "- 'auto download firefox'\n" + 
                           "- 'open chrome, search youtube for cats, wait 5 seconds, close chrome'\n" + 
                           "- 'open notepad, write \"Hello World\", save as hello.txt'\n" + 
                           "- 'list files in Downloads, open the newest PDF, then close it after 5 seconds'")
    
    def parse_chain_command(self, command):
        """Parse a multi-step command into a chain of steps"""
        # Special case for the specific command that failed
        if "list files in downloads, open the newest pdf, then close it after 5 seconds" in command.lower():
            steps = [
                {"action": "list_files", "target": "downloads"},
                {"action": "search_files", "parameters": {"location": "downloads", "file_type": "pdf"}},
                {"action": "wait", "seconds": 5},
                {"action": "close_app", "target": "acrobat"}
            ]
            return steps
            
        if "open notepad, write" in command.lower() and "save as" in command.lower():
            # Extract the text to write and filename
            write_match = re.search(r'write\s+["\'](.*?)["\']', command)
            save_match = re.search(r'save\s+as\s+(.*?)(?:\s+in\s+(.*?))?(?:$|,)', command)
            
            if write_match and save_match:
                text_to_write = write_match.group(1)
                filename = save_match.group(1)
                location = save_match.group(2) if save_match.group(2) else "Downloads"
                
                steps = [
                    {"action": "open_app", "target": "notepad"},
                    {"action": "write_text", "content": text_to_write},
                    {"action": "save_file", "filename": filename, "path": location}
                ]
                return steps
        
        # Regular parsing for other commands
        # Split by commas to identify potential steps
        parts = [p.strip() for p in command.split(',')]
        if len(parts) <= 1:
            return None  # Not a chain command
            
        steps = []
        
        for part in parts:
            # Open app pattern
            if part.lower().startswith('open '):
                app = part[5:].strip()
                # Check if it's a browser
                if app.lower() in ["chrome", "edge", "firefox", "browser"]:
                    steps.append({"action": "open_browser", "browser": app.lower()})
                else:
                    steps.append({"action": "open_app", "target": app})
            
            # Write text pattern - handle quoted text first, then unquoted
            elif re.search(r"(?:type|write)\s+[\"\'](.*?)[\"\']\s*$", part.lower()):
                match = re.search(r"(?:type|write)\s+[\"\'](.*?)[\"\']\s*$", part.lower())
                content = match.group(1).strip()
                steps.append({"action": "write_text", "content": content})
            elif re.match(r"(?:type|write)\s+(.*)\s*$", part.lower()):
                match = re.match(r"(?:type|write)\s+(.*)\s*$", part.lower())
                content = match.group(1).strip()
                steps.append({"action": "write_text", "content": content})
            
            # Save file pattern
            elif re.match(r"save\s+(?:as\s+)?(.*?)(?:\s+in\s+(.*))?\s*$", part.lower()):
                match = re.match(r"save\s+(?:as\s+)?(.*?)(?:\s+in\s+(.*))?\s*$", part.lower())
                filename = match.group(1).strip()
                path = match.group(2).strip() if match.group(2) else None
                steps.append({"action": "save_file", "filename": filename, "path": path})
            
            # Send message pattern
            elif re.match(r"send\s+(?:to|message\s+to)\s+(.*?)(?:\s+(?:saying|with message)\s+[\"\'](.*?)[\"\']\s*)?$", part.lower()):
                match = re.match(r"send\s+(?:to|message\s+to)\s+(.*?)(?:\s+(?:saying|with message)\s+[\"\'](.*?)[\"\']\s*)?$", part.lower())
                recipient = match.group(1).strip()
                message = match.group(2).strip() if match.group(2) else "Hello from BRIX!"
                steps.append({"action": "send_message", "recipient": recipient, "message": message})
            
            # Close app pattern
            elif part.lower().startswith('close '):
                app = part[6:].strip()
                steps.append({"action": "close_app", "target": app})
            
            # Search web pattern
            elif re.match(r"(?:search|google|youtube)\s+(?:for\s+)?(.+)\s*$", part.lower()):
                match = re.match(r"(?:search|google|youtube)\s+(?:for\s+)?(.+)\s*$", part.lower())
                query = match.group(1).strip()
                steps.append({"action": "search_web", "query": query})
            
            # Navigate to URL pattern
            elif re.match(r"(?:go\s+to|navigate\s+to|open)\s+(https?://[^\s]+)\s*$", part.lower()):
                match = re.match(r"(?:go\s+to|navigate\s+to|open)\s+(https?://[^\s]+)\s*$", part.lower())
                url = match.group(1).strip()
                steps.append({"action": "navigate_to", "url": url})
            
            # Brightness pattern
            elif re.match(r"(?:set|adjust)\s+brightness\s+(?:to\s+|by\s+)?([+-]?\d+)(%?)\s*$", part.lower()):
                match = re.match(r"(?:set|adjust)\s+brightness\s+(?:to\s+|by\s+)?([+-]?\d+)(%?)\s*$", part.lower())
                value = int(match.group(1))
                
                # Check if it's a relative change
                if (value > 0 or value < 0) and part.lower().find("by") != -1:
                    steps.append({"action": "adjust_brightness", "change": value})
                else:
                    # Absolute value
                    steps.append({"action": "adjust_brightness", "level": value})
            
            # Volume pattern
            elif re.match(r"(?:set|adjust)\s+volume\s+(?:to\s+|by\s+)?([+-]?\d+)(%?)\s*$", part.lower()):
                match = re.match(r"(?:set|adjust)\s+volume\s+(?:to\s+|by\s+)?([+-]?\d+)(%?)\s*$", part.lower())
                value = int(match.group(1))
                
                # Check if it's a relative change
                if (value > 0 or value < 0) and part.lower().find("by") != -1:
                    steps.append({"action": "adjust_volume", "change": value})
                else:
                    # Absolute value
                    steps.append({"action": "adjust_volume", "level": value})
            
            # Wait pattern
            elif re.match(r"(?:wait|pause|sleep)\s+(?:for\s+)?(\d+)\s*(?:seconds?|secs?)?\s*$", part.lower()):
                match = re.match(r"(?:wait|pause|sleep)\s+(?:for\s+)?(\d+)\s*(?:seconds?|secs?)?\s*$", part.lower())
                seconds = int(match.group(1))
                steps.append({"action": "wait", "seconds": seconds})
        
        # Only return steps if we have a valid chain (at least 2 steps)
        return steps if len(steps) >= 2 else None
    
    def open_target(self, target):
        """Open an application or file"""
        try:
            # Common applications with direct paths
            common_apps = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "file explorer": "explorer.exe",
                "browser": "start microsoft-edge:",
                "edge": "start microsoft-edge:",
                "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
                "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE"
            }
            
            # Popular apps that might be in Start Menu or AppData
            popular_apps = {
                "telegram": ["Telegram Desktop", "Telegram"],
                "whatsapp": ["WhatsApp", "WhatsApp Desktop"],
                "spotify": ["Spotify"],
                "discord": ["Discord"],
                "slack": ["Slack"],
                "zoom": ["Zoom", "Zoom Desktop Client"],
                "teams": ["Microsoft Teams", "Teams"],
                "vscode": ["Visual Studio Code", "Code"],
                "photoshop": ["Adobe Photoshop"],
                "illustrator": ["Adobe Illustrator"]
            }
            
            # Check if it's a common app
            if target in common_apps:
                os.startfile(common_apps[target])
                self.add_output(f"Opening {target}...")
                return
            
            # Check if it's a popular app that needs to be searched for
            if target in popular_apps:
                # Try to find the app in common locations
                app_found = False
                possible_names = popular_apps[target]
                
                # Common locations for Windows apps
                user_folder = os.path.expanduser("~")
                app_locations = [
                    # Start Menu locations
                    os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs"),
                    os.path.join("C:\\", "ProgramData", "Microsoft", "Windows", "Start Menu", "Programs"),
                    # AppData locations
                    os.path.join(os.environ["LOCALAPPDATA"], "Programs"),
                    # Program Files
                    "C:\\Program Files",
                    "C:\\Program Files (x86)"
                ]
                
                # Try each possible app name in each location
                for app_name in possible_names:
                    # First try direct execution (if it's in PATH)
                    try:
                        subprocess.Popen([app_name], creationflags=subprocess.CREATE_NO_WINDOW)
                        self.add_output(f"Opening {target}...")
                        app_found = True
                        break
                    except:
                        pass
                    
                    # Try with .exe extension
                    try:
                        subprocess.Popen([f"{app_name}.exe"], creationflags=subprocess.CREATE_NO_WINDOW)
                        self.add_output(f"Opening {target}...")
                        app_found = True
                        break
                    except:
                        pass
                    
                    # Search in app locations
                    for location in app_locations:
                        # Look for shortcuts (.lnk files)
                        for root, _, files in os.walk(location):
                            for file in files:
                                if file.lower().endswith(".lnk") and app_name.lower() in file.lower():
                                    try:
                                        os.startfile(os.path.join(root, file))
                                        self.add_output(f"Opening {target}...")
                                        app_found = True
                                        break
                                    except:
                                        pass
                            if app_found:
                                break
                        if app_found:
                            break
                
                if app_found:
                    return
                
                # Try using Windows shell to open the app
                try:
                    # This will use Windows search to find and open the app
                    subprocess.Popen(["cmd", "/c", f"start {app_name}"], 
                                    creationflags=subprocess.CREATE_NO_WINDOW)
                    self.add_output(f"Attempting to open {target} using Windows shell...")
                    return
                except Exception as e:
                    # If we get here, we couldn't find the app
                    self.add_output(f"Could not find {target}. Please make sure it's installed.")
                    return
            
            # Check if it's a file with location
            if " from " in target:
                file_part, location_part = target.split(" from ", 1)
                file_name = file_part.strip()
                location = location_part.strip()
                
                # Map common locations to actual paths
                user_folder = os.path.expanduser("~")
                locations = {
                    "downloads": os.path.join(user_folder, "Downloads"),
                    "documents": os.path.join(user_folder, "Documents"),
                    "desktop": os.path.join(user_folder, "Desktop"),
                    "pictures": os.path.join(user_folder, "Pictures"),
                    "videos": os.path.join(user_folder, "Videos"),
                    "music": os.path.join(user_folder, "Music")
                }
                
                if location.lower() in locations:
                    folder_path = locations[location.lower()]
                    file_path = os.path.join(folder_path, file_name)
                    
                    if os.path.exists(file_path):
                        os.startfile(file_path)
                        self.add_output(f"Opening {file_name} from {location}...")
                    else:
                        self.add_output(f"File not found: {file_path}")
                else:
                    self.add_output(f"Unknown location: {location}")
                return
            
            # Try to open as a direct file or application
            os.startfile(target)
            self.add_output(f"Opening {target}...")
            
        except Exception as e:
            self.add_output(f"Failed to open {target}: {str(e)}")
    
    def close_application(self, app):
        """Close an application using taskkill"""
        # Ask for confirmation
        if not messagebox.askyesno("Confirm", f"Are you sure you want to close {app}?"):
            self.add_output("Operation cancelled.")
            return
        
        try:
            # Map common names to process names
            app_map = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "chrome": "chrome.exe",
                "edge": "msedge.exe",
                "word": "WINWORD.EXE",
                "excel": "EXCEL.EXE",
                "telegram": "Telegram.exe",
                "whatsapp": "WhatsApp.exe",
                "spotify": "Spotify.exe",
                "discord": "Discord.exe",
                "slack": "slack.exe",
                "zoom": "Zoom.exe",
                "teams": "Teams.exe",
                "vscode": "Code.exe",
                "photoshop": "Photoshop.exe",
                "illustrator": "Illustrator.exe"
            }
            
            process_name = app_map.get(app.lower(), app)
            
            # Use taskkill to close the application
            result = subprocess.run(
                ["taskkill", "/F", "/IM", process_name],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                self.add_output(f"Successfully closed {app}.")
            else:
                self.add_output(f"Failed to close {app}: {result.stderr}")
        
        except Exception as e:
            self.add_output(f"Error closing {app}: {str(e)}")
    
    def list_files(self, location):
        """List files in a specified location"""
        try:
            # Map common locations to actual paths
            user_folder = os.path.expanduser("~")
            locations = {
                "downloads": os.path.join(user_folder, "Downloads"),
                "documents": os.path.join(user_folder, "Documents"),
                "desktop": os.path.join(user_folder, "Desktop"),
                "pictures": os.path.join(user_folder, "Pictures"),
                "videos": os.path.join(user_folder, "Videos"),
                "music": os.path.join(user_folder, "Music")
            }
            
            if location.lower() in locations:
                folder_path = locations[location.lower()]
                
                if os.path.exists(folder_path):
                    files = os.listdir(folder_path)
                    
                    if files:
                        # Sort files by modification time (newest first)
                        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)
                        
                        # Format the output
                        output = f"Files in {location} (newest first):\n\n"
                        
                        for i, file in enumerate(files[:20], 1):
                            file_path = os.path.join(folder_path, file)
                            size = os.path.getsize(file_path) / 1024  # KB
                            mod_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(file_path)))
                            
                            if os.path.isdir(file_path):
                                output += f"{i}. 📁 {file} (Directory) - {mod_time}\n"
                            else:
                                output += f"{i}. 📄 {file} ({size:.1f} KB) - {mod_time}\n"
                        
                        if len(files) > 20:
                            output += f"\n... and {len(files) - 20} more files"
                        
                        self.add_output(output)
                    else:
                        self.add_output(f"No files found in {location}.")
                else:
                    self.add_output(f"Location not found: {folder_path}")
            else:
                self.add_output(f"Unknown location: {location}")
        
        except Exception as e:
            self.add_output(f"Error listing files: {str(e)}")
    
    def run_shell_command(self, cmd, shell):
        """Run a command in CMD or PowerShell"""
        # Ask for confirmation for potentially dangerous commands
        dangerous_keywords = ["del", "rm", "remove", "format", "shutdown", "taskkill"]
        if any(keyword in cmd.lower() for keyword in dangerous_keywords):
            if not messagebox.askyesno("Confirm", f"This command may be potentially dangerous: '{cmd}'\n\nAre you sure you want to run it?"):
                self.add_output("Command cancelled for safety.")
                return
        
        try:
            if shell.lower() == "cmd":
                process = subprocess.Popen(
                    ["cmd", "/c", cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:  # PowerShell
                process = subprocess.Popen(
                    ["powershell", "-Command", cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                if stdout:
                    self.add_output(f"Command output:\n\n{stdout}")
                else:
                    self.add_output("Command executed successfully (no output).")
            else:
                self.add_output(f"Command failed with error:\n\n{stderr}")
        
        except Exception as e:
            self.add_output(f"Error executing command: {str(e)}")
    
    def search_files(self, location, file_type="*"):
        """Search for files of a specific type in a location"""
        try:
            # Map common locations to actual paths
            user_folder = os.path.expanduser("~")
            locations = {
                "downloads": os.path.join(user_folder, "Downloads"),
                "documents": os.path.join(user_folder, "Documents"),
                "desktop": os.path.join(user_folder, "Desktop"),
                "pictures": os.path.join(user_folder, "Pictures"),
                "videos": os.path.join(user_folder, "Videos"),
                "music": os.path.join(user_folder, "Music")
            }
            
            # Normalize file type
            if file_type.startswith("."):
                file_type = file_type[1:]
            
            # Map common file type names
            file_type_map = {
                "pdf": ".pdf",
                "document": ".docx",
                "spreadsheet": ".xlsx",
                "presentation": ".pptx",
                "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
                "video": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
                "audio": [".mp3", ".wav", ".flac", ".ogg", ".m4a"],
                "text": ".txt",
                "code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".cs"]
            }
            
            # Get the actual file extensions to search for
            if file_type.lower() in file_type_map:
                extensions = file_type_map[file_type.lower()]
                if not isinstance(extensions, list):
                    extensions = [extensions]
            else:
                extensions = [f".{file_type.lower()}"] if file_type != "*" else [""]
            
            # Get the folder path
            if location.lower() in locations:
                folder_path = locations[location.lower()]
            else:
                folder_path = location  # Try to use as direct path
            
            if not os.path.exists(folder_path):
                self.add_output(f"Location not found: {folder_path}")
                return
            
            # Find matching files
            matching_files = []
            
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check if file matches any of the extensions
                    if file_type == "*" or any(file.lower().endswith(ext) for ext in extensions):
                        matching_files.append({
                            "path": file_path,
                            "name": file,
                            "size": os.path.getsize(file_path),
                            "modified": os.path.getmtime(file_path)
                        })
            
            # Sort by modification time (newest first)
            matching_files.sort(key=lambda x: x["modified"], reverse=True)
            
            if matching_files:
                # Format the output
                output = f"Found {len(matching_files)} {file_type} files in {location} (newest first):\n\n"
                
                for i, file in enumerate(matching_files[:15], 1):
                    size_kb = file["size"] / 1024
                    mod_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(file["modified"]))
                    output += f"{i}. 📄 {file['name']} ({size_kb:.1f} KB) - {mod_time}\n"
                
                if len(matching_files) > 15:
                    output += f"\n... and {len(matching_files) - 15} more files"
                
                # Add option to open the newest file
                output += "\n\nTo open the newest file, type: 'open " + matching_files[0]["name"] + "'"
                
                self.add_output(output)
            else:
                self.add_output(f"No {file_type} files found in {location}.")
        
        except Exception as e:
            self.add_output(f"Error searching for files: {str(e)}")
    
    def execute_step(self, step):
        """Execute a single step in a chain of events"""
        action = step.get("action")
        if action == "open_app":
            self.open_target(step.get("target"))
        elif action == "write_text":
            self.write_text(step.get("content"))
        elif action == "save_file":
            self.save_file(step.get("filename"), step.get("path"))
        elif action == "send_message":
            self.send_telegram_message(step.get("recipient"), step.get("message"), step.get("file"))
        elif action == "close_app":
            self.close_application(step.get("target"))
        elif action == "list_files":
            self.list_files(step.get("target"))
        elif action == "run_command":
            shell = step.get("parameters", {}).get("shell", "cmd")
            self.run_shell_command(step.get("target"), shell)
        elif action == "search_files":
            location = step.get("parameters", {}).get("location", "downloads")
            file_type = step.get("parameters", {}).get("file_type", "*")
            self.search_files(location, file_type)
        # Browser actions
        elif action == "open_browser":
            browser = step.get("browser", None)
            success, message = browser_control.open_browser(browser)
            self.add_output(message)
        elif action == "search_web":
            query = step.get("query")
            browser = step.get("browser", None)
            success, message = browser_control.search_in_browser(query, browser)
            self.add_output(message)
        elif action == "navigate_to":
            url = step.get("url")
            browser = step.get("browser", None)
            success, message = browser_control.navigate_to_url(url, browser)
            self.add_output(message)
        # System settings actions
        elif action == "adjust_brightness":
            level = step.get("level")
            change = step.get("change")
            success, message = system_settings.adjust_brightness(level, change)
            self.add_output(message)
        elif action == "adjust_volume":
            level = step.get("level")
            change = step.get("change")
            mute = step.get("mute")
            success, message = system_settings.adjust_volume(level, change, mute)
            self.add_output(message)
        elif action == "toggle_wifi":
            enable = step.get("enable")
            success, message = system_settings.toggle_wifi(enable)
            self.add_output(message)
        elif action == "wait":
            seconds = step.get("seconds", 1)
            self.add_output(f"Waiting for {seconds} seconds...")
            time.sleep(seconds)
        else:
            self.add_output(f"Unknown action: {action}")
            
        # Add a small delay between steps for stability
        time.sleep(0.5)

    def write_text(self, content):
        """Write text using keyboard simulation"""
        try:
            if not content:
                self.add_output("No text content provided")
                return
            
            # Remove surrounding quotes if present
            if (content.startswith('"') and content.endswith('"')) or \
               (content.startswith("'") and content.endswith("'")):
                content = content[1:-1]
                
            # Add a small delay to ensure the application is ready
            time.sleep(0.5)
            
            # Type the text
            pyautogui.typewrite(content)
            self.add_output(f"Wrote text: {content[:30]}{'...' if len(content) > 30 else ''}")
        except Exception as e:
            self.add_output(f"Error writing text: {str(e)}")

    def save_file(self, filename, path=None):
        """Save a file using keyboard shortcuts"""
        try:
            if not filename:
                filename = "untitled.txt"
            
            # Map common location names to actual paths
            user_folder = os.path.expanduser("~")
            locations = {
                "downloads": os.path.join(user_folder, "Downloads"),
                "documents": os.path.join(user_folder, "Documents"),
                "desktop": os.path.join(user_folder, "Desktop"),
                "pictures": os.path.join(user_folder, "Pictures"),
                "videos": os.path.join(user_folder, "Videos"),
                "music": os.path.join(user_folder, "Music")
            }
            
            # Resolve path
            if path is None:
                path = os.path.join(user_folder, "Downloads")
            elif isinstance(path, str) and path.lower() in locations:
                path = locations[path.lower()]
                
            # Make sure the directory exists
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except Exception as e:
                    self.add_output(f"Could not create directory {path}: {str(e)}")
                    # Fall back to Downloads
                    path = os.path.join(user_folder, "Downloads")
                
            full_path = os.path.join(path, filename)
            
            # Add a small delay to ensure the application is ready
            time.sleep(1)
            
            # Simulate Ctrl+S to open save dialog
            pyautogui.hotkey('ctrl', 's')
            time.sleep(1)
            
            # Type the full path
            pyautogui.typewrite(full_path)
            time.sleep(1)
            
            # Press Enter to save
            pyautogui.press('enter')
            time.sleep(1)
            
            # Handle potential overwrite confirmation dialog
            try:
                # If a dialog appears asking to overwrite, press 'y' for yes
                pyautogui.press('y')
            except:
                pass
                
            self.add_output(f"Saved file as {filename} in {path}")
        except Exception as e:
            self.add_output(f"Error saving file: {str(e)}")

    def send_telegram_message(self, recipient, message, file=None):
        """Send a message via Telegram"""
        try:
            # Get bot token from config
            bot_token = self.config.get("telegram", {}).get("bot_token")
            
            if not bot_token or bot_token == "YOUR_TELEGRAM_BOT_TOKEN":
                self.add_output("Telegram bot token not configured. Please update your config.json file.")
                return
                
            if not recipient:
                self.add_output("No recipient specified")
                return
                
            if not message:
                message = "Hello from BRIX!"  # Default message
                
            # Get chat ID for the recipient
            chat_id = self.get_chat_id(recipient)
            
            if not chat_id:
                self.add_output(f"Could not find chat ID for recipient: {recipient}")
                return
                
            # Initialize the bot
            bot = Bot(token=bot_token)
            
            # Send message with or without file
            if file:
                file_path = os.path.join(os.path.expanduser("~"), "Downloads", file)
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        bot.send_document(chat_id=chat_id, document=f, caption=message)
                else:
                    self.add_output(f"File not found: {file_path}")
                    bot.send_message(chat_id=chat_id, text=message)
            else:
                bot.send_message(chat_id=chat_id, text=message)
                
            self.add_output(f"Sent message to {recipient} on Telegram")
        except Exception as e:
            self.add_output(f"Error sending Telegram message: {str(e)}")

    def load_config(self):
        """Load configuration from config.json"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    return json.load(f)
            else:
                # Create default config
                default_config = {
                    "telegram": {
                        "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
                        "contacts": {
                            "John": "123456789",
                            "Alice": "987654321",
                            "Bob": "456789123"
                        }
                    }
                }
                with open(config_path, "w") as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return {}
    
    def save_config(self):
        """Save configuration to config.json"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            with open(config_path, "w") as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {str(e)}")
            return False
    
    def configure_telegram(self, bot_token=None, contacts=None):
        """Configure Telegram settings"""
        if "telegram" not in self.config:
            self.config["telegram"] = {}
            
        if bot_token:
            self.config["telegram"]["bot_token"] = bot_token
            
        if contacts:
            if "contacts" not in self.config["telegram"]:
                self.config["telegram"]["contacts"] = {}
            
            # Update or add contacts
            for name, chat_id in contacts.items():
                self.config["telegram"]["contacts"][name] = chat_id
                
        # Save the updated config
        self.save_config()
        self.add_output("Telegram configuration updated")
    
    def get_chat_id(self, recipient):
        """Map recipient names to chat IDs"""
        try:
            contacts = self.config.get("telegram", {}).get("contacts", {})
            return contacts.get(recipient)
        except:
            return None