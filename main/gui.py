"""
gui.py

Tkinter GUI for BahtBuddy personal finance management system.
Provides a desktop interface to test all backend functions.

Created by Chirayu Sukhum (Tuey), October 14, 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import date
import json
import main


class BahtBuddyGUI:
    """Main GUI application for BahtBuddy."""
    
    def __init__(self, root):
        """
        Initialize the GUI application.
        
        Arguments:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("BahtBuddy - Personal Finance Manager")
        self.root.geometry("1000x750")
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_setup_tab()
        self.create_accounts_tab()
        self.create_transactions_tab()
        self.create_budget_tab()
        self.create_reports_tab()
        
        # Load accounts cache for dropdowns
        self.accounts_cache = []
        self.expense_accounts = []
    
    def create_setup_tab(self):
        """Create the setup/initialization tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='🚀 Setup')
        
        # Title
        title = ttk.Label(tab, text="Database Setup", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=20)
        
        # Info
        info_frame = ttk.Frame(tab)
        info_frame.pack(pady=10, padx=20, fill='x')
        
        info = ttk.Label(info_frame, text="📌 Step 1: Initialize database\n"
                                          "📌 Step 2: Load default accounts\n\n"
                                          "This will create Thai banking accounts, wallets,\n"
                                          "credit cards, and expense categories.",
                        justify='center')
        info.pack()
        
        # Buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Initialize Database",
                  command=self.init_database, width=20).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Load Default Accounts",
                  command=self.load_default_accounts, width=20).pack(side='left', padx=5)
        
        # Result display
        result_label = ttk.Label(tab, text="Results:", font=('Arial', 10, 'bold'))
        result_label.pack(pady=(20,5))
        
        self.setup_result = scrolledtext.ScrolledText(tab, height=15, width=90)
        self.setup_result.pack(pady=5, padx=20)
    
    def create_accounts_tab(self):
        """Create the accounts management tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='📊 Accounts')
        
        # Title
        title = ttk.Label(tab, text="Account Management", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=20)
        
        # View accounts button
        ttk.Button(tab, text="🔄 Refresh & View All Accounts",
                  command=self.view_accounts, width=30).pack(pady=10)
        
        # Opening balance section
        ob_frame = ttk.LabelFrame(tab, text="Set Opening Balance", padding=15)
        ob_frame.pack(pady=20, padx=20, fill='x')
        
        # Account dropdown
        ttk.Label(ob_frame, text="Account:").grid(row=0, column=0, sticky='w', pady=5)
        self.ob_account_combo = ttk.Combobox(ob_frame, width=40, state='readonly')
        self.ob_account_combo.grid(row=0, column=1, pady=5, padx=5, sticky='ew')
        
        ttk.Label(ob_frame, text="Amount:").grid(row=1, column=0, sticky='w', pady=5)
        self.ob_amount = ttk.Entry(ob_frame, width=20)
        self.ob_amount.grid(row=1, column=1, pady=5, padx=5, sticky='w')
        
        ttk.Label(ob_frame, text="Date (YYYY-MM-DD):").grid(row=2, column=0, sticky='w', pady=5)
        self.ob_date = ttk.Entry(ob_frame, width=20)
        self.ob_date.insert(0, str(date.today()))
        self.ob_date.grid(row=2, column=1, pady=5, padx=5, sticky='w')
        
        ob_frame.columnconfigure(1, weight=1)
        
        ttk.Button(ob_frame, text="Set Opening Balance",
                  command=self.set_opening_balance).grid(row=3, column=0, 
                                                         columnspan=2, pady=15)
        
        # Result display
        result_label = ttk.Label(tab, text="Results:", font=('Arial', 10, 'bold'))
        result_label.pack(pady=(10,5))
        
        self.accounts_result = scrolledtext.ScrolledText(tab, height=12, width=90)
        self.accounts_result.pack(pady=5, padx=20)
    
    def create_transactions_tab(self):
        """Create the transactions tab with different transaction types."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='💸 Transactions')
        
        # Title
        title = ttk.Label(tab, text="Record Transaction", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=15)
        
        # Transaction type selector
        type_frame = ttk.LabelFrame(tab, text="Transaction Type", padding=10)
        type_frame.pack(pady=10, padx=20, fill='x')
        
        self.txn_type = tk.StringVar(value="expense")
        
        types = [
            ("💰 Income (Receive Money)", "income"),
            ("💸 Expense (Spend Money)", "expense"),
            ("🔄 Transfer (Between Accounts)", "transfer")
        ]
        
        for text, value in types:
            ttk.Radiobutton(type_frame, text=text, variable=self.txn_type, 
                           value=value, command=self.update_transaction_labels).pack(
                           side='left', padx=20)
        
        # Transaction form
        form_frame = ttk.LabelFrame(tab, text="Transaction Details", padding=15)
        form_frame.pack(pady=10, padx=20, fill='x')
        
        # Date and Amount
        ttk.Label(form_frame, text="Date:").grid(row=0, column=0, sticky='w', pady=5)
        self.txn_date = ttk.Entry(form_frame, width=20)
        self.txn_date.insert(0, str(date.today()))
        self.txn_date.grid(row=0, column=1, pady=5, padx=5, sticky='w')
        
        ttk.Label(form_frame, text="Amount (฿):").grid(row=0, column=2, sticky='w', pady=5, padx=(20,0))
        self.txn_amount = ttk.Entry(form_frame, width=20)
        self.txn_amount.grid(row=0, column=3, pady=5, padx=5, sticky='w')
        
        # From account (Credit)
        self.txn_from_label = ttk.Label(form_frame, text="From Account:")
        self.txn_from_label.grid(row=1, column=0, sticky='w', pady=5)
        self.txn_credit_combo = ttk.Combobox(form_frame, width=40, state='readonly')
        self.txn_credit_combo.grid(row=1, column=1, columnspan=3, pady=5, padx=5, sticky='ew')
        
        # To account (Debit)
        self.txn_to_label = ttk.Label(form_frame, text="To Account:")
        self.txn_to_label.grid(row=2, column=0, sticky='w', pady=5)
        self.txn_debit_combo = ttk.Combobox(form_frame, width=40, state='readonly')
        self.txn_debit_combo.grid(row=2, column=1, columnspan=3, pady=5, padx=5, sticky='ew')
        
        # Notes
        ttk.Label(form_frame, text="Notes:").grid(row=3, column=0, sticky='w', pady=5)
        self.txn_notes = ttk.Entry(form_frame, width=60)
        self.txn_notes.grid(row=3, column=1, columnspan=3, pady=5, padx=5, sticky='ew')
        
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="📝 Record Transaction",
                  command=self.add_transaction, width=20).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📋 View All Transactions",
                  command=self.view_all_transactions, width=20).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Refresh Accounts",
                  command=self.refresh_transaction_dropdowns, width=20).pack(side='left', padx=5)
        
        # Result display
        result_label = ttk.Label(tab, text="Results:", font=('Arial', 10, 'bold'))
        result_label.pack(pady=(10,5))
        
        self.txn_result = scrolledtext.ScrolledText(tab, height=10, width=90)
        self.txn_result.pack(pady=5, padx=20)
    
    def create_budget_tab(self):
        """Create the budget management tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='📈 Budget')
        
        # Title
        title = ttk.Label(tab, text="Budget Management", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=20)
        
        # Budget form
        form_frame = ttk.LabelFrame(tab, text="Create/Update Budget", padding=15)
        form_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(form_frame, text="Period (YYYY-MM):").grid(row=0, column=0, sticky='w', pady=5)
        self.budget_period = ttk.Entry(form_frame, width=20)
        self.budget_period.insert(0, str(date.today())[:7])
        self.budget_period.grid(row=0, column=1, pady=5, padx=5, sticky='w')
        
        ttk.Label(form_frame, text="Category (Expense Account):").grid(row=1, column=0, sticky='w', pady=5)
        self.budget_category_combo = ttk.Combobox(form_frame, width=40, state='readonly')
        self.budget_category_combo.grid(row=1, column=1, pady=5, padx=5, sticky='ew')
        
        ttk.Label(form_frame, text="Budget Amount (฿):").grid(row=2, column=0, sticky='w', pady=5)
        self.budget_amount = ttk.Entry(form_frame, width=20)
        self.budget_amount.grid(row=2, column=1, pady=5, padx=5, sticky='w')
        
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="💾 Create/Update Budget",
                  command=self.create_budget, width=22).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📊 View Budget",
                  command=self.view_budget, width=22).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Refresh Categories",
                  command=self.refresh_budget_dropdown, width=22).pack(side='left', padx=5)
        
        # Result display
        result_label = ttk.Label(tab, text="Results:", font=('Arial', 10, 'bold'))
        result_label.pack(pady=(10,5))
        
        self.budget_result = scrolledtext.ScrolledText(tab, height=15, width=90)
        self.budget_result.pack(pady=5, padx=20)
    
    def create_reports_tab(self):
        """Create the reports tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='📋 Reports')
        
        # Title
        title = ttk.Label(tab, text="Financial Reports", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=20)
        
        # Balance section
        balance_frame = ttk.LabelFrame(tab, text="Account Balance", padding=15)
        balance_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(balance_frame, text="Select Account:").grid(row=0, column=0, sticky='w', pady=5)
        self.report_account_combo = ttk.Combobox(balance_frame, width=40, state='readonly')
        self.report_account_combo.grid(row=0, column=1, pady=5, padx=5, sticky='ew')
        
        balance_frame.columnconfigure(1, weight=1)
        
        ttk.Button(balance_frame, text="💰 Get Balance",
                  command=self.get_balance, width=20).grid(row=1, column=0, 
                                                          columnspan=2, pady=10)
        
        # Budget report section
        budget_frame = ttk.LabelFrame(tab, text="Budget vs Actual Report", padding=15)
        budget_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(budget_frame, text="Period (YYYY-MM):").grid(row=0, column=0, sticky='w', pady=5)
        self.report_period = ttk.Entry(budget_frame, width=20)
        self.report_period.insert(0, str(date.today())[:7])
        self.report_period.grid(row=0, column=1, pady=5, padx=5, sticky='w')
        
        ttk.Button(budget_frame, text="📊 Generate Budget Report",
                  command=self.budget_report, width=25).grid(row=1, column=0, 
                                                            columnspan=2, pady=10)
        
        # Refresh button
        ttk.Button(tab, text="🔄 Refresh Account List",
                  command=self.refresh_report_dropdown, width=25).pack(pady=10)
        
        # Result display
        result_label = ttk.Label(tab, text="Results:", font=('Arial', 10, 'bold'))
        result_label.pack(pady=(10,5))
        
        self.reports_result = scrolledtext.ScrolledText(tab, height=15, width=90)
        self.reports_result.pack(pady=5, padx=20)
    
    # Helper functions for dropdowns
    
    def load_accounts_cache(self):
        """Load accounts from backend and cache them."""
        try:
            result = main.get_accounts()
            if result.get('ok'):
                self.accounts_cache = result.get('items', [])
                # Filter expense accounts for budget
                self.expense_accounts = [
                    acc for acc in self.accounts_cache 
                    if acc['type'] == 'expense'
                ]
                return True
            return False
        except Exception as e:
            print(f"Error loading accounts: {e}")
            return False
    
    def update_transaction_labels(self):
        """Update transaction form labels based on type."""
        txn_type = self.txn_type.get()
        
        if txn_type == "income":
            self.txn_from_label.config(text="Income Source:")
            self.txn_to_label.config(text="Receiving Account (Bank/Cash):")
        elif txn_type == "expense":
            self.txn_from_label.config(text="Payment Account (Bank/Card):")
            self.txn_to_label.config(text="Expense Category:")
        else:  # transfer
            self.txn_from_label.config(text="From Account:")
            self.txn_to_label.config(text="To Account:")
    
    def populate_dropdown(self, combo_widget, filter_type=None):
        """
        Populate dropdown with accounts.
        
        Arguments:
            combo_widget: Combobox widget to populate
            filter_type: Optional account type filter
        """
        if filter_type:
            accounts = [acc for acc in self.accounts_cache if acc['type'] == filter_type]
        else:
            accounts = self.accounts_cache
        
        values = [f"{acc['account_id']} - {acc['name']} ({acc['type']})" 
                 for acc in accounts]
        combo_widget['values'] = values
        if values:
            combo_widget.current(0)
    
    def get_account_id_from_selection(self, combo_widget):
        """Extract account ID from combobox selection."""
        selection = combo_widget.get()
        if selection:
            return int(selection.split(' - ')[0])
        return None
    
    def refresh_transaction_dropdowns(self):
        """Refresh account dropdowns in transaction tab."""
        if self.load_accounts_cache():
            txn_type = self.txn_type.get()
            
            if txn_type == "income":
                self.populate_dropdown(self.txn_credit_combo, 'income')
                self.populate_dropdown(self.txn_debit_combo, 'asset')
            elif txn_type == "expense":
                self.populate_dropdown(self.txn_credit_combo, 'asset')
                self.populate_dropdown(self.txn_debit_combo, 'expense')
            else:  # transfer
                self.populate_dropdown(self.txn_credit_combo, 'asset')
                self.populate_dropdown(self.txn_debit_combo, 'asset')
            
            messagebox.showinfo("Success", "Account lists refreshed!")
        else:
            messagebox.showerror("Error", "Failed to load accounts")
    
    def refresh_budget_dropdown(self):
        """Refresh category dropdown in budget tab."""
        if self.load_accounts_cache():
            values = [acc['name'] for acc in self.expense_accounts]
            self.budget_category_combo['values'] = values
            if values:
                self.budget_category_combo.current(0)
            messagebox.showinfo("Success", "Category list refreshed!")
        else:
            messagebox.showerror("Error", "Failed to load categories")
    
    def refresh_report_dropdown(self):
        """Refresh account dropdown in reports tab."""
        if self.load_accounts_cache():
            self.populate_dropdown(self.report_account_combo)
            messagebox.showinfo("Success", "Account list refreshed!")
        else:
            messagebox.showerror("Error", "Failed to load accounts")
    
    # Backend function calls
    
    def init_database(self):
        """Initialize the database."""
        try:
            result = main.init()
            self.display_result(self.setup_result, result)
            messagebox.showinfo("Success", "Database initialized successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize database: {str(e)}")
    
    def load_default_accounts(self):
        """Load default chart of accounts."""
        try:
            result = main.init_coa_default()
            self.display_result(self.setup_result, result)
            # Refresh cache after loading
            self.load_accounts_cache()
            messagebox.showinfo("Success", 
                              f"Loaded {result.get('added', 0)} default accounts!\n\n"
                              "Now go to other tabs and click 'Refresh' buttons.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load accounts: {str(e)}")
    
    def view_accounts(self):
        """View all accounts."""
        try:
            result = main.get_accounts()
            self.display_result(self.accounts_result, result)
            # Refresh cache and populate dropdown
            if self.load_accounts_cache():
                self.populate_dropdown(self.ob_account_combo)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view accounts: {str(e)}")
    
    def set_opening_balance(self):
        """Set opening balance for an account."""
        try:
            account_id = self.get_account_id_from_selection(self.ob_account_combo)
            if not account_id:
                messagebox.showerror("Error", "Please select an account")
                return
            
            amount = float(self.ob_amount.get())
            date_str = self.ob_date.get()
            
            result = main.set_opening_balance(account_id, amount, date_str)
            self.display_result(self.accounts_result, result)
            
            if result.get('ok'):
                messagebox.showinfo("Success", "Opening balance set!")
                self.ob_amount.delete(0, tk.END)
            else:
                messagebox.showerror("Error", result.get('error', 'Unknown error'))
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
    
    def add_transaction(self):
        """Add a new transaction."""
        try:
            date_str = self.txn_date.get()
            amount = float(self.txn_amount.get())
            credit_id = self.get_account_id_from_selection(self.txn_credit_combo)
            debit_id = self.get_account_id_from_selection(self.txn_debit_combo)
            notes = self.txn_notes.get()
            
            if not credit_id or not debit_id:
                messagebox.showerror("Error", "Please select both accounts")
                return
            
            result = main.add_transaction(date_str, amount, debit_id, 
                                         credit_id, notes)
            self.display_result(self.txn_result, result)
            
            if result.get('ok'):
                txn_type = self.txn_type.get()
                type_name = {"income": "Income", "expense": "Expense", "transfer": "Transfer"}
                messagebox.showinfo("Success", f"{type_name[txn_type]} transaction recorded!")
                # Clear form
                self.txn_amount.delete(0, tk.END)
                self.txn_notes.delete(0, tk.END)
            else:
                messagebox.showerror("Error", result.get('error', 'Unknown error'))
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
    
    def view_all_transactions(self):
        """View all transactions using search."""
        try:
            result = main.search_transactions()
            self.display_result(self.txn_result, result)
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
    
    def create_budget(self):
        """Create or update a budget."""
        try:
            period = self.budget_period.get()
            category = self.budget_category_combo.get()
            amount = float(self.budget_amount.get())
            
            if not category:
                messagebox.showerror("Error", "Please select a category")
                return
            
            result = main.create_or_update_budget(period, category, amount)
            self.display_result(self.budget_result, result)
            
            if result.get('ok'):
                messagebox.showinfo("Success", "Budget created/updated!")
                self.budget_amount.delete(0, tk.END)
            else:
                messagebox.showerror("Error", result.get('error', 'Unknown error'))
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
    
    def view_budget(self):
        """View budget for a period."""
        try:
            period = self.budget_period.get()
            result = main.get_budget(period)
            self.display_result(self.budget_result, result)
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
    
    def get_balance(self):
        """Get account balance."""
        try:
            account_id = self.get_account_id_from_selection(self.report_account_combo)
            if not account_id:
                messagebox.showerror("Error", "Please select an account")
                return
            
            result = main.get_balance(account_id)
            self.display_result(self.reports_result, result)
            
            if result.get('ok'):
                balance = result.get('balance', 0)
                acc_name = self.report_account_combo.get().split(' - ')[1].split(' (')[0]
                messagebox.showinfo("Balance", 
                                  f"{acc_name}\nBalance: ฿{balance:,.2f}")
        except ValueError:
            messagebox.showerror("Error", "Please select a valid account")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
    
    def budget_report(self):
        """Generate budget vs actual report."""
        try:
            period = self.report_period.get()
            result = main.budget_report(period)
            self.display_result(self.reports_result, result)
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
    
    def display_result(self, text_widget, result):
        """
        Display result in a text widget.
        
        Arguments:
            text_widget: Scrolled text widget to display in
            result: Result dictionary to display
        """
        text_widget.delete(1.0, tk.END)
        formatted = json.dumps(result, indent=2, ensure_ascii=False)
        text_widget.insert(1.0, formatted)


def main_gui():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = BahtBuddyGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main_gui()