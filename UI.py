import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import traceback
import os

class BulkEmailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SriRam Mail")
        self.root.configure(bg="black")
        self.root.resizable(width=False, height=False)

        # Configure row and column weights for responsiveness
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Load the logo
        logo_image = Image.open("logo.png")
        logo_image = logo_image.resize((150, 100))
        self.logo = ImageTk.PhotoImage(logo_image)

        # File Selection
        tk.Label(root, text="Send To:", bg="black", fg="white").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.send_to_entry = tk.Entry(root, width=30, bg="black", fg="white")
        self.send_to_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        tk.Button(root, text="Browse", command=self.browse_send_to_file).grid(row=0, column=2, padx=10, pady=10)

        # Sender Credentials
        tk.Label(root, text="Send From:", bg="black", fg="white").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.send_from_entry = tk.Entry(root, width=30, bg="black", fg="white")
        self.send_from_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        tk.Button(root, text="Browse", command=self.browse_send_from_file).grid(row=1, column=2, padx=10, pady=10)

        # Subject
        tk.Label(root, text="Subject:", bg="black", fg="white").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.subject_entry = tk.Entry(root, width=30, bg="black", fg="white")
        self.subject_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # Message Body
        tk.Label(root, text="Message:", bg="black", fg="white").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.message_entry = tk.Text(root, width=30, height=10, wrap=tk.WORD, bg="black", fg="white")
        self.message_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # Attachment
        tk.Label(root, text="Attachment:", bg="black", fg="white").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.attachment_entry = tk.Entry(root, width=30, bg="black", fg="white")
        self.attachment_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        tk.Button(root, text="Browse", command=self.browse_attachment_file).grid(row=4, column=2, padx=10, pady=10)

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(root, variable=self.progress_var, maximum=100, style="Black.Horizontal.TProgressbar").grid(row=5, column=1, padx=20, pady=20, sticky="ew")

        # Logo
        logo_label = tk.Label(root, image=self.logo, bg="black")
        logo_label.grid(row=0, column=3, rowspan=4, padx=10, pady=10, sticky="nsew")

        # Signature
        tk.Label(root, text="Created by - Shivam Sawarn", font=("Helvetica", 10), bg="black", fg="white").grid(row=6, column=3, padx=10, pady=10, sticky="sew")

        # Start Button
        send_button = tk.Button(root, text="Send", command=self.start_sending, bg="yellow", fg="black", height=1, relief="solid", borderwidth=2, overrelief="groove", width=5, font=("Helvetica", 16, "bold"))
        send_button.grid(row=7, column=1, pady=0, sticky="ew")

        # Configure column and row weights for responsiveness
        for i in range(8):
            root.grid_rowconfigure(i, weight=1)
        root.grid_columnconfigure(3, weight=1)

    def browse_send_to_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("Text files", "*.txt")])
        self.send_to_entry.delete(0, 'end')
        self.send_to_entry.insert(0, file_path)

    def browse_send_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("Text files", "*.txt")])
        self.send_from_entry.delete(0, 'end')
        self.send_from_entry.insert(0, file_path)

    def browse_attachment_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        if file_path:
            file_size = os.path.getsize(file_path)
            if file_size > 2 * 1024 * 1024:  # 2 MB in bytes
                messagebox.showerror("Error", "Attachment size exceeds 2 MB limit.")
            else:
                self.attachment_entry.delete(0, 'end')
                self.attachment_entry.insert(0, file_path)

    def start_sending(self):
        send_to_file_path = self.send_to_entry.get()
        send_from_file_path = self.send_from_entry.get()
        subject = self.subject_entry.get()
        message_body = self.message_entry.get("1.0", tk.END).strip()  # Retrieve and strip extra spaces/newlines
        attachment_path = self.attachment_entry.get()

        if not all([send_to_file_path, send_from_file_path, subject, message_body]):
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        try:
            email_data = pd.read_csv(send_to_file_path)
            sender_credentials = pd.read_csv(send_from_file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {e}")
            print(f"Error reading file: {e}")
            return

        try:
            email_data.columns = [col.strip().lower() for col in email_data.columns]
            sender_credentials.columns = [col.strip().lower() for col in sender_credentials.columns]
        except Exception as e:
            messagebox.showerror("Error", f"Error processing data: {e}")
            print(f"Error processing data: {e}")
            return

        total_emails = len(email_data)
        progress_step = 100 / total_emails

        for index, row in email_data.iterrows():
            sender_row = index % len(sender_credentials)
            sender_email = sender_credentials.at[sender_row, 'email']
            sender_password = sender_credentials.at[sender_row, 'password']
            smtp_server = sender_credentials.at[sender_row, 'smtp']
            smtp_port = sender_credentials.at[sender_row, 'port']

            recipient_email = row['email']

            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = recipient_email
            message['Subject'] = subject

            salutation = f"Dear {row['name']},\n\n"
            body = salutation+message_body
            #body = message_body.replace('\n', '<br>')
            message.attach(MIMEText(body, 'html'))

            if attachment_path:
                try:
                    part = MIMEBase('application', 'octet-stream')
                    with open(attachment_path, 'rb') as file:
                        part.set_payload(file.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
                    message.attach(part)
                except Exception as e:
                    messagebox.showerror("Error", f"Error attaching file: {e}")
                    print(f"Error attaching file: {e}")
                    continue

            try:
                with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, recipient_email, message.as_string())
            except Exception as e:
                error_message = f"Error sending email to {recipient_email}: {e}"
                messagebox.showerror("Error", error_message)
                print(error_message)
                print(traceback.format_exc())
                continue

            self.progress_var.set((index + 1) * progress_step)
            self.root.update_idletasks()

        messagebox.showinfo("Success", "Emails sent successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BulkEmailApp(root)
    root.mainloop()
