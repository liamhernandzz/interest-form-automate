import tkinter as tk
from tkinter import filedialog, ttk, messagebox

from run_sf_parser import load_and_parse
from emailer import process_submission

class InterestFormApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Interest Form Automator")
        self.root.geometry("900x500")

        self.parsed_rows = []  # holds (fields, decision) tuples after upload

        # --- Top controls ---
        top_frame = tk.Frame(root)
        top_frame.pack(fill="x", padx=10, pady=10)

        upload_btn = tk.Button(top_frame, text="Upload CSV", command=self.upload_csv)
        upload_btn.pack(side="left")

        self.dry_run_var = tk.BooleanVar(value=True)  # default: safe
        dry_run_check = tk.Checkbutton(
            top_frame, text="Dry Run (preview only, no real sending)",
            variable=self.dry_run_var
        )
        dry_run_check.pack(side="left", padx=15)

        send_btn = tk.Button(top_frame, text="Process / Send", command=self.process_all)
        send_btn.pack(side="left")

        self.status_label = tk.Label(root, text="No file loaded.", anchor="w")
        self.status_label.pack(fill="x", padx=10)

        # --- Results table ---
        columns = ("first_name", "last_name", "email", "sport", "ticket_type", "action")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=130)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def upload_csv(self):
        filepath = filedialog.askopenfilename(
            title="Select CSV export",
            filetypes=[("CSV files", "*.csv")]
        )
        if not filepath:
            return  # user cancelled

        try:
            self.parsed_rows = load_and_parse(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse file:\n{e}")
            return

        self.populate_table()
        self.status_label.config(
            text=f"Loaded {len(self.parsed_rows)} rows from {filepath}"
        )

    def populate_table(self):
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        for fields, decision in self.parsed_rows:
            sports = ", ".join(decision.get("sports", []))
            ticket_type = decision.get("ticket_type", "")
            action = decision.get("action", "")

            self.tree.insert("", "end", values=(
                fields.get("firstName", ""),
                fields.get("lastName", ""),
                fields.get("emailAddress", ""),
                sports,
                ticket_type,
                action,
            ))

    def process_all(self):
        if not self.parsed_rows:
            messagebox.showwarning("No data", "Upload a CSV first.")
            return

        dry_run = self.dry_run_var.get()

        if not dry_run:
            confirmed = messagebox.askyesno(
                "Confirm real send",
                f"This will send {len(self.parsed_rows)} real emails. Continue?"
            )
            if not confirmed:
                return

        sent_count = 0
        skipped_count = 0

        for fields, decision in self.parsed_rows:
            if decision["action"] == "send_template":
                process_submission(fields, decision, dry_run=dry_run)
                sent_count += 1
            else:
                skipped_count += 1

        mode = "Dry run complete" if dry_run else "Sending complete"
        messagebox.showinfo(
            "Done",
            f"{mode}.\nProcessed: {sent_count}\nSkipped (manual review): {skipped_count}"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = InterestFormApp(root)
    root.mainloop()