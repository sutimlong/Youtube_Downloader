import customtkinter as ctk

app = ctk.CTk()
entry = ctk.CTkEntry(app, placeholder_text="Paste here")
entry.pack(pady=20)
app.mainloop()
