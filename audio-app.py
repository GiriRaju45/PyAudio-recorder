import tkinter as tk
from tkinter import ttk
import pandas as pd

class AudioRecorderApp:
    def __init__(self, master):
        self.master = master
        self.master.title('Audio Recorder App')
        self.master.geometry('400x200')
        
        # Load the CSV data
        self.dataframe = pd.read_csv(r'C:\Users\richa\Downloads\TTS_DC\tkinter\demo_correct.csv')
        self.current_index = 0
        
        # UI Components
        self.id_label = ttk.Label(master, text='ID:')
        self.id_label.pack(pady=(20, 0))
        
        self.id_value_label = ttk.Label(master, text="")
        self.id_value_label.pack(pady=(5, 20))
        
        self.sentence_label = ttk.Label(master, text='Sentence:')
        self.sentence_label.pack(pady=(20, 0))
        
        self.sentence_entry = ttk.Entry(master, width=50)
        self.sentence_entry.pack(pady=5)
        
        self.next_button = ttk.Button(master, text='Next', command=self.load_next)
        self.next_button.pack(pady=(20, 0))
        
        # Initial Data Load
        self.load_current_data()
    
    def load_current_data(self):
        """Load data of the current index."""
        if not self.dataframe.empty and self.current_index < len(self.dataframe):
            current_record = self.dataframe.iloc[self.current_index]
            self.id_value_label.config(text=str(current_record['ID']))
            self.sentence_entry.delete(0, tk.END)
            self.sentence_entry.insert(0, current_record['Sentence'])
    
    def load_next(self):
        """Load the next record in the CSV."""
        if self.current_index < len(self.dataframe) - 1:
            self.current_index += 1
            self.load_current_data()
        else:
            print("No more records.")

def main():
    root = tk.Tk()
    app = AudioRecorderApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
