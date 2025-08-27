import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
import math
import statistics as stats
import re
import inspect
import random

# Modelos candidatos para ajuste empírico
MODELS = {
    'O(1)': lambda n: 1.0,
    'O(log n)': lambda n: math.log2(n + 1),
    'O(n)': lambda n: float(n),
    'O(n log n)': lambda n: (n * math.log2(n + 1)),
    'O(n^2)': lambda n: float(n)**2,
    'O(n^3)': lambda n: float(n)**3,
    'O(2^n)': lambda n: 2.0**float(n) if n < 30 else float('inf'),
}

def fit_complexity(ns, ts):
    # Filtra pares onde tempo > um limiar mínimo (ex: 1e-6s) para evitar ruído
    pairs = [(n, t) for n, t in zip(ns, ts) if t > 1e-6]
    if len(pairs) < 2:
        return 'Indefinido', float('inf'), 0.0

    ns, ts = zip(*pairs)
    best_model = None
    best_err = float('inf')
    best_a = 0.0
    for name, f in MODELS.items():
        try:
            xs = [f(n) for n in ns]
        except OverflowError:
            continue
        denom = sum(x*x for x in xs)
        if denom == 0:
            continue
        a = sum(x*t for x, t in zip(xs, ts)) / denom
        preds = [a * x for x in xs]
        eps = 1e-12
        mape = sum(abs(p - t) / max(t, eps) for p, t in zip(preds, ts)) / len(ts)
        if mape < best_err:
            best_err = mape
            best_model = name
            best_a = a
    return best_model or 'Indefinido', best_err, best_a

