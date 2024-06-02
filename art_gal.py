import tkinter as tk
from tkinter import filedialog, messagebox
import pol_vis
import pltri
import mcoloring

class ArtGalleryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Art Gallery Problem")
        self.root.geometry("720x512")
        self.canvas = tk.Canvas(self.root, bg="white", width=720, height=512)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.init_ui()

        self.lock = 0
        self.pts = []
        self.points = []
        self.count = 0

        self.variations = [[], [], []]
        self.validColors = []
        self.currVariationDisplayed = 0
        self.guardSelected = 0
        self.processed = 0
        self.stepsFinish = 0
        self.triangles = []
        self.ears = []
        self.triI = -1
        self.coloring3 = []
        self.colI = -1
        self.triPts = []

    def init_ui(self):
        self.status_var = tk.StringVar()
        self.label1_var = tk.StringVar()
        self.label2_var = tk.StringVar()
        
        self.status_label = tk.Label(self.root, textvariable=self.status_var, anchor='w', bg="white")
        self.status_label.pack(side=tk.TOP, fill=tk.X)
        
        self.label1 = tk.Label(self.root, textvariable=self.label1_var, anchor='w', bg="white")
        self.label1.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.label2 = tk.Label(self.root, textvariable=self.label2_var, anchor='w', bg="white")
        self.label2.pack(side=tk.BOTTOM, fill=tk.X)

        self.label1_var.set("Place first point (Left Click), Load Polygon from file (Space)")
        self.label2_var.set("")
        self.status_var.set("Start by building a polygon or loading a polygon from a file")

        self.canvas.bind("<Button-1>", self.on_left_click)
        self.root.bind("<space>", self.load_polygon)
        self.root.bind("<Return>", self.on_enter)
        self.root.bind("<Right>", self.on_right)
        self.root.bind("<Left>", self.on_left)
        self.root.bind("<Up>", self.on_up)
        self.root.bind("<Down>", self.on_down)
        self.root.bind("<BackSpace>", self.on_backspace)

    def _intersection(self, P1, P2, P3):
        return (P3[1] - P1[1]) * (P2[0] - P1[0]) > (P2[1] - P1[1]) * (P3[0] - P1[0])

    def find_intersection(self, S1x, S1y, D1x, D1y, S2x, S2y, D2x, D2y):
        return self._intersection([S1x, S1y], [S2x, S2y], [D2x, D2y]) != self._intersection([D1x, D1y], [S2x, S2y], [D2x, D2y]) and self._intersection([S1x, S1y], [D1x, D1y], [S2x, S2y]) != self._intersection([S1x, S1y], [D1x, D1y], [D2x, D2y])

    def display_status(self, status_msg):
        self.status_var.set(status_msg)

    def display_label1(self, label_msg):
        self.label1_var.set(label_msg)

    def display_label2(self, label_msg):
        self.label2_var.set(label_msg)

    def draw_polygon(self):
        for i in range(len(self.points) - 1):
            self.canvas.create_line(self.points[i], self.points[i + 1], fill="blue")
            self.canvas.create_text(self.points[i], text=str(i), anchor="nw", font=("Comic Sans MS", 10))
        self.canvas.create_line(self.points[-1], self.points[0], fill="blue")
        self.canvas.create_text(self.points[-1], text=str(len(self.points) - 1), anchor="nw", font=("Comic Sans MS", 10))

    def display_variation(self, variation, guard):
        self.canvas.delete("all")
        self.display_label1("Switch between Variations (LEFT or RIGHT), Switch guard visibility (UP or DOWN),")
        self.display_label2("Reset (BACKSPACE)")
        self.display_status(f"The no. of guards sufficient to guard the gallery are {len(variation)}. Displaying Variation {self.currVariationDisplayed + 1} out of {len(self.validColors)}")

        self.draw_polygon()
        if guard == 0:
            for p in variation:
                self.canvas.create_oval(p[1][0] - 5, p[1][1] - 5, p[1][0] + 5, p[1][1] + 5, fill="red", outline="")
        else:
            self.display_status("Loading...")
            visibility = pol_vis.computeVisibility(self.points, variation[guard - 1][1])
            self.canvas.create_polygon(visibility, fill="blue")
            self.canvas.create_oval(variation[guard - 1][1][0] - 5, variation[guard - 1][1][1] - 5, variation[guard - 1][1][0] + 5, variation[guard - 1][1][1] + 5, fill="black")

            self.display_status(f"Visibility for variation {self.currVariationDisplayed + 1}'s guard no. {guard} out of {len(variation)}")

    def process(self):
        gen = pltri.triangulate_poly(self.pts)
        adj_matrix = [[0 for __ in range(self.count)] for _ in range(self.count)]

        for x in gen:
            self.triangles.append(x[0])
            self.ears.append(x[1])
            x = x[0]
            adj_matrix[x[0][2]][x[1][2]] = 1
            adj_matrix[x[1][2]][x[0][2]] = 1
            adj_matrix[x[2][2]][x[1][2]] = 1
            adj_matrix[x[1][2]][x[2][2]] = 1
            adj_matrix[x[2][2]][x[0][2]] = 1
            adj_matrix[x[0][2]][x[2][2]] = 1

        g = mcoloring.Graph(self.count)
        g.graph = adj_matrix
        m = 3
        coloring = g.graphColouring(m)

        i = 0
        rgbCount = [0, 0, 0]
        for c in coloring:
            self.coloring3.append(c)
            rgbCount[c - 1] += 1
            self.variations[c - 1].append([i, self.pts[i][:2]])
            i += 1
        rgbMin = min(rgbCount)
        for i in range(len(rgbCount)):
            if rgbCount[i] == rgbMin:
                self.validColors.append(i)
        self.currVariationDisplayed = 0
        self.guardSelected = 0

    def display_next(self, i):
        if i < len(self.triangles):
            self.canvas.create_polygon([self.triangles[i][0][:2], self.triangles[i][1][:2], self.triangles[i][2][:2]], fill="red")
            self.canvas.create_line(self.triangles[i][0][:2], self.triangles[i][1][:2], self.triangles[i][2][:2], self.triangles[i][0][:2], fill="blue")
            self.canvas.create_oval(self.ears[i][0] - 8, self.ears[i][1] - 8, self.ears[i][0] + 8, self.ears[i][1] + 8, fill="green")

    def display_prev(self, index, mode):
        indexTri = index
        if mode == 1:
            indexTri = len(self.triangles) - 1

        if mode == 0:
            self.canvas.delete("all")
            self.display_label1("Next step (RIGHT), Previous step (LEFT),")
            self.display_label2("Reset (BACKSPACE)")
            self.display_status("Running Ear-clipping Triangulation algorithm")
            self.draw_polygon()

            i = -1
            while i < indexTri:
                i += 1
                self.display_next(i)

        if mode == 1:
            self.display_triangulated()
            i = -1
            self.display_status("Running 3-coloring algorithm")
            self.display_label1("Next step (RIGHT), Previous step (LEFT),")
            self.display_label2("Reset (BACKSPACE)")
            while i < index:
                i += 1
                self.display_3colors(i)

    def display_triangulated(self):
        self.canvas.delete("all")
        self.display_status("Displaying Triangulated Polygon")
        self.display_label1("Next step (RIGHT), Previous step (LEFT),")
        self.display_label2("Reset (BACKSPACE)")

        for tri in self.triangles:
            if [tri[0][0], tri[0][1]] not in self.triPts:
                self.triPts.append([tri[0][0], tri[0][1]])
            if [tri[1][0], tri[1][1]] not in self.triPts:
                self.triPts.append([tri[1][0], tri[1][1]])
            if [tri[2][0], tri[2][1]] not in self.triPts:
                self.triPts.append([tri[2][0], tri[2][1]])
            self.canvas.create_line([tri[0][:2], tri[1][:2], tri[2][:2]], fill="blue")

    def display_3colors(self, i):
        index = -1
        for pt in self.points:
            index += 1
            if self.triPts[i] == pt[:2]:
                break
        self.canvas.create_oval(self.triPts[i][0] - 5, self.triPts[i][1] - 5, self.triPts[i][0] + 5, self.triPts[i][1] + 5, fill="red" if self.coloring3[index] == 1 else "green" if self.coloring3[index] == 2 else "blue")

    def on_left_click(self, event):
        if self.lock != 1:
            self.display_label1("Finish Polygon (ENTER),")
            self.display_label2("Reset (BACKSPACE)")
            self.display_status("Continue adding vertices of the polygon, or press 'ENTER' to complete the Polygon")

            intersection = False
            for i in range(len(self.pts) - 2):
                if self.find_intersection(event.x, event.y, self.pts[-1][0], self.pts[-1][1], self.pts[i][0], self.pts[i][1], self.pts[i + 1][0], self.pts[i + 1][1]):
                    intersection = True
                    break
            if not intersection:
                pt = [event.x, event.y, self.count]
                self.count += 1
                self.pts.append(pt)
                self.points.append(pt[:2])
                self.canvas.create_oval(event.x - 3, event.y - 3, event.x + 3, event.y + 3, fill="black")
                self.canvas.create_text(event.x, event.y, text=str(self.count - 1), anchor="nw", font=("Comic Sans MS", 10))
                if len(self.pts) > 1:
                    self.canvas.create_line(self.pts[-2][:2], self.pts[-1][:2], fill="blue")
            else:
                self.display_status("Cannot insert this vertex as it doesn't produce a simple polygon. Please try again.")

    def load_polygon(self, event):
        if self.lock != 1:
            path = filedialog.askopenfilename()
            if not path:
                return
            intersection = False
            with open(path) as dataFile:
                for line in dataFile:
                    lineSplit = line.split()
                    currPt = [int(lineSplit[0]), int(lineSplit[1])]
                    for i in range(len(self.pts) - 2):
                        if self.find_intersection(currPt[0], currPt[1], self.pts[-1][0], self.pts[-1][1], self.pts[i][0], self.pts[i][1], self.pts[i + 1][0], self.pts[i + 1][1]):
                            intersection = True
                            break
                    if not intersection:
                        pt = [currPt[0], currPt[1], self.count]
                        self.count += 1
                        self.pts.append(pt)
                        self.points.append(pt[:2])
                        self.canvas.create_oval(currPt[0] - 3, currPt[1] - 3, currPt[0] + 3, currPt[1] + 3, fill="black")
                        self.canvas.create_text(currPt[0], currPt[1], text=str(self.count - 1), anchor="nw", font=("Comic Sans MS", 10))
                        if len(self.pts) > 1:
                            self.canvas.create_line(self.pts[-2][:2], currPt, fill="blue")
                    else:
                        break

            self.display_label1("Run (ENTER), Run step-by-step automatically (SPACE), Run step-by-step manually (RIGHT),")
            self.display_label2("Reset (BACKSPACE)")
            self.display_status("Choose an option to run the Algorithm")
            if not intersection:
                for i in range(1, len(self.pts) - 2):
                    if self.find_intersection(self.pts[-1][0], self.pts[-1][1], self.pts[0][0], self.pts[0][1], self.pts[i][0], self.pts[i][1], self.pts[i + 1][0], self.pts[i + 1][1]):
                        intersection = True
                        break

            if not intersection:
                self.canvas.create_line(self.pts[-1][:2], self.pts[0][:2], fill="blue")
                self.lock = 1
            else:
                self.canvas.delete("all")
                self.lock = 0
                self.pts = []
                self.points = []
                self.count = 0
                self.variations = [[], [], []]
                self.validColors = []
                self.currVariationDisplayed = 0
                self.guardSelected = 0
                self.processed = 0
                self.stepsFinish = 0
                self.triangles = []
                self.ears = []
                self.triI = -1
                self.coloring3 = []
                self.colI = -1
                self.triPts = []

                self.display_label1("Place first point (Left Click), Load Polygon from file (Space),")
                self.display_label2("Reset (BACKSPACE)")
                self.display_status("Cannot create simple polygon. Vertex doesn't produce a simple polygon.")

    def on_enter(self, event):
        if self.lock == 1:
            self.process()
            self.processed = 1
            self.stepsFinish = 1
            self.display_variation(self.variations[self.validColors[self.currVariationDisplayed]], self.guardSelected)
        elif len(self.pts) > 2:
            self.display_label1("Run (ENTER), Run step-by-step automatically (SPACE), Run step-by-step manually (RIGHT),")
            self.display_label2("Reset (BACKSPACE)")
            self.display_status("Choose an option to run the Algorithm")
            intersection = False
            for i in range(1, len(self.pts) - 2):
                if self.find_intersection(self.pts[-1][0], self.pts[-1][1], self.pts[0][0], self.pts[0][1], self.pts[i][0], self.pts[i][1], self.pts[i + 1][0], self.pts[i + 1][1]):
                    intersection = True
                    break

            if not intersection:
                self.canvas.create_line(self.pts[-1][:2], self.pts[0][:2], fill="blue")
                self.lock = 1
            else:
                self.display_status("Cannot insert this vertex as it doesn't produce a simple polygon. Please try again.")

    def on_right(self, event):
        if self.lock == 1 and self.stepsFinish == 1:
            self.currVariationDisplayed = (self.currVariationDisplayed + 1) % len(self.validColors)
            self.guardSelected = 0
            self.display_variation(self.variations[self.validColors[self.currVariationDisplayed]], self.guardSelected)
        elif self.lock == 1 and self.stepsFinish == 0:
            if self.processed != 1:
                self.process()
                self.processed = 1

            if self.triI < len(self.triangles) - 1:
                self.display_status("Running Ear-clipping Triangulation algorithm")
                self.display_label1("Next step (RIGHT), Previous step (LEFT),")
                self.display_label2("Reset (BACKSPACE)")
                self.triI += 1
                self.display_next(self.triI)
            elif self.triI == len(self.triangles) - 1:
                self.triI += 1
                self.display_triangulated()
            else:
                if self.colI < len(self.points) - 1:
                    self.display_status("Running 3-coloring algorithm")
                    self.display_label1("Next step (RIGHT), Previous step (LEFT),")
                    self.display_label2("Reset (BACKSPACE)")
                    self.colI += 1
                    self.display_3colors(self.colI)
                elif self.colI == len(self.points) - 1:
                    self.colI += 1
                    self.stepsFinish = 1
                    self.display_variation(self.variations[self.validColors[self.currVariationDisplayed]], self.guardSelected)

    def on_left(self, event):
        if self.lock == 1 and self.stepsFinish == 1:
            self.currVariationDisplayed = (self.currVariationDisplayed - 1) % len(self.validColors)
            self.guardSelected = 0
            self.display_variation(self.variations[self.validColors[self.currVariationDisplayed]], self.guardSelected)
        elif self.lock == 1 and self.stepsFinish == 0:
            if self.triI == len(self.triangles) and self.colI > 0 and self.colI < len(self.points):
                self.display_status("Running 3-coloring algorithm")
                self.display_label1("Next step (RIGHT), Previous step (LEFT),")
                self.display_label2("Reset (BACKSPACE)")
                self.colI -= 1
                self.display_prev(self.colI, 1)
            elif self.triI == len(self.triangles) and self.colI == 0:
                self.colI = -1
                self.display_triangulated()
            elif self.triI <= len(self.triangles) and self.triI > 0:
                self.display_status("Running Ear-clipping Triangulation algorithm")
                self.display_label1("Next step (RIGHT), Previous step (LEFT),")
                self.display_label2("Reset (BACKSPACE)")
                self.triI -= 1
                self.display_prev(self.triI, 0)
            elif self.triI == 0:
                self.triI -= 1
                self.canvas.delete("all")
                self.display_status("Displaying Original Polygon")
                self.display_label1("Previous step (LEFT),")
                self.display_label2("Reset (BACKSPACE)")

                self.draw_polygon()

    def on_up(self, event):
        if self.lock == 1 and self.stepsFinish == 1:
            self.guardSelected = (self.guardSelected - 1) % (len(self.variations[self.validColors[self.currVariationDisplayed]]) + 1)
            self.display_variation(self.variations[self.validColors[self.currVariationDisplayed]], self.guardSelected)

    def on_down(self, event):
        if self.lock == 1 and self.stepsFinish == 1:
            self.guardSelected = (self.guardSelected + 1) % (len(self.variations[self.validColors[self.currVariationDisplayed]]) + 1)
            self.display_variation(self.variations[self.validColors[self.currVariationDisplayed]], self.guardSelected)

    def on_backspace(self, event):
        self.canvas.delete("all")
        self.lock = 0
        self.pts = []
        self.points = []
        self.count = 0

        self.variations = [[], [], []]
        self.validColors = []
        self.currVariationDisplayed = 0
        self.guardSelected = 0
        self.processed = 0
        self.stepsFinish = 0
        self.triangles = []
        self.ears = []
        self.triI = -1
        self.coloring3 = []
        self.colI = -1
        self.triPts = []

        self.display_status("Start by building a polygon or loading a polygon from a file")
        self.display_label1("Place first point (Left Click), Load Polygon from file (Space)")
        self.display_label2("")

if __name__ == "__main__":
    root = tk.Tk()
    app = ArtGalleryApp(root)
    root.mainloop()
