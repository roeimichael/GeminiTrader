import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from dotenv import load_dotenv
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.tradingagents.agent_pool import AgentRegistry, AgentPool
from src.tradingagents.config import DEFAULT_CONFIG

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

        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg=self.bg_dark)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title = tk.Label(
            main_frame,
            text="GeminiTrader - Agent Pool Manager",
            font=("Arial", 24, "bold"),
            bg=self.bg_dark,
            fg=self.fg_light
        )
        title.pack(pady=(0, 20))

        content_frame = tk.Frame(main_frame, bg=self.bg_dark)
        content_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(content_frame, bg=self.bg_medium, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)

        right_frame = tk.Frame(content_frame, bg=self.bg_medium)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)

        button_frame = tk.Frame(main_frame, bg=self.bg_dark)
        button_frame.pack(fill=tk.X, pady=(20, 0))

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

            messagebox.showinfo(
                "Success",
                f"Initialized {count} agents!\n\nPool is ready for analysis."
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


def main():
    root = tk.Tk()
    app = AgentSelectorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
