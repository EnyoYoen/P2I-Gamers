from itertools import dropwhile, takewhile
import random
from tkinter import Frame, Tk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class Graphs:
	def __init__(self, root, graphs_class, plot_args={}):
		self.root = root
		self.fig = plt.figure()

		self.canvas = FigureCanvasTkAgg(self.fig, master = self.root) 

		self.canvas.get_tk_widget().pack(expand=True, fill='both')

		self.graphs = {}
		self.update_queue = list()
		for i, (name, graph) in enumerate(graphs_class.items()):
			self.graphs[name] = graph(self.fig, 221 + i, **plot_args.get(name, {}))

			self.update_queue.append(name)

	def plot(self):
		if len(self.update_queue) == 0:
			return

		for graphtype in set(self.update_queue):
			if graphtype not in self.graphs:
				continue
			self.graphs[graphtype].plot()

		self.update_queue = []

		self.canvas.draw()
		self.root.update_idletasks()

	def add_data(self, graph, *data, **kwargs):
		if graph not in self.graphs:
			return

		self.graphs[graph].add_data(*data, **kwargs)

	def callback(self, func, timeout):
		def wrapper():
			self.root.after(timeout, wrapper)
			func()
			self.plot()

		self.root.after(timeout, wrapper)

	def update(self, graph):
		self.update_queue.append(graph)

class SubGraph:
	SUBPLOT_ARGS = {}
	def __init__(self, fig, pos, **kwargs) -> None:
		self.data = []
		self.ax = fig.add_subplot(pos, **self.SUBPLOT_ARGS|kwargs)
		
	def add_data(self, index, data, limit=None, value_limit=None, **kwargs):
		while len(self.data) <= index:
			self.data.append([])

		for i, row in enumerate(data):
			while len(self.data[index]) <= i:
				self.data[index].append([])

			self.data[index][i].extend(row)
			if limit is not None:
				if len(self.data[index][i]) > limit:
					self.data[index][i] = self.data[index][i][-limit:]

		if value_limit is not None:
			xs = list(takewhile(lambda e: e<value_limit, self.data[index][0]))
			if len(xs) > 0:
				size = len(self.data[index][0])-len(xs)
				for i in range(len(self.data[index])):
					self.data[index][i] = self.data[index][i][-size:]

	def plot_func(self, *data):
		return self.ax.plot(*data)

	def plot(self):
		if len(self.data) == 0:
			return
		self.ax.clear()

		for rows in self.data:
			if len(rows) == 0:
				continue
			try:
				self.plot_func(*rows)
			except Exception as e:
				print(e)

class LineGraph(SubGraph):
	pass

class Graph3D(SubGraph):
	SUBPLOT_ARGS = {'projection': '3d'}

class BoxPlot(SubGraph):
	def plot_func(self, *data):
		self.ax.boxplot(*data)

if __name__ == "__main__":
	fen = Tk()
	parent = Frame(fen)
	
	graphs_class = {
		'line': LineGraph,
		'3D': Graph3D,
		'boxplot': BoxPlot,
		'line2': LineGraph,
	}
	g = Graphs(parent, graphs_class)
 
	g.add_data('line', 0, [1, 2, 3], [4, 5, 6])
	g.add_data('line', 0, [4], [5])
	g.add_data('line', 2, range(20), random.choices(range(6), k=20))
	phases=(np.pi/2, 0, -np.pi/2, -np.pi)
	for i, phase in enumerate(phases):
		# Prepare arrays x, y, z
		theta = np.linspace(-4 * np.pi + phase, 4 * np.pi + phase, 100)
		z = np.linspace(-2, 2, 100)
		r = z**2 + 1
		x = r * np.sin(theta)
		y = r * np.cos(theta)
  
		g.add_data('3D', i, x, y, z)
  
  
	g.add_data('boxplot', 0, [random.choices(range(100), k=20), random.choices(range(100), k=20)])

	func_ind = 0
	def func():
		global func_ind
		# n = random.randint(0, 5)
		n = 5
		for i in range(2):
			g.add_data('line2', i, range(func_ind, func_ind+n), random.choices(range(6), k=n), limit=20)
		# g.plot()
		func_ind += n
		g.update('line2')

	g.callback(func, 1000)

	g.plot()

	parent.pack()
	fen.mainloop()