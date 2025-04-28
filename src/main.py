import tkinter as tk
from tkinter import messagebox, ttk
import random


class PageReplacementSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Page Replacement Simulator")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        # Global variables
        self.generated_pages = []
        self.current_index = 0
        self.frames = []
        self.page_faults = 0
        self.animation_speed = 1.0
        self.animation_id = None
        self.is_animating = False

        # Setup UI components
        self.setup_ui()

        # Set defaults
        self.frames_entry.insert(0, "3")
        self.pages_entry.insert(0, "10")

    def setup_ui(self):
        # Create main frames
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Top control panel
        self.control_frame = ttk.LabelFrame(
            self.main_frame, text="Controls", padding=10)
        self.control_frame.pack(fill=tk.X, pady=(0, 10))

        # Settings frame (left)
        settings_frame = ttk.Frame(self.control_frame)
        settings_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Frames input
        ttk.Label(settings_frame, text="Number of Frames:").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.frames_entry = ttk.Entry(settings_frame, width=10)
        self.frames_entry.grid(row=0, column=1, padx=5, pady=5)

        # Pages input
        ttk.Label(settings_frame, text="Number of Pages:").grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.pages_entry = ttk.Entry(settings_frame, width=10)
        self.pages_entry.grid(row=1, column=1, padx=5, pady=5)

        # Generate button
        generate_btn = ttk.Button(
            settings_frame, text="Generate Pages", command=self.generate_pages)
        generate_btn.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=10)

        # Animation controls (middle)
        anim_frame = ttk.Frame(self.control_frame, padding=(20, 0, 0, 0))
        anim_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20)

        ttk.Label(anim_frame, text="Animation Speed:").pack(anchor=tk.W)
        self.speed_scale = ttk.Scale(anim_frame, from_=0.5, to=3.0, orient=tk.HORIZONTAL,
                                     length=150, command=self.update_speed)
        self.speed_scale.set(1.0)
        self.speed_scale.pack(fill=tk.X)

        self.speed_label = ttk.Label(anim_frame, text="1.0x")
        self.speed_label.pack()

        # Algorithm buttons (right)
        algo_frame = ttk.Frame(self.control_frame, padding=(20, 0, 0, 0))
        algo_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20)

        ttk.Label(algo_frame, text="Select Algorithm:").pack(anchor=tk.W)
        algo_buttons_frame = ttk.Frame(algo_frame)
        algo_buttons_frame.pack(fill=tk.X, pady=5)

        self.fifo_btn = ttk.Button(
            algo_buttons_frame, text="FIFO", command=self.run_fifo)
        self.fifo_btn.pack(side=tk.LEFT, padx=5)

        self.lru_btn = ttk.Button(
            algo_buttons_frame, text="LRU", command=self.run_lru)
        self.lru_btn.pack(side=tk.LEFT, padx=5)

        self.opt_btn = ttk.Button(
            algo_buttons_frame, text="OPT", command=self.run_opt)
        self.opt_btn.pack(side=tk.LEFT, padx=5)

        # Control buttons
        ctrl_buttons_frame = ttk.Frame(algo_frame)
        ctrl_buttons_frame.pack(fill=tk.X, pady=5)

        self.start_btn = ttk.Button(
            ctrl_buttons_frame, text="Start", command=self.start_animation, state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            ctrl_buttons_frame, text="Stop", command=self.stop_animation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = ttk.Button(
            ctrl_buttons_frame, text="Reset", command=self.reset_simulation)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        # Page sequence display
        self.sequence_frame = ttk.LabelFrame(
            self.main_frame, text="Page Reference Sequence", padding=10)
        self.sequence_frame.pack(fill=tk.X, pady=(0, 10))

        self.sequence_canvas = tk.Canvas(self.sequence_frame, height=50, bg="white", highlightthickness=1,
                                         highlightbackground="gray")
        self.sequence_canvas.pack(fill=tk.X, pady=5)

        # Main content area (split into two)
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Memory frames visualization (left)
        self.frames_frame = ttk.LabelFrame(
            content_frame, text="Memory Frames", padding=10)
        self.frames_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.frames_canvas = tk.Canvas(self.frames_frame, bg="white", highlightthickness=1,
                                       highlightbackground="gray")
        self.frames_canvas.pack(fill=tk.BOTH, expand=True, pady=5)

        # Simulation log (right)
        self.log_frame = ttk.LabelFrame(
            content_frame, text="Simulation Log", padding=10)
        self.log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Add scrollbar to log
        log_scroll = ttk.Scrollbar(self.log_frame)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(self.log_frame, height=10,
                                width=30, yscrollcommand=log_scroll.set)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        log_scroll.config(command=self.log_text.yview)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_speed(self, value):
        """Update animation speed"""
        self.animation_speed = float(value)
        self.speed_label.config(text=f"{self.animation_speed:.1f}x")

    def generate_pages(self):
        """Generate random page reference sequence"""
        try:
            num_pages = int(self.pages_entry.get())
            if num_pages <= 0 or num_pages > 50:
                messagebox.showerror(
                    "Invalid Input", "Number of pages must be between 1 and 50.")
                return

            # Generate pages between 0 and 9
            self.generated_pages = [random.randint(
                0, 9) for _ in range(num_pages)]
            self.draw_page_sequence()
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(
                tk.END, f"Generated Pages: {' '.join(map(str, self.generated_pages))}\n\n")
            self.status_var.set(
                f"Generated {num_pages} pages. Select an algorithm to run.")

            # Enable buttons
            self.fifo_btn.config(state=tk.NORMAL)
            self.lru_btn.config(state=tk.NORMAL)
            self.opt_btn.config(state=tk.NORMAL)

        except ValueError:
            messagebox.showerror(
                "Invalid Input", "Please enter a valid number for pages.")

    def draw_page_sequence(self):
        """Draw the page sequence on canvas"""
        self.sequence_canvas.delete("all")

        box_size = 40
        padding = 5
        x_start = 10

        # Draw each page box
        for i, page in enumerate(self.generated_pages):
            x = x_start + i * (box_size + padding)

            # Check if we need to show ellipsis for long sequences
            if x > self.sequence_canvas.winfo_width() - 2*box_size and i < len(self.generated_pages) - 1:
                self.sequence_canvas.create_text(
                    x + 10, box_size/2, text="...", font=("Arial", 12, "bold"))

                # Draw the last page after ellipsis
                last_x = x + 30
                self.sequence_canvas.create_rectangle(last_x, 5, last_x + box_size, 5 + box_size,
                                                      fill="#e0e0e0", outline="black", tags=f"page{len(self.generated_pages)-1}")
                self.sequence_canvas.create_text(last_x + box_size/2, 5 + box_size/2,
                                                 text=str(self.generated_pages[-1]), tags=f"page{len(self.generated_pages)-1}")
                break

            # Draw page box
            self.sequence_canvas.create_rectangle(x, 5, x + box_size, 5 + box_size,
                                                  fill="#e0e0e0", outline="black", tags=f"page{i}")
            self.sequence_canvas.create_text(
                x + box_size/2, 5 + box_size/2, text=str(page), tags=f"page{i}")

    def highlight_current_page(self, index):
        """Highlight current page in sequence"""
        # Remove previous highlights
        self.sequence_canvas.delete("highlight")

        if index >= len(self.generated_pages):
            return

        box_size = 40
        padding = 5
        x_start = 10
        x = x_start + index * (box_size + padding)

        # If we're showing ellipsis and this is the last page
        if x > self.sequence_canvas.winfo_width() - 2*box_size and index < len(self.generated_pages) - 1:
            # Don't highlight
            return
        elif index == len(self.generated_pages) - 1 and x > self.sequence_canvas.winfo_width() - 2*box_size:
            # Highlight the last page shown after ellipsis
            x = x_start + (self.sequence_canvas.winfo_width() - 2 *
                           box_size) // (box_size + padding) * (box_size + padding) + 30

        # Create highlight rectangle
        self.sequence_canvas.create_rectangle(x-2, 3, x+box_size+2, 7+box_size,
                                              outline="red", width=2, tags="highlight")

    def draw_frames(self, highlight_index=-1):
        """Draw memory frames"""
        self.frames_canvas.delete("all")

        if not self.frames:
            return

        # Get available space
        width = self.frames_canvas.winfo_width()
        height = self.frames_canvas.winfo_height()

        frame_width = min(100, width - 20)
        frame_height = min(60, (height - 20) // len(self.frames))
        start_y = 20

        # Draw each frame
        for i, page in enumerate(self.frames):
            y = start_y + i * (frame_height + 10)

            # Determine if this frame should be highlighted
            fill_color = "#ff9999" if i == highlight_index else "#e0e0ff"

            # Draw frame box
            self.frames_canvas.create_rectangle(10, y, 10 + frame_width, y + frame_height,
                                                fill=fill_color, outline="black")
            self.frames_canvas.create_text(10 + frame_width/2, y + frame_height/2,
                                           text=str(page), font=("Arial", 14, "bold"))

            # Label the frame
            self.frames_canvas.create_text(10 + frame_width + 10, y + frame_height/2,
                                           text=f"Frame {i}", anchor=tk.W)

    def prepare_algorithm(self, name):
        """Common setup for all algorithms"""
        try:
            frame_size = int(self.frames_entry.get())
            if frame_size <= 0 or frame_size > 10:
                messagebox.showerror(
                    "Invalid Input", "Number of frames must be between 1 and 10.")
                return False

            if not self.generated_pages:
                messagebox.showerror(
                    "No Pages", "Please generate page reference sequence first.")
                return False

            # Reset simulation state
            self.current_index = 0
            self.frames = []
            self.page_faults = 0

            # Update UI
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, f"{name} Algorithm Selected\n")
            self.log_text.insert(
                tk.END, f"Page Reference String: {' '.join(map(str, self.generated_pages))}\n\n")
            self.status_var.set(f"Running {name} algorithm")

            # Disable algorithm buttons during simulation
            self.fifo_btn.config(state=tk.DISABLED)
            self.lru_btn.config(state=tk.DISABLED)
            self.opt_btn.config(state=tk.DISABLED)

            # Enable start button
            self.start_btn.config(state=tk.NORMAL)

            # Reset canvas
            self.frames_canvas.delete("all")
            self.sequence_canvas.delete("highlight")

            return True
        except ValueError:
            messagebox.showerror(
                "Invalid Input", "Please enter a valid number for frames.")
            return False

    def run_fifo(self):
        """Setup FIFO algorithm simulation"""
        if not self.prepare_algorithm("FIFO"):
            return

        self.algorithm = "FIFO"
        self.log_text.insert(tk.END, "Click 'Start' to begin animation\n\n")

    def run_lru(self):
        """Setup LRU algorithm simulation"""
        if not self.prepare_algorithm("LRU"):
            return

        self.algorithm = "LRU"
        self.log_text.insert(tk.END, "Click 'Start' to begin animation\n\n")

    def run_opt(self):
        """Setup OPT algorithm simulation"""
        if not self.prepare_algorithm("OPT"):
            return

        self.algorithm = "OPT"
        self.log_text.insert(tk.END, "Click 'Start' to begin animation\n\n")

    def start_animation(self):
        """Start the animation"""
        self.is_animating = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.animate_step()

    def stop_animation(self):
        """Stop the animation"""
        self.is_animating = False
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        self.stop_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.NORMAL)
        self.status_var.set("Animation stopped")

    def reset_simulation(self):
        """Reset the simulation"""
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None

        self.is_animating = False
        self.current_index = 0
        self.frames = []
        self.page_faults = 0

        # Reset UI
        self.frames_canvas.delete("all")
        self.sequence_canvas.delete("highlight")
        self.log_text.delete(1.0, tk.END)

        # Reset buttons
        self.fifo_btn.config(state=tk.NORMAL)
        self.lru_btn.config(state=tk.NORMAL)
        self.opt_btn.config(state=tk.NORMAL)
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)

        self.status_var.set("Simulation reset")

    def animate_step(self):
        """Perform one step of the animation"""
        if not self.is_animating or self.current_index >= len(self.generated_pages):
            if self.current_index >= len(self.generated_pages):
                self.status_var.set(
                    f"Simulation complete. Total page faults: {self.page_faults}")
                self.stop_btn.config(state=tk.DISABLED)
                self.log_text.insert(
                    tk.END, f"\nSimulation complete.\nTotal page faults: {self.page_faults}\n")
            return

        # Get current page
        current_page = self.generated_pages[self.current_index]

        # Highlight current page in sequence
        self.highlight_current_page(self.current_index)

        # Process according to algorithm
        if self.algorithm == "FIFO":
            self.process_fifo_step(current_page)
        elif self.algorithm == "LRU":
            self.process_lru_step(current_page)
        elif self.algorithm == "OPT":
            self.process_opt_step(current_page)

        # Increment index for next step
        self.current_index += 1

        # Schedule next step
        delay = int(1000 / self.animation_speed)
        self.animation_id = self.root.after(delay, self.animate_step)

    def process_fifo_step(self, current_page):
        """Process one step of FIFO algorithm"""
        frame_size = int(self.frames_entry.get())
        page_fault = False
        replaced_index = -1
        replaced_page = None

        if current_page not in self.frames:
            page_fault = True
            if len(self.frames) < frame_size:
                self.frames.append(current_page)
                replaced_index = len(self.frames) - 1
            else:
                replaced_page = self.frames[0]
                self.frames.pop(0)
                self.frames.append(current_page)
                replaced_index = len(self.frames) - 1
            self.page_faults += 1

        # Update log
        if page_fault:
            if replaced_page is not None:
                log_msg = f"Page {current_page}: Not in frames, replacing {replaced_page} (FIFO) -> Page Fault!\n"
            else:
                log_msg = f"Page {current_page}: Not in frames, adding to frame -> Page Fault!\n"
        else:
            log_msg = f"Page {current_page}: Already in frames -> Page Hit\n"

        self.log_text.insert(tk.END, log_msg)
        self.log_text.see(tk.END)

        # Update frames display
        self.draw_frames(replaced_index if page_fault else -1)

        # Update status
        self.status_var.set(f"FIFO: Processing page {current_page}, " +
                            ("Page Fault" if page_fault else "Page Hit"))

    def process_lru_step(self, current_page):
        """Process one step of LRU algorithm"""
        frame_size = int(self.frames_entry.get())
        page_fault = False
        replaced_index = -1
        replaced_page = None

        if current_page not in self.frames:
            page_fault = True
            if len(self.frames) < frame_size:
                self.frames.append(current_page)
                replaced_index = len(self.frames) - 1
            else:
                replaced_page = self.frames[0]
                self.frames.pop(0)
                self.frames.append(current_page)
                replaced_index = len(self.frames) - 1
            self.page_faults += 1
        else:
            # Move to the end (most recently used)
            self.frames.remove(current_page)
            self.frames.append(current_page)

        # Update log
        if page_fault:
            if replaced_page is not None:
                log_msg = f"Page {current_page}: Not in frames, replacing {replaced_page} (LRU) -> Page Fault!\n"
            else:
                log_msg = f"Page {current_page}: Not in frames, adding to frame -> Page Fault!\n"
        else:
            log_msg = f"Page {current_page}: Already in frames, moving to MRU position -> Page Hit\n"

        self.log_text.insert(tk.END, log_msg)
        self.log_text.see(tk.END)

        # Update frames display
        self.draw_frames(replaced_index if page_fault else -1)

        # Update status
        self.status_var.set(f"LRU: Processing page {current_page}, " +
                            ("Page Fault" if page_fault else "Page Hit"))

    def process_opt_step(self, current_page):
        """Process one step of OPT algorithm"""
        frame_size = int(self.frames_entry.get())
        page_fault = False
        replaced_index = -1
        replaced_page = None

        if current_page not in self.frames:
            page_fault = True
            if len(self.frames) < frame_size:
                self.frames.append(current_page)
                replaced_index = len(self.frames) - 1
            else:
                # Find page that won't be used for the longest time
                farthest_use = -1
                for i, frame in enumerate(self.frames):
                    if frame in self.generated_pages[self.current_index+1:]:
                        next_use = self.generated_pages[self.current_index+1:].index(
                            frame)
                        if next_use > farthest_use:
                            farthest_use = next_use
                            replaced_index = i
                    else:
                        # If not used again, this is optimal
                        replaced_index = i
                        break

                replaced_page = self.frames[replaced_index]
                self.frames[replaced_index] = current_page
            self.page_faults += 1

        # Update log
        if page_fault:
            if replaced_page is not None:
                log_msg = f"Page {current_page}: Not in frames, replacing {replaced_page} (OPT) -> Page Fault!\n"
            else:
                log_msg = f"Page {current_page}: Not in frames, adding to frame -> Page Fault!\n"
        else:
            log_msg = f"Page {current_page}: Already in frames -> Page Hit\n"

        self.log_text.insert(tk.END, log_msg)
        self.log_text.see(tk.END)

        # Update frames display
        self.draw_frames(replaced_index if page_fault else -1)

        # Update status
        self.status_var.set(f"OPT: Processing page {current_page}, " +
                            ("Page Fault" if page_fault else "Page Hit"))


# Main application launcher
if __name__ == "__main__":
    root = tk.Tk()
    app = PageReplacementSimulator(root)
    root.mainloop()
