# Reciprocal Lattice Visualizer

A lightweight, browser-based 3D interactive tool for visualizing real crystal lattices, their corresponding reciprocal lattices, and Bragg diffraction points intersecting the Ewald Sphere. 

This project uses modern web technologies to render thousands of lattice points efficiently at 60 FPS, completely contained within a single HTML file.

##  Features
* **Interactive 3D Engine:** Powered by Three.js with orbit controls (pan, zoom, rotate).
* **High Performance:** Uses `InstancedMesh` rendering to draw thousands of points simultaneously without lagging.
* **Modern UI Control Panel:** Sleek, responsive sliders to adjust lattice constants ($a, b, c$), angles ($\alpha, \beta, \gamma$), Ewald sphere radius, and rotation in real-time.
* **Hover Tooltips:** Raycasting integration allows users to hover over any 3D lattice point to see its exact $(x, y, z)$ coordinates and point type.
* **Bragg Diffraction Highlighting:** Automatically calculates which reciprocal points intersect the Ewald sphere and highlights them in red.
* **Zero-Install Setup:** No `npm install` or build steps required. 

##  How to Run
Because the entire application and its dependencies (via CDN) are bundled into a single file, running it is incredibly simple:

1. Clone or download this repository.
2. Double-click the `index.html` file to open it in your preferred modern web browser (Chrome, Firefox, Edge, Safari).
3. Ensure you have an active internet connection the first time you open it so the browser can cache the Three.js library.

##  Mathematical Formulas Used

The visualizer calculates the real and reciprocal lattice vectors based on the standard triclinic unit cell. All angles are converted to radians before calculation.

### 1. Real Space Vectors
Given lattice parameters $a, b, c$ and angles $\alpha, \beta, \gamma$, the real space Cartesian vectors $\mathbf{v}_a, \mathbf{v}_b, \mathbf{v}_c$ are defined as:

$$\mathbf{v}_a = \begin{bmatrix} a \\ 0 \\ 0 \end{bmatrix}$$

$$\mathbf{v}_b = \begin{bmatrix} b \cos\gamma \\ b \sin\gamma \\ 0 \end{bmatrix}$$

$$\mathbf{v}_c = \begin{bmatrix} c \cos\beta \\ c \cdot c_1 \\ c \cdot c_2 \end{bmatrix}$$

Where the volume-related geometric constants are:
$$c_1 = \frac{\cos\alpha - \cos\beta \cos\gamma}{\sin\gamma}$$
$$c_2 = \sqrt{1 - \cos^2\beta - c_1^2}$$

*(Note: In the code, `c2` is protected by `Math.max(0, ...)` to prevent `NaN` crashes when users input extreme unphysical angles).*

### 2. Reciprocal Space Vectors (Physics Convention)
This visualizer uses the crystallographic physics convention which includes the $2\pi$ factor. 

First, the volume of the real unit cell $V$ is calculated using the scalar triple product:
$$V = \mathbf{v}_a \cdot (\mathbf{v}_b \times \mathbf{v}_c)$$

Then, the reciprocal lattice vectors $\mathbf{v}_a^*, \mathbf{v}_b^*, \mathbf{v}_c^*$ are generated:
$$\mathbf{v}_a^* = \frac{2\pi}{V} (\mathbf{v}_b \times \mathbf{v}_c)$$
$$\mathbf{v}_b^* = \frac{2\pi}{V} (\mathbf{v}_c \times \mathbf{v}_a)$$
$$\mathbf{v}_c^* = \frac{2\pi}{V} (\mathbf{v}_a \times \mathbf{v}_b)$$

### 3. Ewald Sphere & Diffraction
A point is considered "Diffracting" (a Bragg peak) if its distance $d$ to the center of the Ewald sphere falls within a narrow tolerance:
$$| d - R_{ewald} | < \text{tolerance}$$

## 🛠️ Built With
* **HTML5 / CSS3 / ES6 JavaScript** - Core web technologies.
* **[Three.js](https://threejs.org/)** - 3D rendering engine.
* **ES Module Import Maps** - For dependency management without Node.js.

##  Contribution Guidelines
Contributions are welcome! If you'd like to improve the visualizer, add features, or fix bugs, please follow these steps:

1. **Fork the Repository:** Click the "Fork" button at the top right of this page.
2. **Clone your Fork:** `git clone https://github.com/your-username/reciprocal-visualizer.git`
3. **Create a Branch:** `git checkout -b feature/AmazingFeature` or `bugfix/FixMathError`
4. **Make your Changes:** Edit the `index.html` file. Keep performance in mind (favor `InstancedMesh` over separate objects).
5. **Commit your Changes:** `git commit -m 'Add some AmazingFeature'`
6. **Push to the Branch:** `git push origin feature/AmazingFeature`
7. **Open a Pull Request:** Navigate to the original repository and click "Compare & pull request".

### Code Style
* Keep the code contained within the single `index.html` file to maintain the "zero-install" philosophy.
* Comment complex math or Three.js matrix manipulations.
* Do not introduce heavy dependencies unless strictly necessary.
