import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from pathlib import Path
from workflow import open_folder
from workflow import run_multi_comparison

base_dir = Path.home() / "ContainerChecker"




def browse_file(entry_widget):
    file_path = filedialog.askopenfilename(
        title="PDF auswählen",
        filetypes=[("PDF-Dateien", "*.pdf"), ("Alle Dateien", "*.*")]
    )
    if file_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file_path)


def start_comparison():
    file_a = entry_file_a.get().strip()
    file_b = entry_file_b.get().strip()
    parser_b = parser_b_var.get()
    file_c = entry_file_c.get().strip()
    parser_c = parser_c_var.get()

    if not file_a or not file_b:
        messagebox.showwarning(
            "Fehlende Eingabe",
            "pls select files"
        )
        return

    try:
        status_var.set("comparing ...")
        root.update_idletasks()

        comparisons = [
            {"file": file_b, "parser": parser_b},
            {"file": file_c, "parser": parser_c},
        ]
        result_data = run_multi_comparison(
            file_ref=file_a,
            parser_ref=parser_a,
            comparisons=comparisons,
            base_dir=Path.home() / "ContainerChecker"
        )
        results = result_data["results"]
        base_output_dir = result_data["base_output_dir"]
        only_ref_all_file = result_data["only_ref_all_file"]

        summary_text = "Finished multi comparison:\n\n"
        summary_text += (
        f"\nOnly in MAX3 (not in MSK/HL): {len(open(only_ref_all_file).readlines()) - 1}\n"
        f"{only_ref_all_file}\n\n"
    )

        for r in results:
            summary_text += (
                f"{r['comparison']}\n"
                f"Container in ref: {r['count_ref']}\n"
                f"Container in other: {r['count_other']}\n"
                f"Only in ref: {r['only_ref']}\n"
                f"Only in other: {r['only_other']}\n"
                f"Differences: {r['differences']}\n"
                f"Output: {r['output_dir']}\n\n"
            )

        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, summary_text)

        status_var.set("Fertig.")
        messagebox.showinfo("success", "successfully finished comparing.")
        open_folder(base_output_dir)

    except Exception as e:
        status_var.set("Fehler.")
        messagebox.showerror("Fehler", str(e))

#Design
Font = ("Consolas", 12)
Fontclr="#22931c"
Buttomclr = "#2FFF00"
Fieldclr = "#2a6ae1"
BG="#0B0D32"
BG2="#C02A2A"

def style_optionmenu(menu):
    menu.config(
        bg="#2b2b2b",
        fg="white",
        activebackground="#00fb9f",
        activeforeground="black",
        borderwidth=0,
        highlightthickness=0,
        relief="flat",
        font=("Arial", 11)
    )

    menu["menu"].config(
        bg="#2b2b2b",
        fg="white",
        activebackground="#00ffcc",
        activeforeground="black"
    )


root = tk.Tk()
root.title("Container Checker")
root.geometry("760x520")
root.configure(bg="#417834")

parser_a = "MAX3"
parser_b_var = tk.StringVar(value="MSK")
status_var = tk.StringVar(value="ready.")

main_frame = tk.Frame(root, padx=15, pady=15, bg=BG)
main_frame.pack(fill="both", expand=True)

title_label = tk.Label(
    main_frame,
    text="Container Checker",
    font= ("Consolas", 18, "bold"),
    bg="#272D93",
    fg="#ED0000"
    
)
title_label.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 15))

# Datei A
tk.Label(main_frame, bg=BG, fg=Fontclr, font=Font,text="Max3 reference  (choose your reference file from Max3)").grid(row=1, column=0, sticky="w")
entry_file_a = tk.Entry(
    main_frame,
    bg=Fieldclr,     
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    width=70)
entry_file_a.grid(row=2, column=0, padx=(0, 10), pady=(0, 10), sticky="we")
tk.Button(
    main_frame,
    text="select",
    fg=Buttomclr,
    bg=BG2,
    activebackground="#00fb9f",
    command=lambda: browse_file(entry_file_a)
).grid(row=2, column=1, pady=(0, 10), sticky="w")





# Datei B
tk.Label(main_frame, bg=BG, fg=Fontclr, font=Font,text="Manifest a").grid(row=5, column=0, sticky="w")
entry_file_b = tk.Entry(
    main_frame,
    bg=Fieldclr,     
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    width=70)
entry_file_b.grid(row=6, column=0, padx=(0, 10), pady=(0, 10), sticky="we")
tk.Button(
    main_frame,
    text="select",
    fg=Buttomclr,
    bg=BG2,
    activebackground="#00fb9f",
    command=lambda: browse_file(entry_file_b)
).grid(row=6, column=1, pady=(0, 10), sticky="w")

tk.Label(main_frame, bg=BG, fg=Fontclr, font=Font,text="Parser a").grid(row=7, column=0, sticky="w")
parser_b_menu = tk.OptionMenu(main_frame, parser_b_var, "MAX3", "MSK", "HL")
parser_b_menu.grid(row=8, column=0, sticky="w", pady=(0, 15))
style_optionmenu(parser_b_menu)





# Datei C (HL)
tk.Label(main_frame, bg=BG, fg=Fontclr, font=Font, text="Manifest b").grid(row=9, column=0, sticky="w")

entry_file_c = tk.Entry(
    main_frame,
    bg=Fieldclr,
    borderwidth=0,
    highlightthickness=0,
    relief="flat",
    width=70
)
entry_file_c.grid(row=10, column=0, padx=(0, 10), pady=(0, 10), sticky="we")

tk.Button(
    main_frame,
    text="select",
    fg=Buttomclr,
    bg=BG2,
    activebackground="#00fb9f",
    command=lambda: browse_file(entry_file_c)
).grid(row=10, column=1, pady=(0, 10), sticky="w")

parser_c_var = tk.StringVar(value="HL")

tk.Label(main_frame, bg=BG, fg=Fontclr, font=Font, text="Parser b").grid(row=11, column=0, sticky="w")

parser_c_menu = tk.OptionMenu(main_frame, parser_c_var, "MAX3", "MSK", "HL")
parser_c_menu.grid(row=12, column=0, sticky="w", pady=(0, 15))
style_optionmenu(parser_c_menu)

# Startbutton
start_button = tk.Button(
    main_frame,
    text="compare",
    command=start_comparison,
    height=2,
    width=20,
    bg=BG2,
    fg=Buttomclr,
    activebackground="#00fb9f",
)
start_button.grid(row=13, column=0, sticky="w", pady=(0, 15))

tk.Label(
    main_frame,
    textvariable=status_var,
    fg="blue"
).grid(row=13, column=0, columnspan=2, sticky="e", pady=(0, 10))

tk.Label(main_frame, bg=BG, fg=Fontclr, font=Font, text="summary").grid(row=15, column=0, sticky="w")

result_text = tk.Text(main_frame, height=12, width=80)
result_text.grid(row=16, column=0, columnspan=3, sticky="nsew")

main_frame.rowconfigure(16, weight=1)
main_frame.columnconfigure(0, weight=1)

root.mainloop()