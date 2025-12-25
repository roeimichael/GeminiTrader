import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from dotenv import load_dotenv
from datetime import datetime
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tradingagents.agent_pool import AgentRegistry, AgentPool
from tradingagents.config import DEFAULT_CONFIG
from tradingagents.conversation_manager import ConversationManager

class AgentSelectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GeminiTrader - Agent Selector")
        self.root.geometry("1200x800")

        load_dotenv()

        self.bg_dark = "#1e1e1e"
        self.bg_medium = "#2d2d2d"
        self.bg_light = "#3d3d3d"
        self.fg_light = "#e0e0e0"
        self.accent = "#4a9eff"

        self.root.configure(bg=self.bg_dark)

        self.registry = AgentRegistry()
        self.pool = None
        self.conversation_manager = None

        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg=self.bg_dark)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title = tk.Label(
            main_frame,
            text="GeminiTrader - Multi-Agent Trading System",
            font=("Arial", 24, "bold"),
            bg=self.bg_dark,
            fg=self.fg_light
        )
        title.pack(pady=(0, 20))

        # Create notebook for tabs
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=self.bg_dark, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.bg_medium, foreground=self.fg_light,
                       padding=[20, 10], font=('Arial', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', self.accent)])

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Agent Pool Setup
        pool_tab = tk.Frame(self.notebook, bg=self.bg_dark)
        self.notebook.add(pool_tab, text="Agent Pool Setup")
        self.setup_pool_tab(pool_tab)

        # Tab 2: Conversation
        conversation_tab = tk.Frame(self.notebook, bg=self.bg_dark)
        self.notebook.add(conversation_tab, text="Conversation")
        self.setup_conversation_tab(conversation_tab)

    def setup_pool_tab(self, parent):
        """Setup the agent pool management tab"""
        content_frame = tk.Frame(parent, bg=self.bg_dark)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = tk.Frame(content_frame, bg=self.bg_medium, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)

        right_frame = tk.Frame(content_frame, bg=self.bg_medium)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)

        button_frame = tk.Frame(parent, bg=self.bg_dark)
        button_frame.pack(fill=tk.X, pady=(10, 0), padx=10)

        self.setup_buttons(button_frame)

    def setup_left_panel(self, parent):
        tk.Label(
            parent,
            text="Available Agents",
            font=("Arial", 16, "bold"),
            bg=self.bg_medium,
            fg=self.fg_light
        ).pack(pady=10)

        filter_frame = tk.Frame(parent, bg=self.bg_medium)
        filter_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(filter_frame, text="Category:", bg=self.bg_medium, fg=self.fg_light).pack(side=tk.LEFT)

        self.category_var = tk.StringVar(value="all")
        category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            values=["all", "analysts", "researchers", "managers", "risk_analysts", "trader"],
            state="readonly",
            width=15
        )
        category_combo.pack(side=tk.LEFT, padx=(5, 0))
        category_combo.bind("<<ComboboxSelected>>", lambda e: self.update_available_agents())

        list_frame = tk.Frame(parent, bg=self.bg_light)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.available_listbox = tk.Listbox(
            list_frame,
            bg=self.bg_light,
            fg=self.fg_light,
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10),
            borderwidth=0,
            highlightthickness=0
        )
        self.available_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.available_listbox.yview)

        self.available_listbox.bind("<Double-Button-1>", lambda e: self.add_selected_agent())

        btn_frame = tk.Frame(parent, bg=self.bg_medium)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        add_btn = tk.Button(
            btn_frame,
            text="Add to Pool →",
            command=self.add_selected_agent,
            bg=self.accent,
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2"
        )
        add_btn.pack(fill=tk.X)

        self.update_available_agents()

    def setup_right_panel(self, parent):
        tk.Label(
            parent,
            text="Active Agent Pool",
            font=("Arial", 16, "bold"),
            bg=self.bg_medium,
            fg=self.fg_light
        ).pack(pady=10)

        list_frame = tk.Frame(parent, bg=self.bg_light)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.active_listbox = tk.Listbox(
            list_frame,
            bg=self.bg_light,
            fg=self.fg_light,
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10),
            borderwidth=0,
            highlightthickness=0
        )
        self.active_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.active_listbox.yview)

        self.active_listbox.bind("<Double-Button-1>", lambda e: self.remove_selected_agent())

        btn_frame = tk.Frame(parent, bg=self.bg_medium)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        remove_btn = tk.Button(
            btn_frame,
            text="← Remove from Pool",
            command=self.remove_selected_agent,
            bg="#ff4444",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2"
        )
        remove_btn.pack(fill=tk.X)

        info_label = tk.Label(
            parent,
            text="Agent Info:",
            font=("Arial", 12, "bold"),
            bg=self.bg_medium,
            fg=self.fg_light
        )
        info_label.pack(padx=10, pady=(10, 5), anchor="w")

        self.info_text = scrolledtext.ScrolledText(
            parent,
            height=6,
            bg=self.bg_light,
            fg=self.fg_light,
            font=("Arial", 9),
            wrap=tk.WORD,
            borderwidth=0
        )
        self.info_text.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.active_listbox.bind("<<ListboxSelect>>", self.show_agent_info)

    def setup_buttons(self, parent):
        left_btns = tk.Frame(parent, bg=self.bg_dark)
        left_btns.pack(side=tk.LEFT)

        quick_setups = [
            ("Full Analysis", self.setup_full),
            ("Basic Analysis", self.setup_basic),
            ("Research Debate", self.setup_research)
        ]

        for text, command in quick_setups:
            btn = tk.Button(
                left_btns,
                text=text,
                command=command,
                bg=self.bg_medium,
                fg=self.fg_light,
                font=("Arial", 10),
                relief=tk.FLAT,
                cursor="hand2",
                padx=15,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=5)

        right_btns = tk.Frame(parent, bg=self.bg_dark)
        right_btns.pack(side=tk.RIGHT)

        actions = [
            ("Initialize Pool", self.initialize_pool, self.accent),
            ("Clear All", self.clear_all, "#ff4444"),
            ("Export Config", self.export_config, self.bg_medium),
            ("Import Config", self.import_config, self.bg_medium),
        ]

        for text, command, color in actions:
            btn = tk.Button(
                right_btns,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Arial", 10, "bold"),
                relief=tk.FLAT,
                cursor="hand2",
                padx=15,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=5)

    def update_available_agents(self):
        self.available_listbox.delete(0, tk.END)

        category = self.category_var.get()
        all_agents = self.registry.list_all_agents()

        for agent in all_agents:
            if category == "all" or agent["category"] == category:
                display = f"[{agent['category']}] {agent['name']}"
                self.available_listbox.insert(tk.END, display)
                self.available_listbox.itemconfig(tk.END, bg=self.bg_light, fg=self.fg_light)

    def add_selected_agent(self):
        selection = self.available_listbox.curselection()
        if not selection:
            return

        text = self.available_listbox.get(selection[0])
        category = text.split("]")[0].replace("[", "")

        all_agents = [a for a in self.registry.list_all_agents() if a["category"] == category]
        agent_name = text.split("] ")[1]
        agent = next((a for a in all_agents if a["name"] == agent_name), None)

        if agent:
            display = f"{agent['name']} ({agent['category']}:{agent['id']})"
            if display not in self.active_listbox.get(0, tk.END):
                self.active_listbox.insert(tk.END, display)
                self.active_listbox.itemconfig(tk.END, bg=self.bg_light, fg=self.fg_light)

    def remove_selected_agent(self):
        selection = self.active_listbox.curselection()
        if not selection:
            return

        self.active_listbox.delete(selection[0])

    def show_agent_info(self, event):
        selection = self.active_listbox.curselection()
        if not selection:
            return

        text = self.active_listbox.get(selection[0])
        parts = text.split("(")[1].split(")")[0].split(":")
        category = parts[0]
        agent_id = parts[1]

        agent_info = self.registry.get_agent_info(category, agent_id)

        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"Name: {agent_info['name']}\n\n")
        self.info_text.insert(tk.END, f"Category: {category}\n\n")
        self.info_text.insert(tk.END, f"Description: {agent_info['description']}\n\n")
        self.info_text.insert(tk.END, f"Requires Memory: {agent_info['requires_memory']}")

    def setup_full(self):
        self.active_listbox.delete(0, tk.END)
        agents = [
            ("analysts", "market"), ("analysts", "fundamentals"),
            ("analysts", "news"), ("analysts", "social"),
            ("researchers", "bull"), ("researchers", "bear"),
            ("managers", "research"),
            ("trader", "trader"),
            ("risk_analysts", "risky"), ("risk_analysts", "safe"), ("risk_analysts", "neutral"),
            ("managers", "risk")
        ]
        for cat, aid in agents:
            info = self.registry.get_agent_info(cat, aid)
            self.active_listbox.insert(tk.END, f"{info['name']} ({cat}:{aid})")

    def setup_basic(self):
        self.active_listbox.delete(0, tk.END)
        agents = [("analysts", "market"), ("analysts", "fundamentals")]
        for cat, aid in agents:
            info = self.registry.get_agent_info(cat, aid)
            self.active_listbox.insert(tk.END, f"{info['name']} ({cat}:{aid})")

    def setup_research(self):
        self.active_listbox.delete(0, tk.END)
        agents = [
            ("analysts", "market"), ("analysts", "fundamentals"),
            ("researchers", "bull"), ("researchers", "bear"),
            ("managers", "research")
        ]
        for cat, aid in agents:
            info = self.registry.get_agent_info(cat, aid)
            self.active_listbox.insert(tk.END, f"{info['name']} ({cat}:{aid})")

    def clear_all(self):
        self.active_listbox.delete(0, tk.END)
        if self.pool:
            self.pool.clear()

    def initialize_pool(self):
        try:
            self.pool = AgentPool(DEFAULT_CONFIG)

            count = self.active_listbox.size()
            if count == 0:
                messagebox.showwarning("No Agents", "Please add agents to the pool first")
                return

            for i in range(count):
                text = self.active_listbox.get(i)
                parts = text.split("(")[1].split(")")[0].split(":")
                category = parts[0]
                agent_id = parts[1]

                self.pool.add_agent(category, agent_id)

            # Create conversation manager
            self.conversation_manager = ConversationManager(self.pool)

            # Enable conversation tab
            self.send_button.config(state=tk.NORMAL)
            self.pool_status_label.config(
                text=f"✓ Pool initialized with {count} agents. Ready for conversation!",
                fg="#00ff88"
            )

            messagebox.showinfo(
                "Success",
                f"Initialized {count} agents!\n\nPool is ready for analysis and conversation."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize pool:\n{str(e)}")

    def export_config(self):
        count = self.active_listbox.size()
        if count == 0:
            messagebox.showwarning("No Agents", "No agents to export")
            return

        agents = []
        for i in range(count):
            text = self.active_listbox.get(i)
            parts = text.split("(")[1].split(")")[0].split(":")
            agents.append({"category": parts[0], "id": parts[1]})

        config = {"agents": agents}

        filename = "agent_config.json"
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)

        messagebox.showinfo("Exported", f"Configuration exported to {filename}")

    def import_config(self):
        filename = "agent_config.json"
        if not os.path.exists(filename):
            messagebox.showerror("Error", f"File not found: {filename}")
            return

        with open(filename, 'r') as f:
            config = json.load(f)

        self.active_listbox.delete(0, tk.END)

        for agent in config["agents"]:
            cat = agent["category"]
            aid = agent["id"]
            info = self.registry.get_agent_info(cat, aid)
            self.active_listbox.insert(tk.END, f"{info['name']} ({cat}:{aid})")

        messagebox.showinfo("Imported", f"Loaded {len(config['agents'])} agents")

    def setup_conversation_tab(self, parent):
        """Setup the conversation interface tab"""
        # Main container
        container = tk.Frame(parent, bg=self.bg_dark)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Status bar at top
        status_frame = tk.Frame(container, bg=self.bg_medium)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.pool_status_label = tk.Label(
            status_frame,
            text="⚠ Pool not initialized. Please initialize agents in the Pool Setup tab first.",
            font=("Arial", 10),
            bg=self.bg_medium,
            fg="#ff6b6b",
            padx=15,
            pady=10
        )
        self.pool_status_label.pack(fill=tk.X)

        # Conversation display area
        conversation_frame = tk.Frame(container, bg=self.bg_medium)
        conversation_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        tk.Label(
            conversation_frame,
            text="Conversation Output",
            font=("Arial", 14, "bold"),
            bg=self.bg_medium,
            fg=self.fg_light,
            anchor="w"
        ).pack(fill=tk.X, padx=10, pady=(10, 5))

        # Scrolled text for conversation output
        self.conversation_output = scrolledtext.ScrolledText(
            conversation_frame,
            bg=self.bg_light,
            fg=self.fg_light,
            font=("Consolas", 10),
            wrap=tk.WORD,
            borderwidth=0,
            padx=10,
            pady=10
        )
        self.conversation_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.conversation_output.config(state=tk.DISABLED)

        # Input frame
        input_frame = tk.Frame(container, bg=self.bg_medium)
        input_frame.pack(fill=tk.X)

        tk.Label(
            input_frame,
            text="Your Query:",
            font=("Arial", 12, "bold"),
            bg=self.bg_medium,
            fg=self.fg_light,
            anchor="w"
        ).pack(fill=tk.X, padx=10, pady=(10, 5))

        # Query input
        query_input_frame = tk.Frame(input_frame, bg=self.bg_medium)
        query_input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.query_input = tk.Text(
            query_input_frame,
            height=3,
            bg=self.bg_light,
            fg=self.fg_light,
            font=("Arial", 11),
            wrap=tk.WORD,
            borderwidth=0,
            padx=10,
            pady=10
        )
        self.query_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Optional context inputs
        context_frame = tk.Frame(input_frame, bg=self.bg_medium)
        context_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(
            context_frame,
            text="Context (Optional):",
            font=("Arial", 10),
            bg=self.bg_medium,
            fg=self.fg_light
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(
            context_frame,
            text="Ticker:",
            font=("Arial", 10),
            bg=self.bg_medium,
            fg=self.fg_light
        ).pack(side=tk.LEFT)

        self.ticker_input = tk.Entry(
            context_frame,
            bg=self.bg_light,
            fg=self.fg_light,
            font=("Arial", 10),
            width=10,
            borderwidth=0
        )
        self.ticker_input.pack(side=tk.LEFT, padx=(5, 15))

        tk.Label(
            context_frame,
            text="Date:",
            font=("Arial", 10),
            bg=self.bg_medium,
            fg=self.fg_light
        ).pack(side=tk.LEFT)

        self.date_input = tk.Entry(
            context_frame,
            bg=self.bg_light,
            fg=self.fg_light,
            font=("Arial", 10),
            width=12,
            borderwidth=0
        )
        self.date_input.pack(side=tk.LEFT, padx=(5, 0))
        self.date_input.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Action buttons
        button_frame = tk.Frame(input_frame, bg=self.bg_medium)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.send_button = tk.Button(
            button_frame,
            text="Send Query & Start Debate",
            command=self.send_query,
            bg=self.accent,
            fg="white",
            font=("Arial", 11, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=10
        )
        self.send_button.pack(side=tk.LEFT, padx=(0, 10))
        self.send_button.config(state=tk.DISABLED)

        clear_button = tk.Button(
            button_frame,
            text="Clear Output",
            command=self.clear_conversation,
            bg=self.bg_light,
            fg=self.fg_light,
            font=("Arial", 10),
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=10
        )
        clear_button.pack(side=tk.LEFT)

        # Example queries
        examples_frame = tk.Frame(input_frame, bg=self.bg_medium)
        examples_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(
            examples_frame,
            text="Example queries:",
            font=("Arial", 9, "italic"),
            bg=self.bg_medium,
            fg="#888",
            anchor="w"
        ).pack(fill=tk.X)

        example_text = """• "Should I invest in MSFT? They're releasing earnings next week."
• "What's your analysis of AAPL's current technical setup?"
• "Is now a good time to enter TSLA given recent price action?"
• "Compare the risk/reward of investing in tech vs energy sector"
"""
        tk.Label(
            examples_frame,
            text=example_text,
            font=("Arial", 9),
            bg=self.bg_medium,
            fg="#666",
            anchor="w",
            justify=tk.LEFT
        ).pack(fill=tk.X, padx=15)

    def send_query(self):
        """Send query to all agents and display conversation"""
        if not self.pool or not self.conversation_manager:
            messagebox.showerror("Error", "Please initialize the agent pool first!")
            return

        query = self.query_input.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a query first!")
            return

        # Get optional context
        context = {
            "ticker": self.ticker_input.get().strip().upper() if self.ticker_input.get().strip() else None,
            "date": self.date_input.get().strip() if self.date_input.get().strip() else None
        }

        # Disable button during processing
        self.send_button.config(state=tk.DISABLED, text="Processing...")
        self.root.update()

        try:
            # Send query to conversation manager
            result = self.conversation_manager.send_query_to_agents(query, context)

            # Display the conversation
            self.display_conversation(result)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

        finally:
            # Re-enable button
            self.send_button.config(state=tk.NORMAL, text="Send Query & Start Debate")

    def display_conversation(self, conversation: Dict[str, Any]):
        """Display the conversation results in the output area"""
        self.conversation_output.config(state=tk.NORMAL)
        self.conversation_output.delete("1.0", tk.END)

        # Header
        self.conversation_output.insert(tk.END, "=" * 80 + "\n", "header")
        self.conversation_output.insert(tk.END, "MULTI-AGENT ANALYSIS & DEBATE\n", "header")
        self.conversation_output.insert(tk.END, f"Timestamp: {conversation.get('timestamp', '')}\n", "header")
        self.conversation_output.insert(tk.END, "=" * 80 + "\n\n", "header")

        # Query
        self.conversation_output.insert(tk.END, "YOUR QUERY:\n", "section_header")
        self.conversation_output.insert(tk.END, f"{conversation['query']}\n\n", "query")

        # Context if provided
        if conversation.get('context') and any(conversation['context'].values()):
            self.conversation_output.insert(tk.END, "CONTEXT:\n", "section_header")
            ctx = conversation['context']
            if ctx.get('ticker'):
                self.conversation_output.insert(tk.END, f"  Ticker: {ctx['ticker']}\n", "context")
            if ctx.get('date'):
                self.conversation_output.insert(tk.END, f"  Date: {ctx['date']}\n", "context")
            self.conversation_output.insert(tk.END, "\n")

        # Individual Responses
        self.conversation_output.insert(tk.END, "\n" + "=" * 80 + "\n", "separator")
        self.conversation_output.insert(tk.END, "PHASE 1: INDIVIDUAL AGENT ANALYSES\n", "phase_header")
        self.conversation_output.insert(tk.END, "=" * 80 + "\n\n", "separator")

        for i, response in enumerate(conversation['individual_responses'], 1):
            self.conversation_output.insert(tk.END, f"\n[{i}] {response['agent'].upper()}\n", "agent_name")
            self.conversation_output.insert(tk.END, f"Role: {response['perspective']}\n", "role")
            self.conversation_output.insert(tk.END, "-" * 80 + "\n", "separator")
            self.conversation_output.insert(tk.END, f"{response['response']}\n", "response")

        # Debate
        self.conversation_output.insert(tk.END, "\n\n" + "=" * 80 + "\n", "separator")
        self.conversation_output.insert(tk.END, "PHASE 2: AGENT DEBATE & DISCUSSION\n", "phase_header")
        self.conversation_output.insert(tk.END, "=" * 80 + "\n\n", "separator")

        for debate_round in conversation['debate']:
            self.conversation_output.insert(tk.END, f"\nROUND {debate_round['round']}: {debate_round['topic'].upper()}\n", "debate_round")
            self.conversation_output.insert(tk.END, "-" * 80 + "\n", "separator")

            for exchange in debate_round['exchanges']:
                speaker = exchange.get('speaker', 'Unknown')
                self.conversation_output.insert(tk.END, f"\n[{speaker}]\n", "speaker")

                if 'agents' in exchange:
                    self.conversation_output.insert(tk.END, f"Agents: {', '.join(exchange['agents'])}\n", "agents")

                statement = exchange.get('statement', '')
                self.conversation_output.insert(tk.END, f"{statement}\n", "statement")

        # Final Verdict
        verdict = conversation['final_verdict']
        self.conversation_output.insert(tk.END, "\n\n" + "=" * 80 + "\n", "separator")
        self.conversation_output.insert(tk.END, "PHASE 3: FINAL CONSENSUS VERDICT\n", "phase_header")
        self.conversation_output.insert(tk.END, "=" * 80 + "\n\n", "separator")

        self.conversation_output.insert(tk.END, f"RECOMMENDATION: {verdict['overall_recommendation']}\n", "verdict")
        self.conversation_output.insert(tk.END, f"CONFIDENCE: {verdict['confidence_level']}\n\n", "confidence")

        # Sentiment breakdown
        sentiment = verdict['sentiment_breakdown']
        self.conversation_output.insert(tk.END, "SENTIMENT BREAKDOWN:\n", "section_header")
        self.conversation_output.insert(tk.END, f"  Bullish: {sentiment['bullish']} agents ({sentiment['bullish_percentage']}%)\n", "sentiment")
        self.conversation_output.insert(tk.END, f"  Bearish: {sentiment['bearish']} agents\n", "sentiment")
        self.conversation_output.insert(tk.END, f"  Neutral: {sentiment['neutral']} agents\n\n", "sentiment")

        # Key points
        self.conversation_output.insert(tk.END, "KEY POINTS:\n", "section_header")
        for point in verdict['key_points']:
            self.conversation_output.insert(tk.END, f"  • {point}\n", "bullet")
        self.conversation_output.insert(tk.END, "\n")

        # Action items
        self.conversation_output.insert(tk.END, "ACTION ITEMS:\n", "section_header")
        for item in verdict['action_items']:
            self.conversation_output.insert(tk.END, f"  ✓ {item}\n", "action")
        self.conversation_output.insert(tk.END, "\n")

        # Summary
        self.conversation_output.insert(tk.END, "SUMMARY:\n", "section_header")
        self.conversation_output.insert(tk.END, verdict['summary'] + "\n\n", "summary")

        self.conversation_output.insert(tk.END, "=" * 80 + "\n", "separator")

        # Configure tags for formatting
        self.conversation_output.tag_config("header", foreground="#4a9eff", font=("Arial", 11, "bold"))
        self.conversation_output.tag_config("section_header", foreground="#4a9eff", font=("Arial", 10, "bold"))
        self.conversation_output.tag_config("phase_header", foreground="#00ff88", font=("Arial", 12, "bold"))
        self.conversation_output.tag_config("agent_name", foreground="#ffd700", font=("Arial", 11, "bold"))
        self.conversation_output.tag_config("role", foreground="#aaa", font=("Arial", 9, "italic"))
        self.conversation_output.tag_config("debate_round", foreground="#ff6b6b", font=("Arial", 10, "bold"))
        self.conversation_output.tag_config("speaker", foreground="#ff9f43", font=("Arial", 10, "bold"))
        self.conversation_output.tag_config("verdict", foreground="#00ff88", font=("Arial", 13, "bold"))
        self.conversation_output.tag_config("confidence", foreground="#4a9eff", font=("Arial", 11))

        self.conversation_output.config(state=tk.DISABLED)
        self.conversation_output.see(tk.END)

    def clear_conversation(self):
        """Clear the conversation output"""
        self.conversation_output.config(state=tk.NORMAL)
        self.conversation_output.delete("1.0", tk.END)
        self.conversation_output.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = AgentSelectorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
