import cv2
import os
from tkinter import Tk, Button, Label, Entry, filedialog, StringVar, IntVar, messagebox
from PIL import Image, ImageTk


class CameraInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Camera Controller with Save Path")

        # Initialize camera
        self.camera = cv2.VideoCapture(0)
        self.output_dir = ""
        self.save_folder = ""  # Folder name typed by the user
        self.counter = 1  # Image counter

        # List of valid face types
        self.valid_face_types = ['sad', 'smile', 'neutral']

        # Label to display the camera stream
        self.stream_label = Label(root)
        self.stream_label.pack()

        # Text entry box for folder name
        Label(root, text="Enter folder name (valid: sad, smile, neutral):").pack()
        self.folder_name_var = StringVar()
        self.folder_entry = Entry(root, textvariable=self.folder_name_var)
        self.folder_entry.pack()
        self.folder_entry.bind("<KeyRelease>", self.reset_counter)  # Reset counter when folder name changes

        # Label to display the counter
        self.counter_label = Label(root, text=f"Image Counter: {self.counter}")
        self.counter_label.pack()

        # Manual counter input
        Label(root, text="Set Counter Manually:").pack()
        self.counter_var = IntVar(value=self.counter)  # Variable to store manual counter input
        self.counter_entry = Entry(root, textvariable=self.counter_var)
        self.counter_entry.pack()

        # Button to manually set counter
        Button(root, text="Update Counter", command=self.update_counter_manually).pack()

        # Button to choose directory
        Button(root, text="Choose Save Directory", command=self.choose_directory).pack()

        # Capture image button
        Button(root, text="Capture Image", command=self.capture_image).pack()

        # Start the live stream
        self.update_stream()

    def choose_directory(self):
        self.output_dir = filedialog.askdirectory()
        print(f"Save directory set to: {self.output_dir}")

    def capture_image(self):
        if self.output_dir == "":
            print("Please choose a directory first.")
            return

        # Get the folder name from the text box
        folder_name = self.folder_name_var.get()

        # Check if the folder name is valid
        if folder_name not in self.valid_face_types:
            messagebox.showerror("Invalid Folder Name",
                                 "Invalid expression - please enter a valid face type (sad, smile, neutral).")
            return

        # Create the complete directory if it doesn't exist
        save_path = os.path.join(self.output_dir, folder_name)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # Capture image and save it with an incrementing counter
        ret, frame = self.camera.read()
        if ret:
            file_path = os.path.join(save_path, f"{self.counter}.jpg")
            cv2.imwrite(file_path, frame)
            print(f"Saved image: {file_path}")
            self.counter += 1
            self.update_counter_label()  # Update the counter display
        else:
            print("Failed to capture image.")

    def update_counter_label(self):
        # Update the label to reflect the current counter value
        self.counter_label.config(text=f"Image Counter: {self.counter}")

    def update_counter_manually(self):
        # Manually update the counter from the entry box value
        try:
            new_counter_value = self.counter_var.get()
            if new_counter_value >= 1:  # Ensure the counter is a valid number
                self.counter = new_counter_value
                self.update_counter_label()
                print(f"Counter manually set to: {self.counter}")
            else:
                messagebox.showerror("Invalid Counter", "Counter value must be greater than or equal to 1.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the counter.")

    def update_stream(self):

        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.stream_label.imgtk = imgtk
            self.stream_label.configure(image=imgtk)

        self.root.after(20, self.update_stream)

    def reset_counter(self, event=None):
        # Reset the image counter to 1 when the folder name changes
        self.counter = 1
        self.counter_var.set(self.counter)  # Reset the manual input as well
        print(f"Folder name changed. Counter reset to {self.counter}")
        self.update_counter_label()  # Update the counter display after reset

    def close(self):
        if self.camera.isOpened():
            self.camera.release()
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