def generate_args(sig):
    args = []
    for name, param in sig.parameters.items():
        if param.annotation == int or 'int' in str(param.annotation) or 'n' in name:
            args.append(1)
        elif param.annotation == float or 'float' in str(param.annotation):
            args.append(1.0)
        elif param.annotation == list or 'list' in str(param.annotation) or 'arr' in name or 'vetor' in name:
            args.append([1,2,3])
        elif param.annotation == str or 'str' in str(param.annotation):
            args.append("abc")
        elif 'dist' in name:
            args.append([[0,1],[1,0]])
        elif 'target' in name or 'value' in name:
            args.append(3)
        else:
            args.append(1)
    return args

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analisador Dinâmico de Código Python")
        self.geometry("950x650")
        self.configure(bg="#e3eafc")
        self.create_widgets()

    def create_widgets(self):
        frame_top = tk.Frame(self, bg="#e3eafc")
        frame_top.pack(fill=tk.X, pady=10)
        tk.Label(frame_top, text="Analisador Dinâmico de Código Python", font=("Segoe UI", 22, "bold"), bg="#e3eafc", fg="#0d6efd").pack(pady=5)
        tk.Label(frame_top, text="Cole seu código Python abaixo:", font=("Segoe UI", 13), bg="#e3eafc", fg="#333").pack(pady=2)

        frame_code = tk.Frame(self, bg="#e3eafc")
        frame_code.pack(fill=tk.BOTH, expand=True, padx=20)
        self.txt_code = scrolledtext.ScrolledText(frame_code, height=15, font=("Consolas", 12), bg="#f4f7ff", fg="#222", insertbackground="#222", borderwidth=2, relief="groove")
        self.txt_code.pack(fill=tk.BOTH, expand=True, pady=5)

        frame_btn = tk.Frame(self, bg="#e3eafc")
        frame_btn.pack(fill=tk.X, pady=5)
        self.btn_run = tk.Button(frame_btn, text="Analisar", font=("Segoe UI", 13, "bold"), bg="#0d6efd", fg="#fff", activebackground="#2563eb", activeforeground="#fff", command=self.run_analysis, borderwidth=0, padx=20, pady=5)
        self.btn_run.pack(pady=5)

        frame_table = tk.Frame(self, bg="#e3eafc")
        frame_table.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#f4f7ff", foreground="#222", rowheight=28, fieldbackground="#f4f7ff", font=("Segoe UI", 11))
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background="#e3eafc", foreground="#0d6efd")
        style.map("Treeview", background=[('selected', '#dbeafe')])
        self.tree = ttk.Treeview(frame_table, columns=("Tempo", "Tamanho", "Resultado", "Complexidade"), show="headings")
        self.tree.heading("Tempo", text="Tempo (s)")
        self.tree.heading("Tamanho", text="Tamanho do Código")
        self.tree.heading("Resultado", text="Resultado")
        self.tree.heading("Complexidade", text="Complexidade")
        self.tree.column("Tempo", width=120, anchor="center")
        self.tree.column("Tamanho", width=140, anchor="center")
        self.tree.column("Resultado", width=300, anchor="w")
        self.tree.column("Complexidade", width=200, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.frame_complex = tk.Frame(self, bg="#e3eafc")
        self.frame_complex.pack(fill=tk.X, padx=20, pady=(0, 15))
        self.lbl_complex = tk.Label(
            self.frame_complex,
            text="Complexidade ajustada aparecerá aqui",
            font=("Segoe UI", 15, "bold"),
            bg="#e0f2fe",
            fg="#0d6efd",
            relief="groove",
            bd=2,
            padx=10,
            pady=10
        )
        self.lbl_complex.pack(fill=tk.X)

    def run_analysis(self):
        self.tree.delete(*self.tree.get_children())
        code = self.txt_code.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("Aviso", "Digite ou cole um código Python para analisar!")
            return

        tempos = []
        tamanhos = []
        resultados = []
        ops_count = None
        resultado_vazio = True

        try:
            exec_env = {}
            exec(code, exec_env)
            funcs = [v for v in exec_env.values() if callable(v)]

            if not funcs:
                t0 = time.perf_counter()
                exec(code, exec_env)
                t1 = time.perf_counter()
                tempo = t1 - t0
                resultado = str(exec_env)
                tempos.append(tempo)
                tamanhos.append(len(code))
                resultados.append(resultado)
            else:
                def count_recursive_calls(func_name, code):
                    pattern = rf'{func_name}\s*\('
                    return len(re.findall(pattern, code))
                for func in funcs:
                    sig = inspect.signature(func)
                    func_name = func.__name__
                    recursive_calls = count_recursive_calls(func_name, code)

                    is_fib = "fib" in func_name.lower()
                    is_exponential = recursive_calls >= 2  # Mais de 1 chamada recursiva = potencial exponencial

                    if is_fib or is_exponential:
                        # Valores maiores e espaçados para recursivas/exponenciais
                        test_sizes = sorted(random.sample(range(5, 31, 5), 5))
                    else:
                        # Valores maiores e espaçados para funções normais
                        test_sizes = sorted(random.sample(range(10, 201, 20), 5))

                    for mult in test_sizes:

                        args = generate_args(sig)
                        if args and isinstance(args[0], list):
                            args[0] = list(range(mult, 0, -1))
                        elif args and isinstance(args[0], (str, tuple, dict)):
                            args[0] = type(args[0])([i for i in range(mult)])
                        elif args:
                            try:
                                args[0] = mult
                            except Exception:
                                args[0] = 1

                        # Executa múltiplas vezes para tirar média e reduzir ruído
                        num_runs = 3
                        tempos_exec = []
                        for _ in range(num_runs):
                            t0 = time.perf_counter()
                            result = func(*args)
                            t1 = time.perf_counter()
                            tempos_exec.append(t1 - t0)
                        tempo = sum(tempos_exec) / num_runs

                        if args and isinstance(args[0], list):
                            tamanho = len(args[0])
                        elif args and isinstance(args[0], (str, tuple, dict)):
                            tamanho = len(args[0])
                        elif args:
                            try:
                                tamanho = int(args[0])
                            except Exception:
                                tamanho = 1
                        else:
                            tamanho = 1

                        resultado = str(result)
                        if resultado:
                            resultado_vazio = False
                        tempos.append(tempo)
                        tamanhos.append(tamanho)
                        resultados.append(resultado)

            if resultado_vazio:
                messagebox.showwarning("Aviso", "O código não produziu nenhum resultado. Por favor, insira um código válido que gere algum resultado.")
                self.lbl_complex.config(text="Complexidade: -\nTécnica: -")
                return

            model, mape, a = fit_complexity(tamanhos, tempos)
            complexidade_str = f"{model} | MAPE: {mape:.3f} | a: {a:.3g}"
            for i in range(len(tempos)):
                self.tree.insert("", "end", values=(f"{tempos[i]:.6f}", tamanhos[i], resultados[i], complexidade_str))
            
            # Análise estática para identificar técnicas
            tecnica = []

            # Recursão: chamada da própria função
            if re.search(r'def\s+(\w+)\s*\(.*\):[\s\S]*?\1\s*\(', code):
                tecnica.append('Recursivo')

            # Dividir para conquistar: uso de divisão e chamadas recursivas
            if re.search(r'(divid|metade|meio|split)', code, re.IGNORECASE) and 'return' in code and re.search(r'def\s+(\w+)\s*\(.*\):[\s\S]*?\1\s*\(', code):
                tecnica.append('Dividir para Conquistar')

            # Programação dinâmica: uso de cache, memoização ou tabelas
            if re.search(r'(memo|cache|dp|tabela)', code, re.IGNORECASE):
                tecnica.append('Programação Dinâmica')

            # Iteração: presença de laços
            if 'for' in code or 'while' in code:
                tecnica.append('Iterativo')

            # Busca binária: uso de meio, comparação com alvo
            if re.search(r'(meio|mid|target|busca_binaria)', code, re.IGNORECASE):
                tecnica.append('Busca Binária')

            # Força bruta: múltiplos loops ou tentativas
            # Recursão sem otimização = força bruta
            if re.search(r'def\s+(\w+)\s*\(.*\):[\s\S]*?\1\s*\(', code) and not re.search(r'(memo|cache|lru_cache)', code, re.IGNORECASE):
                tecnica.append('Força Bruta')


            # Fallback
            tecnica_str = ', '.join(tecnica) if tecnica else 'Não identificado'


            msg = f"Complexidade: {complexidade_str}\nTécnica: {tecnica_str}"
            if ops_count is not None:
                msg += f"\nOperações básicas: {ops_count}"
            self.lbl_complex.config(text=msg)

        except Exception as e:
            messagebox.showerror("Erro", str(e))

if __name__ == "__main__":
    app = App()
    app.mainloop()
