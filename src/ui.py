import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import cvzone
from threading import Thread
from src.config import WIDTH, HEIGHT, CAMERA_SOURCES
from src.image_processing import ParkingMonitor

class ParkingUI:
    def __init__(self, database):
        self.database = database
        self.pos_list = self.database.load_positions()
        self.img = None
        self.root = tk.Tk()
        self.root.title("Smart Parking Dashboard")
        self.root.geometry("400x500")
        self.root.configure(bg='#ecf0f1')
        self.selected_camera = tk.StringVar(value=CAMERA_SOURCES[0])
        self.monitor = ParkingMonitor(self.pos_list, self.database)

    def select_image(self):
        """Select an image for parking spot picking."""
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.img = cv2.imread(file_path)
            if self.img is None:
                messagebox.showerror("Error", "Failed to load image!")
            else:
                messagebox.showinfo("Success", "Image loaded successfully!")

    def mouse_click(self, events, x, y, flags, params):
        """Handle mouse clicks for adding/removing parking spots."""
        if events == cv2.EVENT_LBUTTONDOWN:
            self.pos_list.append((x, y))
        elif events == cv2.EVENT_RBUTTONDOWN:
            self.pos_list = [pos for pos in self.pos_list if not (pos[0] < x < pos[0] + WIDTH and pos[1] < y < pos[1] + HEIGHT)]

    def show_parking_picker(self):
        """Show the parking spot picker window."""
        if self.img is None:
            messagebox.showwarning("Warning", "Please select an image first!")
            return

        cv2.namedWindow("Parking Picker")
        cv2.setMouseCallback("Parking Picker", self.mouse_click)
        while True:
            temp_img = self.img.copy()
            for i, pos in enumerate(self.pos_list):
                cv2.rectangle(temp_img, pos, (pos[0] + WIDTH, pos[1] + HEIGHT), (255, 0, 255), 2)
                cvzone.putTextRect(temp_img, str(i + 1), (pos[0] + 5, pos[1] + 20), scale=1, thickness=1)
            cv2.imshow("Parking Picker", temp_img)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                self.database.save_positions(self.pos_list)
                break
            elif key == ord('q'):
                break
        cv2.destroyAllWindows()

    def start_picker(self):
        """Start the parking picker in a separate thread."""
        thread = Thread(target=self.show_parking_picker)
        thread.daemon = True
        thread.start()

    def save_parking(self):
        """Save parking spots to the database."""
        if not self.pos_list:
            messagebox.showwarning("Warning", "No parking spots to save!")
            return
        self.database.save_positions(self.pos_list)
        messagebox.showinfo("Success", "Parking spots saved successfully!")

    def clear_all_spots(self):
        """Clear all parking spots."""
        self.pos_list = []
        messagebox.showinfo("Success", "All parking spots cleared!")

    def delete_specific_spot(self):
        """Delete a specific parking spot by index."""
        delete_window = tk.Toplevel(self.root)
        delete_window.title("Delete Specific Spot")
        delete_window.geometry("300x150")

        ttk.Label(delete_window, text="Enter spot number to delete:").pack(pady=10)
        spot_entry = ttk.Entry(delete_window)
        spot_entry.pack(pady=5)

        def confirm_delete():
            try:
                spot_index = int(spot_entry.get()) - 1
                if 0 <= spot_index < len(self.pos_list):
                    self.pos_list.pop(spot_index)
                    messagebox.showinfo("Success", f"Spot {spot_index + 1} deleted!")
                    delete_window.destroy()
                else:
                    messagebox.showerror("Error", "Invalid spot number!")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number!")

        ttk.Button(delete_window, text="Delete", command=confirm_delete).pack(pady=10)

    def start_monitoring(self):
        """Start monitoring for all cameras."""
        threads = []
        for i, source in enumerate(CAMERA_SOURCES):
            thread = Thread(target=self.monitor.monitor_parking, args=(source, i + 1))
            thread.daemon = True
            thread.start()
            threads.append(thread)

    def analyze_parking_data(self):
        """Analyze parking data and display results."""
        data = self.database.get_monitoring_data()
        if not data:
            messagebox.showinfo("Info", "No monitoring data available!")
            return

        total_entries = len(data)
        total_free = sum(entry["free_spaces"] for entry in data)
        total_spaces = data[0]["total_spaces"]
        avg_occupancy_rate = ((total_spaces * total_entries - total_free) / (total_spaces * total_entries)) * 100

        busiest_entry = max(data, key=lambda x: total_spaces - x["free_spaces"])
        busiest_time = busiest_entry["timestamp"]
        busiest_occupancy = total_spaces - busiest_entry["free_spaces"]

        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Parking Analysis")
        analysis_window.geometry("400x300")

        ttk.Label(analysis_window, text="Parking Slot Analysis", font=('Arial', 14, 'bold')).pack(pady=10)
        ttk.Label(analysis_window, text=f"Average Occupancy Rate: {avg_occupancy_rate:.2f}%").pack(pady=5)
        ttk.Label(analysis_window, text=f"Busiest Time: {busiest_time}").pack(pady=5)
        ttk.Label(analysis_window, text=f"Occupancy at Busiest Time: {busiest_occupancy}/{total_spaces}").pack(pady=5)

    def create_ui(self):
        """Create the Tkinter UI."""
        style = ttk.Style()
        style.configure("TButton", font=('Arial', 10))
        style.configure("TLabel", font=('Arial', 12), background='#ecf0f1')

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill='both')

        ttk.Label(frame, text="Smart Parking Dashboard", font=('Arial', 18, 'bold')).pack(pady=10)

        ttk.Label(frame, text="Select Camera/Video:").pack(pady=5)
        camera_dropdown = ttk.Combobox(frame, textvariable=self.selected_camera, values=CAMERA_SOURCES, state="readonly", width=27)
        camera_dropdown.pack(pady=5)

        buttons = [
            ("Select Image", self.select_image),
            ("Set Parking Spots", self.start_picker),
            ("Save Parking Spots", self.save_parking),
            ("Delete Specific Spot", self.delete_specific_spot),
            ("Clear All Spots", self.clear_all_spots),
            ("Start Monitoring", self.start_monitoring),
            ("Analyze Parking Data", self.analyze_parking_data),
            ("Exit", self.root.quit)
        ]

        for text, cmd in buttons:
            ttk.Button(frame, text=text, command=cmd, width=30).pack(pady=10)

        status_label = ttk.Label(frame, text="Status: Ready")
        status_label.pack(pady=10)

    def run(self):
        """Run the application."""
        self.create_ui()
        self.root.mainloop()