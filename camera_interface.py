import cv2
import os
from tkinter import Tk, Button, Label, Entry, filedialog, StringVar, IntVar, messagebox
from PIL import Image, ImageTk
import threading


class CameraInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Camera Controller")

        # Initialize camera settings
        self.camera_indexes = [0, 1, 2]  # Indexes for three cameras
        self.cameras = [cv2.VideoCapture(i) for i in self.camera_indexes]
        self.output_dir = ""
        self.counters = [1] * len(self.cameras)  # Image counters for each camera
        self.valid_face_types = ['sad', 'smile', 'neutral']

        self.stream_labels = []
        self.folder_entries = []
        self.counter_labels = []
        self.counter_vars = []

        # Create UI components for each camera
        for i in range(len(self.cameras)):
            self.create_camera_ui(i)

        # Button to choose directory
        Button(root, text="Choose Save Directory", command=self.choose_directory).pack()

        # Capture images from all cameras
        Button(root, text="Capture Images", command=self.capture_images).pack()

        # Start the live stream for all cameras
        self.update_streams()

    def create_camera_ui(self, index):
        # Label to display the camera stream
        stream_label = Label(self.root)
        stream_label.pack()
        self.stream_labels.append(stream_label)

        # Text entry box for folder name
        Label(self.root, text=f"Camera {index + 1} - Enter folder name (valid: sad, smile, neutral):").pack()
        folder_name_var = StringVar()
        folder_entry = Entry(self.root, textvariable=folder_name_var)
        folder_entry.pack()
        folder_entry.bind("<KeyRelease>",
                          lambda e, i=index: self.reset_counter(i))  # Reset counter when folder name changes
        self.folder_entries.append(folder_name_var)

        # Label to display the counter
        counter_label = Label(self.root, text=f"Image Counter: {self.counters[index]}")
        counter_label.pack()
        self.counter_labels.append(counter_label)

        # Manual counter input
        counter_var = IntVar(value=self.counters[index])  # Variable to store manual counter input
        counter_entry = Entry(self.root, textvariable=counter_var)
        counter_entry.pack()
        self.counter_vars.append(counter_var)

        # Button to manually set counter
        Button(self.root, text="Update Counter", command=lambda i=index: self.update_counter_manually(i)).pack()

    def choose_directory(self):
        self.output_dir = filedialog.askdirectory()
        print(f"Save directory set to: {self.output_dir}")

    def capture_images(self):
        if self.output_dir == "":
            print("Please choose a directory first.")
            return

        # Capture image from each camera
        for index, camera in enumerate(self.cameras):
            folder_name = self.folder_entries[index].get()

            # Check if the folder name is valid
            if folder_name not in self.valid_face_types:
                messagebox.showerror("Invalid Folder Name",
                                     f"Camera {index + 1}: Invalid expression - please enter a valid face type (sad, smile, neutral).")
                return

            # Create the complete directory if it doesn't exist
            save_path = os.path.join(self.output_dir, folder_name)
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # Capture image and save it with the format: camera_index_counter.jpg
            ret, frame = camera.read()
            if ret:
                file_path = os.path.join(save_path, f"camera_{index}_{self.counters[index]}.jpg")
                cv2.imwrite(file_path, frame)
                print(f"Camera {index + 1}: Saved image: {file_path}")
                self.counters[index] += 1
                self.counter_labels[index].config(
                    text=f"Image Counter: {self.counters[index]}")  # Update the counter display
            else:
                print(f"Camera {index + 1}: Failed to capture image.")

    def update_streams(self):
        for index, camera in enumerate(self.cameras):
            ret, frame = camera.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)

                self.stream_labels[index].imgtk = imgtk
                self.stream_labels[index].configure(image=imgtk)

        self.root.after(20, self.update_streams)

    def reset_counter(self, index):
        # Reset the image counter to 1 when the folder name changes
        self.counters[index] = 1
        self.counter_vars[index].set(self.counters[index])  # Reset the manual input as well
        self.counter_labels[index].config(text=f"Image Counter: {self.counters[index]}")
        print(f"Camera {index + 1}: Folder name changed. Counter reset to {self.counters[index]}")

    def update_counter_manually(self, index):
        # Manually update the counter from the entry box value
        try:
            new_counter_value = self.counter_vars[index].get()
            if new_counter_value >= 1:  # Ensure the counter is a valid number
                self.counters[index] = new_counter_value
                self.counter_labels[index].config(text=f"Image Counter: {self.counters[index]}")
                print(f"Camera {index + 1}: Counter manually set to: {self.counters[index]}")
            else:
                messagebox.showerror("Invalid Counter", "Counter value must be greater than or equal to 1.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the counter.")

    def close(self):
        for camera in self.cameras:
            if camera.isOpened():
                camera.release()
                print("Camera released.")

        cv2.destroyAllWindows()
        self.root.quit()
        self.root.destroy()
        print("Application closed.")


if __name__ == "__main__":
    root = Tk()
    app = CameraInterface(root)

    # Bind window close event
    root.protocol("WM_DELETE_WINDOW", app.close)

    root.mainloop()
