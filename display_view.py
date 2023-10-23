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

    # Create the label to display the text
    label = tk.Label(window, text=text, font=("Arial", 14), justify="left")
    label.pack(padx=10, pady=10)

    # Create the button to close the window
    close_button = tk.Button(window, text="Close", font=("Arial", 14), bg="red", fg="white", command=window.destroy)
    close_button.pack(pady=10)

    print_button = tk.Button(window, text="Print", font=("Arial", 14), bg="green", fg="white", command=print_and_close)
    print_button.pack(pady=10)
    # Run the Tkinter event loop
    window.mainloop()

    return result if 'result' in globals() else False


if __name__ == "__main__":
    text = 'This is a test of the text display function.'
    print(display_text(text))