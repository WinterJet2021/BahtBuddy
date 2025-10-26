"""
gui.py

Graphical User Interface for the BahtBuddy Personal Finance Management System.
Provides a user-friendly interface for managing accounts, transactions,
and budgets using tkinter.

Created by Thanakrit Punyasuntontamrong (Pass) and Chirayu Sukhum (Tuey), October 15, 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from typing import Any, Dict, List, Optional

import main

# -----------------------------------------------------------------------------
# Helper Classes and Functions
# -----------------------------------------------------------------------------

class AccountManager:
    """
    Manages and caches account data to avoid frequent database calls.
    Provides mappings between account IDs and names.
    """
    def __init__(self):
        self.refresh()

    def refresh(self):
        """Reloads all account data from the database."""
        try:
            result = main.get_accounts()
            if result.get("ok"):
                self.accounts = result["items"]
                self.id_to_name = {acc['account_id']: acc['name'] for acc in self.accounts}
                self.name_to_id = {acc['name']: acc['account_id'] for acc in self.accounts}
            else:
                self._reset()
        except Exception:
            self._reset()
            messagebox.showerror("Database Error", "Could not fetch accounts from database.")

    def _reset(self):
        """Resets cache to empty state."""
        self.accounts = []
        self.id_to_name = {}
        self.name_to_id = {}

    def get_name(self, account_id: int) -> str:
        """Get account name from an ID."""
        return self.id_to_name.get(account_id, "Unknown Account")

    def get_id(self, name: str) -> Optional[int]:
        """Get account ID from a name."""
        return self.name_to_id.get(name)

    def get_names_by_type(self, types: List[str]) -> List[str]:
        """Get a sorted list of account names for given types."""
        return sorted([acc['name'] for acc in self.accounts if acc['type'] in types])


def show_api_error(result: Dict[str, Any], title: str = "Error"):
    """Displays an error message from a backend API call."""
    error_msg = result.get("error", "An unknown error occurred.")
    messagebox.showerror(title, error_msg)

# -----------------------------------------------------------------------------
# Dialog Windows (Toplevels) for Specific Actions
# -----------------------------------------------------------------------------

class AddAccountDialog(tk.Toplevel):
    """Dialog for adding a new account."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Add New Account")
        self.geometry("300x150")
        self.transient(parent)
        self.grab_set()

        # Widgets
        ttk.Label(self, text="Account Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = ttk.Entry(self, width=30)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self, text="Account Type:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(self, textvariable=self.type_var, state="readonly", values=['asset', 'liability', 'equity', 'income', 'expense'])
        self.type_combo.grid(row=1, column=1, padx=10, pady=5)
        self.type_combo.set('asset')

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save", command=self.save_account).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)
        
        self.name_entry.focus_set()

    def save_account(self):
        name = self.name_entry.get().strip()
        acc_type = self.type_var.get()

        if not name:
            messagebox.showwarning("Input Error", "Account name cannot be empty.", parent=self)
            return
        
        # This function is not in main.py, so we call the database layer directly.
        # In a real-world scenario, this logic would be in main.py.
        try:
            main.db.insert_account(name, acc_type)
            messagebox.showinfo("Success", f"Account '{name}' added successfully.", parent=self)
            self.parent.refresh_data()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not add account:\n{e}", parent=self)


class SetBalanceDialog(tk.Toplevel):
    """Dialog for setting an account's opening balance."""
    def __init__(self, parent, account_id, account_name):
        super().__init__(parent)
        self.parent = parent
        self.account_id = account_id
        
        self.title(f"Opening Balance for {account_name}")
        self.geometry("350x150")
        self.transient(parent)
        self.grab_set()

        today = datetime.now().strftime("%Y-%m-%d")

        # Widgets
        ttk.Label(self, text="Amount:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(self, width=20)
        self.amount_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.date_entry = ttk.Entry(self, width=20)
        self.date_entry.grid(row=1, column=1, padx=10, pady=5)
        self.date_entry.insert(0, today)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save", command=self.save_balance).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

        self.amount_entry.focus_set()

    def save_balance(self):
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showwarning("Input Error", "Invalid amount.", parent=self)
            return
            
        date = self.date_entry.get().strip()
        
        result = main.set_opening_balance(self.account_id, amount, date)
        if result["ok"]:
            messagebox.showinfo("Success", "Opening balance set successfully.", parent=self)
            self.parent.refresh_data()
            self.destroy()
        else:
            show_api_error(result, "Save Failed")


class ModifyTransactionDialog(tk.Toplevel):
    """Dialog for modifying an existing transaction."""
    def __init__(self, parent, txn_data, acc_manager):
        super().__init__(parent)
        self.parent = parent
        self.txn_id = txn_data['txn_id']
        self.acc_manager = acc_manager

        self.title(f"Modify Transaction #{self.txn_id}")
        self.transient(parent)
        self.grab_set()

        # Prepare account lists
        self.debit_accounts = self.acc_manager.get_names_by_type(['asset', 'expense'])
        self.credit_accounts = self.acc_manager.get_names_by_type(['asset', 'liability', 'equity', 'income'])

        # Widgets
        pad_options = {'padx': 10, 'pady': 5, 'sticky': 'w'}
        ttk.Label(self, text="Date (YYYY-MM-DD):").grid(row=0, column=0, **pad_options)
        self.date_entry = ttk.Entry(self, width=30)
        self.date_entry.grid(row=0, column=1, **pad_options)
        self.date_entry.insert(0, txn_data['date'])

        ttk.Label(self, text="Amount:").grid(row=1, column=0, **pad_options)
        self.amount_entry = ttk.Entry(self, width=30)
        self.amount_entry.grid(row=1, column=1, **pad_options)
        self.amount_entry.insert(0, str(txn_data['amount']))

        ttk.Label(self, text="Debit Account (To):").grid(row=2, column=0, **pad_options)
        self.debit_var = tk.StringVar(value=self.acc_manager.get_name(txn_data['debit_account_id']))
        self.debit_combo = ttk.Combobox(self, textvariable=self.debit_var, state="readonly", values=self.debit_accounts, width=28)
        self.debit_combo.grid(row=2, column=1, **pad_options)
        
        ttk.Label(self, text="Credit Account (From):").grid(row=3, column=0, **pad_options)
        self.credit_var = tk.StringVar(value=self.acc_manager.get_name(txn_data['credit_account_id']))
        self.credit_combo = ttk.Combobox(self, textvariable=self.credit_var, state="readonly", values=self.credit_accounts, width=28)
        self.credit_combo.grid(row=3, column=1, **pad_options)
        
        ttk.Label(self, text="Notes:").grid(row=4, column=0, **pad_options)
        self.notes_entry = ttk.Entry(self, width=30)
        self.notes_entry.grid(row=4, column=1, **pad_options)
        self.notes_entry.insert(0, txn_data['notes'])
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save Changes", command=self.save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

    def save(self):
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showwarning("Input Error", "Invalid amount.", parent=self)
            return

        debit_id = self.acc_manager.get_id(self.debit_var.get())
        credit_id = self.acc_manager.get_id(self.credit_var.get())
        
        fields = {
            "date": self.date_entry.get(),
            "amount": amount,
            "debit_account_id": debit_id,
            "credit_account_id": credit_id,
            "notes": self.notes_entry.get(),
        }

        result = main.modify_transaction(self.txn_id, **fields)
        if result['ok']:
            messagebox.showinfo("Success", "Transaction updated.", parent=self)
            self.parent.refresh_data()
            self.destroy()
        else:
            show_api_error(result, "Update Failed")

# -----------------------------------------------------------------------------
# Main Content Frames
# -----------------------------------------------------------------------------

class DashboardFrame(ttk.Frame):
    """A summary dashboard showing key financial figures."""
    def __init__(self, parent, acc_manager, **kwargs):
        super().__init__(parent, **kwargs)
        self.acc_manager = acc_manager

        self.configure(padding=20)
        self.columnconfigure(0, weight=1)
        
        ttk.Label(self, text="Financial Overview", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        self.assets_var = tk.StringVar(value="Calculating...")
        self.liabilities_var = tk.StringVar(value="Calculating...")
        self.net_worth_var = tk.StringVar(value="Calculating...")
        
        self._create_metric_card("Total Assets", self.assets_var, 1)
        self._create_metric_card("Total Liabilities", self.liabilities_var, 2)
        self._create_metric_card("Net Worth", self.net_worth_var, 3, bold=True)
        
        ttk.Button(self, text="Refresh", command=self.refresh_data).grid(row=4, column=0, columnspan=2, pady=20)

    def _create_metric_card(self, label_text, str_var, row, bold=False):
        font_weight = "bold" if bold else "normal"
        ttk.Label(self, text=f"{label_text}:", font=("Helvetica", 14)).grid(row=row, column=0, sticky="e", padx=10, pady=5)
        ttk.Label(self, textvariable=str_var, font=("Helvetica", 14, font_weight)).grid(row=row, column=1, sticky="w", padx=10, pady=5)

    def refresh_data(self):
        """Recalculates and updates the dashboard figures."""
        self.assets_var.set("Calculating...")
        self.liabilities_var.set("Calculating...")
        self.net_worth_var.set("Calculating...")
        self.update_idletasks() # Force UI update

        total_assets = 0.0
        total_liabilities = 0.0
        
        for account in self.acc_manager.accounts:
            res = main.get_balance(account['account_id'])
            if res['ok']:
                balance = res['balance']
                if account['type'] == 'asset':
                    total_assets += balance
                elif account['type'] == 'liability':
                    total_liabilities += balance
        
        net_worth = total_assets - total_liabilities
        
        self.assets_var.set(f"฿ {total_assets:,.2f}")
        self.liabilities_var.set(f"฿ {total_liabilities:,.2f}")
        self.net_worth_var.set(f"฿ {net_worth:,.2f}")


class AccountsFrame(ttk.Frame):
    """Frame for viewing and managing accounts."""
    def __init__(self, parent, acc_manager, **kwargs):
        super().__init__(parent, **kwargs)
        self.acc_manager = acc_manager
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Top Bar with actions
        top_bar = ttk.Frame(self, padding="5")
        top_bar.grid(row=0, column=0, sticky="ew")
        ttk.Button(top_bar, text="Add New Account", command=self.open_add_account_dialog).pack(side="left", padx=5)
        ttk.Button(top_bar, text="Set Opening Balance", command=self.open_set_balance_dialog).pack(side="left", padx=5)
        ttk.Button(top_bar, text="Refresh", command=self.refresh_data).pack(side="left", padx=5)
        self.init_coa_btn = ttk.Button(top_bar, text="Load Default Accounts", command=self.init_coa)
        self.init_coa_btn.pack(side="left", padx=5)

        # Treeview for accounts list
        self.tree = ttk.Treeview(self, columns=("id", "name", "type", "balance"), show="headings", selectmode="browse")
        self.tree.grid(row=1, column=0, sticky="nsew")

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Account Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("balance", text="Balance (฿)")
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("balance", width=120, anchor="e")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
    
    def refresh_data(self):
        """Clears and repopulates the accounts treeview."""
        self.acc_manager.refresh() # Update the cache first
        
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        if not self.acc_manager.accounts:
            self.init_coa_btn.state(['!disabled']) # Enable button if no accounts
            self.tree.insert("", "end", values=("", "No accounts found.", "Click 'Load Default Accounts' to start.", ""))
        else:
            self.init_coa_btn.state(['disabled']) # Disable if accounts exist
            for acc in self.acc_manager.accounts:
                res = main.get_balance(acc['account_id'])
                balance = f"{res['balance']:,.2f}" if res['ok'] else "Error"
                self.tree.insert("", "end", values=(acc['account_id'], acc['name'], acc['type'], balance))

    def open_add_account_dialog(self):
        AddAccountDialog(self)

    def open_set_balance_dialog(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showinfo("Selection Required", "Please select an account from the list.")
            return
        
        item_values = self.tree.item(selected_item)['values']
        acc_id, acc_name = item_values[0], item_values[1]
        SetBalanceDialog(self, acc_id, acc_name)

    def init_coa(self):
        if messagebox.askyesno("Confirm", "This will add a default set of accounts. Proceed?"):
            res = main.init_coa_default()
            if res['ok']:
                messagebox.showinfo("Success", f"{res['added']} default accounts have been added.")
                self.refresh_data()
            else:
                show_api_error(res, "Initialization Failed")


class TransactionsFrame(ttk.Frame):
    """Frame for adding, viewing, and managing transactions."""
    def __init__(self, parent, acc_manager, **kwargs):
        super().__init__(parent, **kwargs)
        self.acc_manager = acc_manager
        self.transactions_data = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Paned Window for resizable sections
        paned_window = ttk.PanedWindow(self, orient="vertical")
        paned_window.grid(row=0, column=0, sticky="nsew", pady=5)

        # --- Top Pane: Add Transaction ---
        add_frame = ttk.LabelFrame(paned_window, text="Record New Transaction", padding=10)
        paned_window.add(add_frame, weight=0)
        self._create_add_transaction_ui(add_frame)

        # --- Bottom Pane: View/Search Transactions ---
        view_frame = ttk.LabelFrame(paned_window, text="View & Search Transactions", padding=10)
        paned_window.add(view_frame, weight=1)
        self._create_view_transaction_ui(view_frame)

    def _create_add_transaction_ui(self, parent):
        parent.columnconfigure(1, weight=1)
        
        # Date and Amount (common to all types)
        ttk.Label(parent, text="Date:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = ttk.Entry(parent)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(parent, text="Amount:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(parent)
        self.amount_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Notebook for Expense/Income/Transfer
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)

        self.exp_tab, self.inc_tab, self.trn_tab = (
            ttk.Frame(self.notebook),
            ttk.Frame(self.notebook),
            ttk.Frame(self.notebook),
        )
        self.notebook.add(self.exp_tab, text="Expense")
        self.notebook.add(self.inc_tab, text="Income")
        self.notebook.add(self.trn_tab, text="Transfer")
        
        self._create_tab(self.exp_tab, "Paid From:", ['asset', 'liability'], "Category:", ['expense'])
        self._create_tab(self.inc_tab, "Source:", ['income'], "Deposit To:", ['asset'])
        self._create_tab(self.trn_tab, "From Account:", ['asset', 'liability'], "To Account:", ['asset', 'liability'])
        
        # Notes and Record Button
        ttk.Label(parent, text="Notes:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.notes_entry = ttk.Entry(parent)
        self.notes_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        ttk.Button(parent, text="Record Transaction", command=self.record_transaction).grid(row=3, column=0, columnspan=4, pady=10)

    def _create_tab(self, tab, label1, types1, label2, types2):
        tab.columnconfigure(1, weight=1)
        tab.columnconfigure(3, weight=1)
        
        ttk.Label(tab, text=label1).grid(row=0, column=0, padx=5, sticky="w")
        combo1 = ttk.Combobox(tab, state="readonly")
        combo1.grid(row=0, column=1, padx=5, sticky="ew")
        
        ttk.Label(tab, text=label2).grid(row=0, column=2, padx=5, sticky="w")
        combo2 = ttk.Combobox(tab, state="readonly")
        combo2.grid(row=0, column=3, padx=5, sticky="ew")

        tab.c1_types, tab.c2_types = types1, types2
        tab.combo1, tab.combo2 = combo1, combo2

    def _create_view_transaction_ui(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        # Filters
        filter_frame = ttk.Frame(parent)
        filter_frame.grid(row=0, column=0, sticky="ew", pady=5)
        ttk.Label(filter_frame, text="Account:").pack(side="left", padx=5)
        self.search_acc_combo = ttk.Combobox(filter_frame, state="readonly", width=30)
        self.search_acc_combo.pack(side="left", padx=5)
        # Add a "All Accounts" option
        self.search_acc_combo.bind("<<ComboboxSelected>>", lambda e: self.search_transactions())

        ttk.Button(filter_frame, text="Search", command=self.search_transactions).pack(side="left", padx=5)
        ttk.Button(filter_frame, text="Modify Selected", command=self.open_modify_dialog).pack(side="right", padx=5)
        ttk.Button(filter_frame, text="Delete Selected", command=self.delete_transaction).pack(side="right", padx=5)

        # Treeview
        self.tree = ttk.Treeview(parent, columns=("id", "date", "debit", "credit", "amount", "notes"), show="headings")
        self.tree.grid(row=1, column=0, sticky="nsew")
        
        headings = {"id": "ID", "date": "Date", "debit": "To (Debit)", "credit": "From (Credit)", "amount": "Amount", "notes": "Notes"}
        widths = {"id": 40, "date": 90, "debit": 150, "credit": 150, "amount": 100}
        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=widths.get(col, 200), anchor="w" if col=="notes" else "center")
        self.tree.column("amount", anchor="e")

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
    
    def refresh_data(self):
        """Refreshes all data sources for this frame."""
        self.acc_manager.refresh()
        
        # Populate dropdowns in "Add" section
        for tab in [self.exp_tab, self.inc_tab, self.trn_tab]:
            tab.combo1['values'] = self.acc_manager.get_names_by_type(tab.c1_types)
            tab.combo2['values'] = self.acc_manager.get_names_by_type(tab.c2_types)
        
        # Populate search account dropdown
        all_accounts = ["-- All Accounts --"] + sorted(self.acc_manager.name_to_id.keys())
        self.search_acc_combo['values'] = all_accounts
        self.search_acc_combo.set(all_accounts[0])
        
        # Fetch initial transaction list
        self.search_transactions()

    def record_transaction(self):
        date = self.date_entry.get()
        notes = self.notes_entry.get()
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid amount.")
            return

        current_tab = self.notebook.select()

        if current_tab == str(self.exp_tab):
            # Expense: credit = paid from, debit = expense category
            credit_name, debit_name = self.exp_tab.combo1.get(), self.exp_tab.combo2.get()
        elif current_tab == str(self.inc_tab):
            # Income: credit = income source, debit = deposit to
            credit_name, debit_name = self.inc_tab.combo1.get(), self.inc_tab.combo2.get()
        else:
            # Transfer: credit = from, debit = to
            credit_name, debit_name = self.trn_tab.combo1.get(), self.trn_tab.combo2.get()
        
        if not all([date, amount, credit_name, debit_name]):
            messagebox.showwarning("Input Error", "Please fill all required fields.")
            return
            
        credit_id = self.acc_manager.get_id(credit_name)
        debit_id = self.acc_manager.get_id(debit_name)

        result = main.add_transaction(date, amount, debit_id, credit_id, notes)
        if result['ok']:
            messagebox.showinfo("Success", "Transaction recorded.")
            self.amount_entry.delete(0, 'end')
            self.notes_entry.delete(0, 'end')
            self.search_transactions() # Refresh list
        else:
            show_api_error(result, "Record Failed")
    
    def search_transactions(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        account_name = self.search_acc_combo.get()
        account_id = None
        if account_name != "-- All Accounts --":
            account_id = self.acc_manager.get_id(account_name)
            
        if account_id:
            res = main.view_transactions(account_id=account_id)
        else:
            res = main.search_transactions()
        
        if res['ok']:
            self.transactions_data = res['items']
            for txn in self.transactions_data:
                debit_name = self.acc_manager.get_name(txn['debit_account_id'])
                credit_name = self.acc_manager.get_name(txn['credit_account_id'])
                self.tree.insert("", "end", values=(
                    txn['txn_id'], txn['date'], debit_name, credit_name, f"{txn['amount']:,.2f}", txn['notes']
                ))

    def open_modify_dialog(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showinfo("Selection Required", "Please select a transaction to modify.")
            return
        
        txn_id = self.tree.item(selected_item)['values'][0]
        txn_data = next((t for t in self.transactions_data if t['txn_id'] == txn_id), None)
        if txn_data:
            ModifyTransactionDialog(self, txn_data, self.acc_manager)

    def delete_transaction(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showinfo("Selection Required", "Please select a transaction to delete.")
            return

        txn_id = self.tree.item(selected_item)['values'][0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete transaction #{txn_id}?"):
            res = main.delete_transaction(txn_id)
            if res['ok']:
                messagebox.showinfo("Success", "Transaction deleted.")
                self.search_transactions()
            else:
                show_api_error(res, "Delete Failed")


class BudgetFrame(ttk.Frame):
    """Frame for setting budgets and viewing budget vs. actuals reports."""
    def __init__(self, parent, acc_manager, **kwargs):
        super().__init__(parent, **kwargs)
        self.acc_manager = acc_manager

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        paned_window = ttk.PanedWindow(self, orient="vertical")
        paned_window.grid(row=0, column=0, sticky="nsew", pady=5)

        # Top Pane: Set Budget
        set_frame = ttk.LabelFrame(paned_window, text="Set Budget", padding=10)
        paned_window.add(set_frame, weight=0)
        self._create_set_budget_ui(set_frame)

        # Bottom Pane: Budget Report
        report_frame = ttk.LabelFrame(paned_window, text="Budget Report", padding=10)
        paned_window.add(report_frame, weight=1)
        self._create_budget_report_ui(report_frame)

    def _create_set_budget_ui(self, parent):
        default_period = datetime.now().strftime("%Y-%m")
        
        ttk.Label(parent, text="Period (YYYY-MM):").pack(side="left", padx=5)
        self.set_period_entry = ttk.Entry(parent, width=10)
        self.set_period_entry.pack(side="left", padx=5)
        self.set_period_entry.insert(0, default_period)
        
        ttk.Label(parent, text="Category:").pack(side="left", padx=5)
        self.set_cat_combo = ttk.Combobox(parent, state="readonly", width=25)
        self.set_cat_combo.pack(side="left", padx=5)
        
        ttk.Label(parent, text="Amount:").pack(side="left", padx=5)
        self.set_amount_entry = ttk.Entry(parent, width=15)
        self.set_amount_entry.pack(side="left", padx=5)
        
        ttk.Button(parent, text="Set/Update Budget", command=self.set_budget).pack(side="left", padx=10)

    def _create_budget_report_ui(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        filter_frame = ttk.Frame(parent)
        filter_frame.grid(row=0, column=0, sticky="ew", pady=5)
        
        ttk.Label(filter_frame, text="Report Period (YYYY-MM):").pack(side="left", padx=5)
        self.report_period_entry = ttk.Entry(filter_frame, width=10)
        self.report_period_entry.pack(side="left", padx=5)
        self.report_period_entry.insert(0, datetime.now().strftime("%Y-%m"))
        

        self.tree = ttk.Treeview(parent, columns=("cat", "budget", "actual", "var", "pct"), show="headings")
        self.tree.grid(row=1, column=0, sticky="nsew")

        headings = {"cat": "Category", "budget": "Budget", "actual": "Actual", "var": "Variance", "pct": "% Used"}
        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, anchor="e", width=120)
        self.tree.column("cat", anchor="w")

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
    def refresh_data(self):
        self.acc_manager.refresh()
        expense_accounts = self.acc_manager.get_names_by_type(['expense'])
        self.set_cat_combo['values'] = expense_accounts
        if expense_accounts:
            self.set_cat_combo.current(0)
        self.generate_report()

    def set_budget(self):
        period = self.set_period_entry.get()
        category = self.set_cat_combo.get()
        try:
            amount = float(self.set_amount_entry.get())
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid amount.")
            return

        if not category:
            messagebox.showwarning("Input Error", "Please select a category.")
            return
            
        res = main.create_or_update_budget(period, category, amount)
        if res['ok']:
            messagebox.showinfo("Success", "Budget has been set.")
            self.set_amount_entry.delete(0, 'end')
            # If the report is for the same period, refresh it
            if self.report_period_entry.get() == period:
                self.generate_report()
        else:
            show_api_error(res, "Set Budget Failed")
    
    def generate_report(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        period = self.report_period_entry.get()
        res = main.budget_report(period)
        
        if res['ok']:
            for row in res['rows']:
                pct_str = f"{row['pct_of_budget']:.1f}%" if row['pct_of_budget'] is not None else "N/A"
                self.tree.insert("", "end", values=(
                    row['category'],
                    f"{row['budget']:,.2f}",
                    f"{row['actual']:,.2f}",
                    f"{row['variance']:,.2f}",
                    pct_str,
                ))

# -----------------------------------------------------------------------------
# Main Application Window
# -----------------------------------------------------------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BahtBuddy - Personal Finance Manager")
        self.geometry("900x700")
        
        # Initialize backend database
        main.init()

        # Initialize Account Manager
        self.acc_manager = AccountManager()

        # Main layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Navigation bar
        nav_bar = ttk.Frame(self, width=150, style='Card.TFrame')
        nav_bar.grid(row=0, column=0, sticky="nsw")
        nav_bar.grid_rowconfigure(5, weight=1) # Push exit button to bottom
        
        ttk.Label(nav_bar, text="BahtBuddy", font=("Helvetica", 16, "bold"), padding=10).grid(row=0, column=0)
        
        nav_buttons = {
            "Dashboard": DashboardFrame,
            "Accounts": AccountsFrame,
            "Transactions": TransactionsFrame,
            "Budgets": BudgetFrame,
        }
        for i, (name, frame_class) in enumerate(nav_buttons.items(), 1):
            btn = ttk.Button(nav_bar, text=name, command=lambda fc=frame_class: self.show_frame(fc))
            btn.grid(row=i, column=0, sticky="ew", padx=10, pady=5)

        ttk.Button(nav_bar, text="Exit", command=self.quit).grid(row=6, column=0, sticky="ew", padx=10, pady=10)

        # Content area
        container = ttk.Frame(self)
        container.grid(row=0, column=1, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (DashboardFrame, AccountsFrame, TransactionsFrame, BudgetFrame):
            frame = F(container, self.acc_manager)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(DashboardFrame)

    def show_frame(self, frame_class):
        """Shows the requested frame and refreshes its data."""
        frame = self.frames[frame_class]
        frame.tkraise()
        # Call the frame's refresh method if it exists
        if hasattr(frame, 'refresh_data'):
            frame.refresh_data()


if __name__ == "__main__":
    app = App()
    app.mainloop()