import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import shutil
from organiser import get_file_category, organize_code_file, organize_regular_file, undo_organization

class FileOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer")
        self.root.geometry("700x650")
        self.root.configure(bg='#f0f0f0')

        # Title
        title_label = tk.Label(root, text="File Organizer", font=("Arial", 20, "bold"),
                              bg='#f0f0f0', fg='#333')
        title_label.pack(pady=15)

        # Description
        desc_label = tk.Label(root, text="Organize your files by type automatically",
                             font=("Arial", 12), bg='#f0f0f0', fg='#666')
        desc_label.pack(pady=5)

        # Folder selection frame
        folder_frame = tk.Frame(root, bg='#f0f0f0')
        folder_frame.pack(pady=15)

        self.folder_label = tk.Label(folder_frame, text="No folder selected",
                                    font=("Arial", 10), bg='#f0f0f0', fg='#666',
                                    wraplength=400)
        self.folder_label.pack(pady=10)

        # Buttons frame
        buttons_frame = tk.Frame(root, bg='#f0f0f0')
        buttons_frame.pack(pady=10)

        # Select folder button
        select_button = tk.Button(buttons_frame, text="Select Folder",
                                 command=self.select_folder, font=("Arial", 11, "bold"),
                                 bg='#4CAF50', fg='white', padx=15, pady=8,
                                 relief='raised', borderwidth=2)
        select_button.pack(side=tk.LEFT, padx=8)

        # Organize button
        self.organize_button = tk.Button(buttons_frame, text="Organize Files",
                                        command=self.organize_files, font=("Arial", 11, "bold"),
                                        bg='#2196F3', fg='white', padx=15, pady=8,
                                        relief='raised', borderwidth=2, state='disabled')
        self.organize_button.pack(side=tk.LEFT, padx=8)

        # Undo button
        self.undo_button = tk.Button(buttons_frame, text="Undo Last",
                                    command=self.undo_files, font=("Arial", 11, "bold"),
                                    bg='#FF9800', fg='white', padx=15, pady=8,
                                    relief='raised', borderwidth=2, state='disabled')
        self.undo_button.pack(side=tk.LEFT, padx=8)

        # Options frame
        options_frame = tk.LabelFrame(root, text="Options", bg='#f0f0f0', padx=10, pady=10)
        options_frame.pack(pady=10, padx=20, fill=tk.X)

        # Checkboxes for options
        self.detect_duplicates_var = tk.BooleanVar(value=True)
        self.auto_rename_var = tk.BooleanVar(value=False)
        self.dry_run_var = tk.BooleanVar(value=False)

        detect_check = tk.Checkbutton(options_frame, text="Enable duplicate detection",
                                     variable=self.detect_duplicates_var, bg='#f0f0f0',
                                     font=("Arial", 10))
        detect_check.pack(anchor=tk.W, pady=3)

        rename_check = tk.Checkbutton(options_frame, text="Enable auto-rename",
                                     variable=self.auto_rename_var, bg='#f0f0f0',
                                     font=("Arial", 10))
        rename_check.pack(anchor=tk.W, pady=3)

        dry_run_check = tk.Checkbutton(options_frame, text="Dry run mode (no actual changes)",
                                      variable=self.dry_run_var, bg='#f0f0f0',
                                      font=("Arial", 10))
        dry_run_check.pack(anchor=tk.W, pady=3)

        # Log frame
        log_frame = tk.LabelFrame(root, text="Processing Log", bg='#f0f0f0', padx=5, pady=5)
        log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Text widget for logs
        self.log_text = tk.Text(log_frame, height=12, font=("Courier", 9), 
                               bg='#fff', fg='#333', relief='sunken', borderwidth=1)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        # Scrollbar for log
        scrollbar = tk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Status bar
        self.status_label = tk.Label(root, text="Ready to organize files", 
                                    font=("Arial", 9), bg='#e0e0e0', fg='#333',
                                    relief='sunken', borderwidth=1)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

        self.selected_folder = None
        self.stats = {
            'total': 0, 
            'moved': 0, 
            'code_files': 0, 
            'regular_files': 0,
            'duplicates': 0, 
            'skipped': 0
        }
        self.move_history = []  # Track moves for undo functionality

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select folder to organize")
        if folder_path:
            self.selected_folder = folder_path
            self.folder_label.config(text=f"Selected: {folder_path}", fg='#333')
            self.organize_button.config(state='normal')
            self.undo_button.config(state='disabled')
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, "Folder selected. Click 'Organize Files' to start.\n")
            self.log_text.config(state='disabled')
            self.update_status("Folder selected. Ready to organize.")
            self.stats = {
                'total': 0, 
                'moved': 0, 
                'code_files': 0, 
                'regular_files': 0,
                'duplicates': 0, 
                'skipped': 0
            }
            self.move_history = []  # Reset move history when selecting new folder

    def log_message(self, message):
        """Add a message to the log"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update_idletasks()

    def update_status(self, message):
        """Update the status bar"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def organize_files(self):
        if not self.selected_folder:
            messagebox.showerror("Error", "Please select a folder first!")
            return

        # Disable buttons during processing
        self.organize_button.config(state='disabled')
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)

        # Get options
        detect_duplicates = self.detect_duplicates_var.get()
        auto_rename = self.auto_rename_var.get()
        dry_run = self.dry_run_var.get()

        # Log start
        self.log_message("=" * 50)
        self.log_message("FILE ORGANIZATION STARTED")
        self.log_message("=" * 50)
        self.log_message(f"Folder: {self.selected_folder}")
        self.log_message(f"Duplicate detection: {'ON' if detect_duplicates else 'OFF'}")
        self.log_message(f"Auto-rename: {'ON' if auto_rename else 'OFF'}")
        self.log_message(f"Dry run mode: {'ON' if dry_run else 'OFF'}")
        self.log_message("------")
        self.update_status("Organizing files...")

        try:
            # Reset stats and move history
            self.stats = {
                'total': 0, 
                'moved': 0, 
                'code_files': 0, 
                'regular_files': 0,
                'duplicates': 0, 
                'skipped': 0
            }
            self.move_history = []

            # Perform file organization
            self.perform_organization(detect_duplicates, auto_rename, dry_run)

            # Log summary
            self.log_message("------")
            self.log_message("=" * 50)
            self.log_message("ORGANIZATION SUMMARY")
            self.log_message("=" * 50)
            self.log_message(f"Total files processed: {self.stats['total']}")
            self.log_message(f"Code files organized: {self.stats['code_files']}")
            self.log_message(f"Regular files organized: {self.stats['regular_files']}")
            self.log_message(f"Files moved: {self.stats['moved']}")
            self.log_message(f"Duplicates found: {self.stats['duplicates']}")
            self.log_message(f"Files skipped: {self.stats['skipped']}")
            self.log_message("=" * 50)
            if dry_run:
                self.log_message("✓ DRY RUN ONLY - NO CHANGES MADE")
            else:
                self.log_message("✓ Organization completed successfully!")
                # Enable undo button if files were actually moved
                if self.move_history:
                    self.undo_button.config(state='normal')
            self.log_message("")

            self.update_status("Organization completed!")
            messagebox.showinfo("Success", "Files organized successfully! Check log for details.")

        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
            self.update_status("Error occurred during organization.")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

        finally:
            # Re-enable button
            self.log_text.config(state='disabled')
            self.organize_button.config(state='normal')

    def perform_organization(self, detect_duplicates, auto_rename, dry_run):
        """
        Organize files using the unified smart categorization system.
        Handles both code files and regular files in a single pass.
        """
        if not os.path.exists(self.selected_folder):
            raise Exception("Folder path does not exist")

        files = os.listdir(self.selected_folder)

        for file in files:
            file_path = os.path.join(self.selected_folder, file)

            # Skip directories
            if os.path.isdir(file_path):
                continue

            self.stats['total'] += 1
            
            # Determine file category using smart classification
            category_type, category_name, sub_category = get_file_category(file_path)

            # Process code files
            if category_type == "code":
                success, message, src_path, dest_path = organize_code_file(
                    file_path, 
                    self.selected_folder, 
                    category_name, 
                    sub_category,
                    dry_run
                )
                self.stats['code_files'] += 1
                if success:
                    self.log_message(f"✓ {message}")
                    self.stats['moved'] += 1
                    # Track the move for undo functionality
                    if src_path and dest_path and not dry_run:
                        self.move_history.append((src_path, dest_path))
                else:
                    self.log_message(f"⊘ {message}")
                    self.stats['skipped'] += 1

            # Process regular files (images, videos, documents, archives, etc.)
            elif category_type == "regular":
                success, message, src_path, dest_path = organize_regular_file(
                    file_path, 
                    self.selected_folder, 
                    category_name,
                    detect_duplicates,
                    auto_rename,
                    dry_run
                )
                self.stats['regular_files'] += 1
                if success:
                    if "DUPLICATE" in message:
                        self.log_message(f"⚠ {message}")
                        self.stats['duplicates'] += 1
                    else:
                        self.log_message(f"✓ {message}")
                    self.stats['moved'] += 1
                    # Track the move for undo functionality
                    if src_path and dest_path and not dry_run:
                        self.move_history.append((src_path, dest_path))
                else:
                    self.log_message(f"⊘ {message}")
                    self.stats['skipped'] += 1

            # Handle unknown file types
            else:
                self.log_message(f"○ No category: {file}")
                self.stats['skipped'] += 1

            # Refresh UI during processing
            self.root.update_idletasks()

    def undo_files(self):
        """Undo the last file organization"""
        if not self.move_history:
            messagebox.showwarning("No Undo", "Nothing to undo!")
            self.undo_button.config(state='disabled')
            return

        self.undo_button.config(state='disabled')
        self.organize_button.config(state='disabled')
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)

        # Log undo start
        self.log_message("=" * 50)
        self.log_message("UNDO STARTED")
        self.log_message("=" * 50)
        self.log_message(f"Folder: {self.selected_folder}")
        self.log_message(f"Files to undo: {len(self.move_history)}")
        self.log_message("------")
        self.update_status("Undoing organization...")

        try:
            undo_stats = undo_organization(self.move_history)

            # Log summary
            self.log_message("------")
            self.log_message("=" * 50)
            self.log_message("UNDO SUMMARY")
            self.log_message("=" * 50)
            self.log_message(f"Files restored: {undo_stats['undone']}")
            self.log_message(f"Errors: {undo_stats['errors']}")
            self.log_message("=" * 50)
            self.log_message("✓ Undo completed successfully!")
            self.log_message("")

            # Clear move history after successful undo
            self.move_history = []

            self.update_status("Undo completed!")
            messagebox.showinfo("Success", "Files successfully restored to original locations!")

        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
            self.update_status("Error occurred during undo.")
            messagebox.showerror("Error", f"An error occurred during undo: {str(e)}")

        finally:
            # Re-enable buttons
            self.log_text.config(state='disabled')
            self.organize_button.config(state='normal')

def main():
    root = tk.Tk()
    app = FileOrganizerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()



