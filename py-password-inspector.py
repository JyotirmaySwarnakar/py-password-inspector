import hashlib
import random
import string
import requests
import nltk
import customtkinter as ctk
from nltk.corpus import words
import webbrowser
import tkinter as tk 

nltk.download('words')
ENGLISH_WORDS = set(w.lower() for w in words.words())

SUBSTITUTIONS = {'a': '@', 's': '$', 'o': '0', 'i': '1', 'e': '3', 'l': '1', 't': '7'}

def check_length(password):
    return len(password) >= 12

def check_character_variety(password):
    return (any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in string.punctuation for c in password))

def find_dictionary_words(password):
    found = []
    clean_pass = ''.join(c.lower() for c in password if c.isalpha())
    for word in ENGLISH_WORDS:
        if word in clean_pass and len(word) > 3:
            found.append(word)
    return found

def suggest_variation(word):
    return ''.join(SUBSTITUTIONS.get(c.lower(), c) for c in word).capitalize()

def replace_words_in_password(password, matched_words):
    result = password
    for word in matched_words:
        replacement = suggest_variation(word)
        result = result.replace(word, replacement, 1)
        result = result.replace(word.capitalize(), replacement, 1)
        result = result.replace(word.upper(), replacement.upper(), 1)

    if not any(c.isdigit() for c in result):
        result += str(random.randint(10, 99))
    if not any(c in string.punctuation for c in result):
        result += random.choice("!@#$%^&*()_+")

    suffix_chars = string.ascii_letters + string.digits + string.punctuation
    result += ''.join(random.choices(suffix_chars, k=6))

    return result

def check_breach(password):
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]
    try:
        response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
        if response.status_code != 200:
            return None
        hashes = (line.split(':') for line in response.text.splitlines())
        for hash_suffix, count in hashes:
            if hash_suffix == suffix:
                return int(count)
        return 0
    except Exception:
        return None

def analyze_password(password):
    score = 0
    messages = []
    matched_words = find_dictionary_words(password)

    if check_length(password): score += 1
    else: messages.append("❌ Too short: Use at least 12 characters.")

    if check_character_variety(password): score += 1
    else: messages.append("❌ Use mix of uppercase, lowercase, numbers, and symbols.")

    if matched_words:
        messages.append(f"❌ Dictionary words found: {', '.join(matched_words)}")
    else:
        score += 1

    breach_count = check_breach(password)
    if breach_count == 0: score += 1
    elif breach_count is None: messages.append("⚠️ Could not check breach status.")
    else: messages.append(f"❌ This password appeared in {breach_count} data breaches!")

    if score == 4: messages.insert(0, "✅ Strong password!")
    elif score == 3: messages.insert(0, "🟡 Fair password.")
    else: messages.insert(0, "🔴 Weak password.")

    suggestion = replace_words_in_password(password, matched_words) if matched_words else ""
    return messages, suggestion

# --------------- GUI (CustomTkinter) ----------------

suggestion_text = ""  # Global variable to hold the suggestion

def copy_suggestion():
    if suggestion_text:
        app.clipboard_clear()
        app.clipboard_append(suggestion_text)
        copied_label.pack(pady=2)
        app.after(1200, copied_label.pack_forget)

def generate_password():
    global suggestion_text
    # Generate a strong random password
    chars = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(random.choices(chars, k=16))
        # Ensure it meets all criteria
        if (any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in string.punctuation for c in password)):
            break
    suggestion_text = password
    result_box.configure(state="normal")
    result_box.delete("0.0", "end")
    result_box.insert("end", f"🔁 Generated strong password:\n{password}")
    result_box.configure(state="disabled")
    generate_btn.pack_forget()
    copy_btn.pack(pady=5)

def check_password():
    global suggestion_text
    password = entry.get()
    if not password:
        result_box.configure(state="normal")
        result_box.delete("0.0", "end")
        result_box.insert("end", "⚠️ Please enter a password.")
        result_box.configure(state="disabled")
        copy_btn.pack_forget()
        generate_btn.pack(pady=5)
        suggestion_text = ""
        return

    results, suggestion = analyze_password(password)
    result_box.configure(state="normal")
    result_box.delete("0.0", "end")
    result_box.insert("end", "\n".join(results))
    if suggestion:
        result_box.insert("end", f"\n\n🔁 Suggested stronger password:\n{suggestion}")
        suggestion_text = suggestion
        copy_btn.pack(pady=5)
        generate_btn.pack_forget()
    else:
        suggestion_text = ""
        copy_btn.pack_forget()
        generate_btn.pack(pady=5)
    result_box.configure(state="disabled")

def open_options_menu(event):
    # Use standard Tkinter Menu for popup
    menu = tk.Menu(app, tearoff=0)
    menu.add_command(label="Change Theme", command=toggle_theme)
    menu.add_command(label="Visit Developer", command=visit_developer)
    menu.add_command(label="Source Code", command=open_source_code) 
    menu.tk_popup(event.x_root, event.y_root)

def toggle_theme():
    current = ctk.get_appearance_mode()
    if current == "Dark":
        ctk.set_appearance_mode("Light")
    else:
        ctk.set_appearance_mode("Dark")

def visit_developer():
    webbrowser.open("https://github.com/JyotirmaySwarnakar")

def open_source_code():
    webbrowser.open("https://github.com/JyotirmaySwarnakar/py-password-inspector")

# App Appearance
ctk.set_appearance_mode("System")  # "Dark", "Light", or "System"
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("600x400")
app.title("🔐 Password Strength Checker")

menu_btn = ctk.CTkButton(
    app,
    text="⚙️",
    width=36,
    height=36,
    fg_color="#3879d5",  # Light gray background for visibility
    text_color="#FFFFFF", # Dark icon color
    hover=False,
    font=("Segoe UI", 20)
)
menu_btn.place(x=10, y=10)
menu_btn.bind("<Button-1>", open_options_menu)

# UI Layout
ctk.CTkLabel(app, text="Enter your password:", font=("Segoe UI", 16)).pack(pady=10)
entry = ctk.CTkEntry(app, width=400, font=("Consolas", 14))
entry.pack(pady=5)

check_btn = ctk.CTkButton(app, text="Check Password", command=check_password)
check_btn.pack(pady=10)

result_box = ctk.CTkTextbox(app, height=180, width=500, font=("Segoe UI", 12), wrap="word")
result_box.pack(pady=10)
result_box.configure(state="disabled")

copy_btn = ctk.CTkButton(app, text="Copy Suggested Password", command=copy_suggestion)
copy_btn.pack_forget()  # Hide by default

copied_label = ctk.CTkLabel(app, text="Copied!", text_color="#2ecc40", font=("Segoe UI", 12))
copied_label.pack_forget()  # Hide by default

generate_btn = ctk.CTkButton(app, text="Generate Password", command=generate_password)
generate_btn.pack(pady=5)  # Show by default

app.mainloop()