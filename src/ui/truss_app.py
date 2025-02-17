import tkinter as tk
from tkinter import ttk
import numpy as np

from models.truss_node import TrussNode
from models.truss_bar import TrussBar

class TrussApp:
    def __init__(self, root):
        self.root = root
        self.nodes = []
        self.bars = []
        self.setup_gui()
        
    def setup_gui(self):
        self.root.title("Análise de Treliça 2D")
        self.root.state('zoomed') 
        
        # Frames
        input_frame = ttk.Frame(self.root, padding=10)
        input_frame.grid(row=0, column=0, sticky=tk.N)
        
        canvas_frame = ttk.Frame(self.root, padding=10)
        canvas_frame.grid(row=0, column=1)
        
        # Widgets de entrada
        ttk.Label(input_frame, text="Nó X:").grid(row=0, column=0)
        self.node_x = ttk.Entry(input_frame, width=10)
        self.node_x.grid(row=0, column=1)
        
        ttk.Label(input_frame, text="Nó Y:").grid(row=1, column=0)
        self.node_y = ttk.Entry(input_frame, width=10)
        self.node_y.grid(row=1, column=1)

        ttk.Button(input_frame, text="Adicionar Nó", command=self.add_node).grid(row=2, column=0, columnspan=2)
        ttk.Button(input_frame, text="Apagar Nó", command=self.delete_node).grid(row=3, column=0, columnspan=2)
        
        ttk.Label(input_frame, text="Nó Inicial:").grid(row=4, column=0)
        self.bar_start = ttk.Entry(input_frame, width=10)
        self.bar_start.grid(row=4, column=1)
        
        ttk.Label(input_frame, text="Nó Final:").grid(row=5, column=0)
        self.bar_end = ttk.Entry(input_frame, width=10)
        self.bar_end.grid(row=5, column=1)
        
        ttk.Label(input_frame, text="E (MPa):").grid(row=6, column=0)
        self.bar_E = ttk.Entry(input_frame, width=10)
        self.bar_E.grid(row=6, column=1)
        self.bar_E.insert(0, "210000")
        
        ttk.Label(input_frame, text="A (mm²):").grid(row=7, column=0)
        self.bar_A = ttk.Entry(input_frame, width=10)
        self.bar_A.grid(row=7, column=1)
        self.bar_A.insert(0, "100")

        ttk.Button(input_frame, text="Adicionar Barra", command=self.add_bar).grid(row=8, column=0, columnspan=2)
        
        ttk.Label(input_frame, text="Nó para Força:").grid(row=9, column=0)
        self.force_node = ttk.Entry(input_frame, width=10)
        self.force_node.grid(row=9, column=1)
        
        ttk.Label(input_frame, text="Fx (N):").grid(row=10, column=0)
        self.force_x = ttk.Entry(input_frame, width=10)
        self.force_x.grid(row=10, column=1)
        
        ttk.Label(input_frame, text="Fy (N):").grid(row=11, column=0)
        self.force_y = ttk.Entry(input_frame, width=10)
        self.force_y.grid(row=11, column=1)
        
        ttk.Button(input_frame, text="Aplicar Força", command=self.apply_force).grid(row=12, column=0, columnspan=2)
        
        ttk.Label(input_frame, text="Nó para Apoio:").grid(row=13, column=0)
        self.support_node = ttk.Entry(input_frame, width=10)
        self.support_node.grid(row=13, column=1)
        
        self.support_x = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Fixar X", variable=self.support_x).grid(row=14, column=0)
        self.support_y = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Fixar Y", variable=self.support_y).grid(row=14, column=1)

        ttk.Button(input_frame, text="Aplicar Apoio", command=self.apply_support).grid(row=15, column=0, columnspan=2)
        
        ttk.Button(input_frame, text="Resolver", command=self.solve).grid(row=16, column=0, columnspan=2)
        
        footer_label = ttk.Label(input_frame, text="Autor: Joab Manoel Almeida Santos\n(UFAL-LCCV)")
        footer_label.grid(row=17, column=0, columnspan=2, sticky="we", pady=20)
        
        # Canvas
        self.canvas = tk.Canvas(canvas_frame, width=1400, height=800, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Desenhar eixos no ponto (0,0) em coordenadas do canvas
        # Conversão: x = node.x * 50 + 300 e y = 350 - node.y * 50.
        origin_x = 0 * 50 + 300  # 300
        origin_y = 350 - 0 * 50  # 350
        arrow_size = 30
        # Eixo X (da esquerda para a direita)
        self.canvas.create_line(origin_x, origin_y, origin_x + arrow_size, origin_y,
                                arrow=tk.LAST, fill="green", width=2)
        self.canvas.create_text(origin_x + arrow_size + 10, origin_y,
                                text="X", fill="green", anchor="w")
        # Eixo Y (de baixo para cima)
        self.canvas.create_line(origin_x, origin_y, origin_x, origin_y - arrow_size,
                                arrow=tk.LAST, fill="green", width=2)
        self.canvas.create_text(origin_x, origin_y - arrow_size - 10,
                                text="Y", fill="green", anchor="s")
        
    def add_node(self):
        try:
            x = float(self.node_x.get())
            y = float(self.node_y.get())
            # Verificar se já existe um nó com coordenadas semelhantes (tolerância de 1e-6)
            for node in self.nodes:
                if abs(node.x - x) < 1e-6 and abs(node.y - y) < 1e-6:
                    return  # Nó já existe, não cria um novo
            node = TrussNode(len(self.nodes) + 1, x, y)
            self.nodes.append(node)
            self.draw_node(node)
        except ValueError:
            pass

    def delete_node(self):
        # Verifica se um nó foi selecionado (através do clique no canvas)
        if hasattr(self, 'selected_node') and self.selected_node:
            node_to_delete = self.selected_node

            # Remove o nó da lista de nós
            self.nodes.remove(node_to_delete)

            # Remove as barras conectadas ao nó excluído
            self.bars = [bar for bar in self.bars if bar.start != node_to_delete and bar.end != node_to_delete]

            # Limpar todo o canvas
            self.canvas.delete("all")

            # Redesenhar os eixos
            origin_x = 300
            origin_y = 350
            arrow_size = 30
            self.canvas.create_line(origin_x, origin_y, origin_x + arrow_size, origin_y,
                                    arrow=tk.LAST, fill="green", width=2)
            self.canvas.create_text(origin_x + arrow_size + 10, origin_y,
                                    text="X", fill="green", anchor="w")
            self.canvas.create_line(origin_x, origin_y, origin_x, origin_y - arrow_size,
                                    arrow=tk.LAST, fill="green", width=2)
            self.canvas.create_text(origin_x, origin_y - arrow_size - 10,
                                    text="Y", fill="green", anchor="s")

            # Redesenhar as barras restantes
            for bar in self.bars:
                self.draw_bar(bar)

            # Redesenhar os nós restantes
            for node in self.nodes:
                self.draw_node(node)

            self.selected_node = None


    def on_canvas_click(self, event):
        # Converter coordenadas do canvas para as coordenadas do nó
        # Inversão da conversão: node.x = (canvas_x - 300) / 50, node.y = (350 - canvas_y) / 50
        x_click = event.x
        y_click = event.y
        tol_canvas = 5  # tolerância em pixels para detecção
        self.selected_node = None
        self.canvas.delete("selection")
        for node in self.nodes:
            x_node = node.x * 50 + 300
            y_node = 350 - node.y * 50
            if abs(x_click - x_node) <= tol_canvas and abs(y_click - y_node) <= tol_canvas:
                self.selected_node = node
                # Destaque visual do nó selecionado
                self.canvas.create_oval(x_node - 8, y_node - 8, x_node + 8, y_node + 8,
                                        outline="red", width=2, tag="selection")
                break
    def on_delete_key(self, event):
        self.delete_node()
            
    def add_bar(self):
        try:
            start = int(self.bar_start.get()) - 1
            end = int(self.bar_end.get()) - 1
            E = float(self.bar_E.get())
            A = float(self.bar_A.get())
            bar = TrussBar(len(self.bars) + 1, self.nodes[start], self.nodes[end], E, A)
            self.bars.append(bar)
            self.draw_bar(bar)
        except (ValueError, IndexError):
            pass
        
    def apply_force(self):
        try:
            node = int(self.force_node.get()) - 1
            fx = float(self.force_x.get())
            fy = float(self.force_y.get())
            self.nodes[node].forces = [fx, fy]

            # Remover desenhos anteriores da força no nó (identificados pela tag)
            tag = f"force_{node}"
            self.canvas.delete(tag)

            # Converter coordenadas do nó para o canvas
            x = self.nodes[node].x * 50 + 300
            y = 350 - self.nodes[node].y * 50

            arrow_scale = 50  # Fator de escala para representação da força

            # Desenhar a seta representando a força horizontal (Fx)
            if fx != 0:
                # Seta: para a direita se fx positivo, para a esquerda se negativo
                x_end = x + (fx / abs(fx)) * arrow_scale
                self.canvas.create_line(x, y, x_end, y, arrow=tk.LAST, fill="red", width=2, tags=tag)
                self.canvas.create_text((x + x_end) / 2, y - 10, text=f"Fx: {fx:.2f} N", fill="red", tags=tag)

            # Desenhar a seta representando a força vertical (Fy)
            if fy != 0:
                # Seta: para cima se fy positivo, para baixo se negativo
                y_end = y - (fy / abs(fy)) * arrow_scale  # subtrai para que o positivo fique para cima
                self.canvas.create_line(x, y, x, y_end, arrow=tk.LAST, fill="red", width=2, tags=tag)
                self.canvas.create_text(x - 30, (y + y_end) / 2, text=f"Fy: {fy:.2f} N", fill="red", tags=tag)
        except (ValueError, IndexError):
            pass
            
    def apply_support(self):
        try:
            node = int(self.support_node.get()) - 1
            self.nodes[node].constraints = [self.support_x.get(), self.support_y.get()]
            # Redesenhar o nó para mostrar o apoio
            self.draw_node(self.nodes[node])
        except (ValueError, IndexError):
            pass
            
    def draw_node(self, node):
        # Converter coordenadas para o canvas
        x = node.x * 50 + 300
        y = 350 - node.y * 50
        
        # Desenhar nó
        self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="black")
        self.canvas.create_text(x + 10, y + 10, text=str(node.id))
        
        # Desenhar apoio, de acordo com os apoios solicitados
        if node.constraints[0] and node.constraints[1]:
            # Suporte em x e y: desenha o mesmo triângulo invertido (ponta em node)
            points = [x, y, x - 20, y + 20, x + 20, y + 20]
            self.canvas.create_polygon(points, fill="black")
        elif node.constraints[1]:
            # Suporte apenas vertical: desenha o triângulo invertido e adiciona uma reta horizontal abaixo da base
            points = [x, y, x - 20, y + 20, x + 20, y + 20]
            self.canvas.create_polygon(points, fill="black")
            # Reta horizontal com o mesmo tamanho da base, deslocada 10 pixels para baixo
            self.canvas.create_line(x - 20, y + 20 + 7, x + 20, y + 20 + 7, fill="black", width=2)
        elif node.constraints[0]:
            # Suporte apenas horizontal: desenha o triângulo na horizontal (direcionado para a direita)
            points = [x, y, x + 20, y - 20, x + 20, y + 20]
            self.canvas.create_polygon(points, fill="black")
            # Reta horizontal com o mesmo tamanho da base, deslocada 10 pixels para baixo
            self.canvas.create_line(x + 20, y - 20 - 7, x + 20, y + 20 + 7, fill="black", width=2)
        
    def draw_bar(self, bar):
        x1 = bar.start.x * 50 + 300
        y1 = 350 - bar.start.y * 50
        x2 = bar.end.x * 50 + 300
        y2 = 350 - bar.end.y * 50
        self.canvas.create_line(x1, y1, x2, y2, fill="blue")
        self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=str(bar.id))

    def solve(self):
        n_nodes = len(self.nodes)
        K = np.zeros((2 * n_nodes, 2 * n_nodes))
        
        for bar in self.bars:
            dx = bar.end.x - bar.start.x
            dy = bar.end.y - bar.start.y
            L = bar.length
            c = dx / L
            s = dy / L
            k = (bar.E * bar.A) / L
            Ke = k * np.array([
                [ c*c,   c*s, -c*c, -c*s],
                [ c*s,   s*s, -c*s, -s*s],
                [-c*c,  -c*s,  c*c,   c*s],
                [-c*s,  -s*s,  c*s,   s*s]
            ])
            
            start_idx = 2 * (bar.start.id - 1)
            end_idx = 2 * (bar.end.id - 1)
            indices = [start_idx, start_idx + 1, end_idx, end_idx + 1]
            
            for i in range(4):
                for j in range(4):
                    K[indices[i], indices[j]] += Ke[i, j]

        F = np.zeros(2 * n_nodes)
        for i, node in enumerate(self.nodes):
            F[2 * i] = node.forces[0]
            F[2 * i + 1] = node.forces[1]
        
        dof_remove = []
        for i, node in enumerate(self.nodes):
            if node.constraints[0]:
                dof_remove.append(2 * i)
            if node.constraints[1]:
                dof_remove.append(2 * i + 1)
        
        K_modified = np.delete(np.delete(K, dof_remove, axis=0), dof_remove, axis=1)
        F_modified = np.delete(F, dof_remove)
        
        try:
            U_modified = np.linalg.solve(K_modified, F_modified)
        except np.linalg.LinAlgError:
            print("Sistema singular. Verifique a estabilidade da treliça.")
            return

        U = np.zeros(2 * n_nodes)
        keep_mask = np.ones(2 * n_nodes, dtype=bool)
        keep_mask[dof_remove] = False
        U[keep_mask] = U_modified
        
        for bar in self.bars:
            dx = bar.end.x - bar.start.x
            dy = bar.end.y - bar.start.y
            L = bar.length
            c = dx / L
            s = dy / L
            
            start_idx = 2 * (bar.start.id - 1)
            end_idx = 2 * (bar.end.id - 1)
            u = np.array([
                U[start_idx],
                U[start_idx + 1],
                U[end_idx],
                U[end_idx + 1]
            ])
            
            strain = (-c * u[0] - s * u[1] + c * u[2] + s * u[3]) / L
            bar.normal_force = bar.E * bar.A * strain

        self.show_results(U)
        
    def show_results(self, displacements):
        result_window = tk.Toplevel(self.root)
        result_window.title("Resultados")
        
        ttk.Label(result_window, text="Deslocamentos dos Nós:").pack()
        for i, node in enumerate(self.nodes):
            dx = displacements[2 * i]
            dy = displacements[2 * i + 1]
            ttk.Label(result_window, text=f"Nó {node.id}: dx={dx:.4e} mm, dy={dy:.4e} mm").pack()
        
        ttk.Label(result_window, text="\nEsforços Normais nas Barras:").pack()
        for bar in self.bars:
            ttk.Label(result_window, text=f"Barra {bar.id}: N={bar.normal_force:.2f} N").pack()