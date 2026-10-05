import tkinter as tk
from tkinter import messagebox, ttk


def parse_numbers(raw_value):
	parts = raw_value.replace(",", " ").split()
	if not parts:
		raise ValueError("Digite pelo menos um número inteiro.")

	try:
		values = [int(part) for part in parts]
	except ValueError as error:
		raise ValueError("Use somente números inteiros separados por espaço ou vírgula.") from error

	if len(values) > 40:
		raise ValueError("Para manter a tabela legível, informe no máximo 40 números.")
	return values


def create_trace(values):
	working = values.copy()
	trace = [{
		"index": "-",
		"key": "-",
		"compared": "-",
		"action": "Vetor inicial",
		"values": working.copy(),
	}]

	for index in range(1, len(working)):
		key = working[index]
		cursor = index - 1

		while cursor >= 0:
			compared = working[cursor]
			if compared > key:
				working[cursor + 1] = compared
				action = f"{compared} > {key}: desloca {compared} para a direita"
				trace.append({
					"index": index,
					"key": key,
					"compared": f"A[{cursor}] = {compared}",
					"action": action,
					"values": working.copy(),
				})
				cursor -= 1
			else:
				trace.append({
					"index": index,
					"key": key,
					"compared": f"A[{cursor}] = {compared}",
					"action": f"{compared} <= {key}: para os deslocamentos",
					"values": working.copy(),
				})
				break

		working[cursor + 1] = key
		trace.append({
			"index": index,
			"key": key,
			"compared": "-",
			"action": f"Insere {key} na posição {cursor + 1}",
			"values": working.copy(),
		})

	return trace


class InsertionSortApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Teste de Mesa | Ordenação por Inserção")
		self.root.geometry("1040x650")
		self.root.minsize(760, 480)
		self.root.configure(bg="#f3f5f4")

		self.trace = []
		self.current_step = 0
		self.input_value = tk.StringVar(value="8, 3, 5, 1, 9, 2")
		self.step_label = tk.StringVar(value="Informe os valores e inicie a simulação.")
		self._configure_style()
		self._build_interface()

	def _configure_style(self):
		style = ttk.Style()
		style.theme_use("clam")
		style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff",
						foreground="#202a27", rowheight=34, font=("Segoe UI", 10))
		style.configure("Treeview.Heading", background="#e5ebe8", foreground="#263b34",
						font=("Segoe UI", 9, "bold"), padding=(8, 9))
		style.map("Treeview", background=[("selected", "#d6ebe1")],
				  foreground=[("selected", "#173b2c")])
		style.configure("TButton", font=("Segoe UI", 10), padding=(12, 8))

	def _build_interface(self):
		header = tk.Frame(self.root, bg="#173b2c", padx=26, pady=20)
		header.pack(fill="x")
		tk.Label(header, text="ORDENAÇÃO POR INSERÇÃO", bg="#173b2c", fg="#b9dfc9",
				 font=("Segoe UI", 9, "bold")).pack(anchor="w")
		tk.Label(header, text="Teste de mesa", bg="#173b2c", fg="#ffffff",
				 font=("Segoe UI", 23, "bold")).pack(anchor="w", pady=(4, 0))

		content = tk.Frame(self.root, bg="#f3f5f4", padx=26, pady=18)
		content.pack(fill="both", expand=True)

		controls = tk.Frame(content, bg="#f3f5f4")
		controls.pack(fill="x", pady=(0, 14))
		tk.Label(controls, text="Valores inteiros", bg="#f3f5f4", fg="#35453f",
				 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))

		input_row = tk.Frame(controls, bg="#f3f5f4")
		input_row.pack(fill="x")
		self.entry = ttk.Entry(input_row, textvariable=self.input_value, font=("Segoe UI", 11))
		self.entry.pack(side="left", fill="x", expand=True, ipady=6)
		self.entry.bind("<Return>", lambda _event: self.start())
		ttk.Button(input_row, text="Iniciar teste", command=self.start).pack(side="left", padx=(10, 0))

		tk.Label(content, textvariable=self.step_label, bg="#f3f5f4", fg="#35453f",
				 font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 9))

		table_frame = tk.Frame(content, bg="#ffffff", highlightthickness=1,
							   highlightbackground="#d8e0dc")
		table_frame.pack(fill="both", expand=True)
		columns = ("step", "index", "key", "compared", "action", "values")
		self.table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
		headings = {
			"step": "Etapa",
			"index": "i",
			"key": "Chave",
			"compared": "Elemento comparado",
			"action": "Decisão / operação",
			"values": "Vetor após a etapa",
		}
		widths = {"step": 58, "index": 48, "key": 70, "compared": 155,
				  "action": 360, "values": 210}
		for column in columns:
			self.table.heading(column, text=headings[column])
			self.table.column(column, width=widths[column], minwidth=45,
							  anchor="center" if column in ("step", "index", "key") else "w",
							  stretch=column in ("action", "values"))

		scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
		self.table.configure(yscrollcommand=scrollbar.set)
		self.table.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")
		navigation = tk.Frame(content, bg="#f3f5f4", pady=12)
		navigation.pack(fill="x")
		self.previous_button = ttk.Button(navigation, text="← Anterior", command=self.previous_step,
										  state="disabled")
		self.previous_button.pack(side="left")
		self.next_button = ttk.Button(navigation, text="Próxima →", command=self.next_step,
									  state="disabled")
		self.next_button.pack(side="left", padx=(8, 0))
		ttk.Button(navigation, text="Mostrar resultado", command=self.show_result).pack(side="right")

	def start(self):
		try:
			values = parse_numbers(self.input_value.get())
		except ValueError as error:
			messagebox.showerror("Entrada inválida", str(error), parent=self.root)
			return

		self.trace = create_trace(values)
		self.current_step = 0
		for item in self.table.get_children():
			self.table.delete(item)

		for step, row in enumerate(self.trace):
			self.table.insert("", "end", iid=str(step), values=(
				step, row["index"], row["key"], row["compared"], row["action"], row["values"]
			))
		self._show_step(0)
		self.table.focus_set()

	def _show_step(self, step):
		if not self.trace:
			return
		self.current_step = step
		item_id = str(step)
		self.table.selection_set(item_id)
		self.table.focus(item_id)
		self.table.see(item_id)
		row = self.trace[step]
		self.step_label.set(
			f"Etapa {step} de {len(self.trace) - 1}  |  Vetor: {row['values']}"
		)
		self.previous_button.configure(state="normal" if step > 0 else "disabled")
		self.next_button.configure(
			state="normal" if step < len(self.trace) - 1 else "disabled"
		)

	def previous_step(self):
		if self.current_step > 0:
			self._show_step(self.current_step - 1)

	def next_step(self):
		if self.trace and self.current_step < len(self.trace) - 1:
			self._show_step(self.current_step + 1)

	def show_result(self):
		if self.trace:
			messagebox.showinfo("Vetor ordenado", str(self.trace[-1]["values"]), parent=self.root)


def main():
	root = tk.Tk()
	InsertionSortApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()
