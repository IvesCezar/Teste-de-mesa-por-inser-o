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
		"action": "Lista original",
		"values": working.copy(),
		"display_values": working.copy(),
		"explanation": (
			"Esta é a lista antes da ordenação. O primeiro número, sozinho, já pode ser considerado "
			"ordenado. A cada rodada, pegamos o próximo número (a chave) e o inserimos no lugar "
			"correto dentro da parte que já está em ordem."
		),
	}]

	for index in range(1, len(working)):
		key = working[index]
		cursor = index - 1
		sorted_part = working[:index].copy()

		while cursor >= 0:
			compared = working[cursor]
			if compared > key:
				working[cursor + 1] = compared
				display_values = working.copy()
				display_values[cursor] = "[ ]"
				trace.append({
					"index": index,
					"key": key,
					"compared": f"Posição {cursor + 1}: {compared}",
					"action": f"{compared} > {key}: deslocar",
					"values": working.copy(),
					"display_values": display_values,
					"explanation": (
						f"Rodada {index}: a chave é {key}, retirada da posição {index + 1}. "
						f"A parte à esquerda estava ordenada: {sorted_part}. Agora comparamos "
						f"{compared} na posição {cursor + 1} com a chave {key}. Como {compared} > {key}, "
						f"{compared} não pode ficar antes de {key}; por isso, copiamos {compared} "
						f"para a posição {cursor + 2}. A chave {key} fica guardada temporariamente. "
						"[ ] marca o espaço que ela poderá ocupar. Em seguida, comparamos a chave "
						"com o número imediatamente à esquerda."
					),
				})
				cursor -= 1
			else:
				trace.append({
					"index": index,
					"key": key,
					"compared": f"Posição {cursor + 1}: {compared}",
					"action": f"{compared} <= {key}: parar",
					"values": working.copy(),
					"display_values": working.copy(),
					"explanation": (
						f"Rodada {index}: a chave é {key}, retirada da posição {index + 1}. "
						f"Comparamos {compared} na posição {cursor + 1} com {key}. Como {compared} <= {key}, "
						f"{compared} já pode ficar antes da chave. Não deslocamos esse número nem os "
						f"anteriores; a busca termina aqui. A chave será inserida logo depois de {compared}. "
						"Se os valores forem iguais, também paramos: assim, números iguais mantêm a ordem original."
					),
				})
				break

		working[cursor + 1] = key
		if cursor < 0:
			insertion_reason = (
				"Chegamos ao início da lista: todos os números anteriores eram maiores que a chave "
				"e foram deslocados uma posição à direita."
			)
		else:
			insertion_reason = (
				f"A busca parou porque o número na posição {cursor + 1} é menor ou igual à chave."
			)
		trace.append({
			"index": index,
			"key": key,
			"compared": "-",
			"action": f"Inserir {key} na posição {cursor + 2}",
			"values": working.copy(),
			"display_values": working.copy(),
			"explanation": (
				f"Agora inserimos a chave {key} na posição {cursor + 2}. {insertion_reason} "
				f"A lista fica {working}. A parte à esquerda da próxima chave continuará sendo "
				"considerada ordenada."
			),
		})

	return trace


class InsertionSortApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Teste de Mesa | Ordenação por Inserção")
		self.root.geometry("1040x740")
		self.root.minsize(760, 580)
		self.root.configure(bg="#f3f5f4")

		self.trace = []
		self.current_step = 0
		self.input_value = tk.StringVar(value="8, 3, 5, 1, 9, 2")
		self.step_label = tk.StringVar(value="Informe os valores e inicie a simulação.")
		self.explanation_text = tk.StringVar(
			value="Cada etapa explica a comparação feita e o motivo de deslocar ou manter cada número."
		)
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
		tk.Label(content,
				 text="A chave é o número que está sendo inserido. [ ] indica o espaço temporário deixado por ela.",
				 background="#f3f5f4", foreground="#52645c",
				 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 7))

		table_frame = tk.Frame(content, bg="#ffffff", highlightthickness=1,
							   highlightbackground="#d8e0dc")
		table_frame.pack(fill="both", expand=True)
		columns = ("step", "index", "key", "compared", "action", "values")
		self.table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="none")
		headings = {
			"step": "Etapa",
			"index": "Posição i",
			"key": "Chave",
			"compared": "Comparação",
			"action": "Resumo",
			"values": "Vetor após a etapa",
		}
		widths = {"step": 58, "index": 82, "key": 70, "compared": 160,
				  "action": 240, "values": 230}
		for column in columns:
			self.table.heading(column, text=headings[column])
			self.table.column(column, width=widths[column], minwidth=45,
							  anchor="center" if column in ("step", "index", "key") else "w",
							  stretch=column in ("action", "values"))

		scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
		self.table.configure(yscrollcommand=scrollbar.set)
		self.table.pack(side="left", fill="both", expand=True)
		scrollbar.pack(side="right", fill="y")

		detail_panel = tk.Frame(content, bg="#e7efea", padx=14, pady=10)
		detail_panel.pack(fill="x", pady=(10, 0))
		tk.Label(detail_panel, text="POR QUE ESTA ETAPA ACONTECE?",
				 background="#e7efea", foreground="#24523b",
				 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 5))
		self.explanation_label = tk.Label(
			detail_panel, textvariable=self.explanation_text,
			background="#e7efea", foreground="#263b32",
			font=("Segoe UI", 10), justify="left", anchor="w", wraplength=920
		)
		self.explanation_label.pack(fill="x", anchor="w")
		content.bind(
			"<Configure>",
			lambda event: self.explanation_label.configure(wraplength=max(300, event.width - 70))
		)

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
				step, row["index"], row["key"], row["compared"], row["action"],
				row["display_values"]
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
			f"Etapa {step} de {len(self.trace) - 1}  |  Chave: {row['key']}  |  "
			f"Vetor: {row['display_values']}"
		)
		self.explanation_text.set(row["explanation"])
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
