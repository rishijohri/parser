import tkinter as tk

def display_text(text):
    global result
    result = False
    def print_and_close():
        global result
        result = True
        window.destroy()

    # Create the Tkinter window
    window = tk.Tk()
    window.title("Notice")
    window.geometry("500x500") # Set the size of the window

    # Create the canvas and scrollbar
    canvas = tk.Canvas(window)
    scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create the frame to hold the label and buttons
    frame = tk.Frame(canvas)

    # Add the horizontal scrollbar
    h_scrollbar = tk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
    h_scrollbar.pack(side="bottom", fill="x")
    canvas.configure(xscrollcommand=h_scrollbar.set)


    # Add the label to the frame
    label = tk.Label(frame, text=text, font=("Arial", 14), justify="left")
    label.pack(padx=10, pady=10)

    # Add the buttons to the frame
    close_button = tk.Button(frame, text="Close", font=("Arial", 14), bg="red", fg="white", command=window.destroy)
    close_button.pack(pady=10)

    print_button = tk.Button(frame, text="Print", font=("Arial", 14), bg="green", fg="white", command=print_and_close)
    print_button.pack(pady=10)

    # Add the frame to the canvas
    canvas.create_window((0, 0), window=frame, anchor="nw")

    # Configure the canvas to resize with the window
    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.bind("<Configure>", on_configure)

    # Run the Tkinter event loop
    window.mainloop()

    return result if 'result' in globals() else False



if __name__ == "__main__":
    text = 'This is a test of the text display function.'
    print(display_text(text))