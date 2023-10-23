import tkinter as tk

def choose_elements(elements,title="Choose",display_text='CHOOSE', allow_multiple=True):
    selects = []
    # print('choose_elements', elements)
    def end_command():
        # print('end_command')
        for i in listbox.curselection():
            selects.append(elements[i])
        # x = [elements[i] for i in listbox.curselection()]
        window.destroy()
        # print('destroyed')
        return 
    # Create the Tkinter window
    
    window = tk.Tk()
    window.title(title)
    result = []
    # Set the window size and position
    window.geometry("400x400+500+200")

    # Create the label to display the instructions
    label = tk.Label(window, text=display_text, font=("Arial", 16))
    label.pack(pady=10)

    # Create the variable to store the selected elements
    selected_elements = tk.StringVar(value=list(elements))
    # Create the listbox to choose elements
    selectmode = tk.MULTIPLE if allow_multiple else tk.SINGLE
    listbox = tk.Listbox(window, listvariable=selected_elements, selectmode=selectmode, font=("Arial", 14), bg="white", fg="black", height=5)
    listbox.pack(pady=10)

    def update_listbox(*args):
        listbox.delete(0, tk.END)
        for element in elements:
            listbox.insert(tk.END, element)
        print('update_listbox', elements)
    # Register the callback function with the StringVar object
    selected_elements.trace("w", update_listbox)

    # Create the button to submit the selection
    submit_button = tk.Button(window, text="Submit", font=("Arial", 14), bg="blue", fg="white", command=lambda :end_command())
    submit_button.pack(pady=10)

    # Run the Tkinter event loop
    window.mainloop()
    
    #close tkinter window
    # Return the selected elements
    # print('exit')
    return selects

if __name__ == "__main__":
    elements = ["Option 1", "Option 2", "Option 3"]

    selected_elements = choose_elements(elements, allow_multiple=True)
    print(selected_elements)