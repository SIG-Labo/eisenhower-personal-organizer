import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import messagebox
import webbrowser
import subprocess
import shutil
import os
import json

class AboutDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About")
        
        label = tk.Label(self, text="E-Matrix v 3.2\n(c) 2024 Peter De Ceuster\n peterdeceuster.uk \nFree to distribute\nDistributed under the FPA General Code License", justify="center", fg="blue", cursor="hand2")
        label.pack(padx=10, pady=10)
        label.bind("<Button-1>", self.open_url)

        ok_button = tk.Button(self, text="OK", command=self.destroy)
        ok_button.pack(pady=5)

    def open_url(self, event):
        webbrowser.open("https://peterdeceuster.uk/")
        
class DailyPlannerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Eisenhower-Matrix Personal Planner 3.2 - Welcome")
        self.root.state('zoomed')
        self.root.configure(bg='lightblue')
          
        # Play chimes sound
        # winsound.PlaySound("SystemHand", winsound.SND_ALIAS)

        self.tasks = []
        self.task_goals = {}
        self.morning_routine = [
            "Water",
            "Breakfast",
            "Stretching",
            "Plank",
            "Meditation"
        ]
        self.deleted_tasks = []
        self.eisenhower_matrix_results = None
        self.last_review_results = None
        self.data_file = "eisenhower-data.json"
        self.backup_file = "eisenhower-data-backup.json"  

        self.load_backup_data() 
        self.load_data()
        self.create_menu()
        self.create_widgets()  
        self.center_window()  
        self.display_eisenhower_matrix_results()  

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Exit", command=self.exit_program)
        menu.add_cascade(label="File", menu=file_menu)
        
        planner_menu = tk.Menu(menu, tearoff=False)
        planner_menu.add_command(label="Brain Dump", command=self.brain_dump)
        planner_menu.add_command(label="Separate Tasks", command=self.separate_tasks)
        planner_menu.add_command(label="View or alter Morning Routine", command=self.create_morning_routine)
        planner_menu.add_command(label="Stop Overloading List (trim list)", command=self.confirm_stop_overloading_list)
        planner_menu.add_command(label="Connect Tasks to Goals", command=self.connect_tasks_to_goals)
        planner_menu.add_command(label="Retrieve Task Goals", command=self.retrieve_task_goals)
        planner_menu.add_command(label="Retrieve Deleted Tasks (trimmed items)", command=self.retrieve_deleted_tasks)
        planner_menu.add_command(label="Review Day", command=self.review_day)
        planner_menu.add_command(label="List All Tasks", command=self.list_all_tasks)
        planner_menu.add_command(label="Remove a Task", command=self.remove_task)
        planner_menu.add_command(label="Clear All Tasks", command=self.clear_all_tasks)  
        menu.add_cascade(label="Planner", menu=planner_menu)
        
        about_menu = tk.Menu(menu, tearoff=False)
        about_menu.add_command(label="About", command=self.about)
        menu.add_cascade(label="About", menu=about_menu)

        future_ideas_menu = tk.Menu(menu, tearoff=False)
        future_ideas_menu.add_command(label="Enter Future Ideas", command=self.enter_future_ideas)
        future_ideas_menu.add_command(label="Retrieve Future Ideas", command=self.retrieve_future_ideas)
        menu.add_cascade(label="Future Ideas", menu=future_ideas_menu)

    def create_widgets(self):
        self.scrollbar = tk.Scrollbar(self.root)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.review_text_widget = tk.Text(self.root, height=10, width=80, bg="black", fg="green")
        self.review_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.review_text_widget.config(wrap="word")
        self.review_text_widget.config(yscrollcommand=self.scrollbar.set)
        self.review_text_widget.config(xscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.review_text_widget.yview)

        self.eisenhower_matrix_label = tk.Label(self.root, text="Eisenhower Matrix Results:", bg='lightblue')
        self.eisenhower_matrix_label.pack(pady=10)

        self.eisenhower_matrix_display = tk.Text(self.root, height=10, width=80, bg="black", fg="red")  
        self.eisenhower_matrix_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.eisenhower_matrix_display.config(wrap="word")
        self.eisenhower_matrix_display.config(yscrollcommand=self.scrollbar.set)
        self.eisenhower_matrix_display.config(xscrollcommand=self.scrollbar.set)


    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def exit_program(self):
        self.save_data()  
        subprocess.run(["python", "locksoft.py"], check=True)

        self.root.quit()

    def brain_dump(self):
        def add_task():
            task = entry_task.get().strip()
            if task:
                if task not in self.tasks:  
                    self.tasks.append(task)
                    listbox_tasks.insert(tk.END, task)
                    entry_task.delete(0, tk.END)
                else:
                    messagebox.showwarning("Duplicate Task", f"'{task}' is already in the task list.")

        def done():
            new_tasks_added = False
            for task in self.tasks:
                if task not in original_tasks:
                    new_tasks_added = True
                    break
            
            dialog_window.destroy()
            
            if new_tasks_added:
                response = messagebox.askyesno("New Tasks Added", "New tasks have been added. Do you want to connect these tasks to goals?")
                if response:
                    self.connect_tasks_to_goals(self.tasks)

        dialog_window = tk.Toplevel(self.root)
        dialog_window.title("Brain Dump")
        dialog_window.attributes('-topmost', True)
        
        frame = tk.Frame(dialog_window)
        frame.pack(padx=10, pady=10)
        
        entry_task = tk.Entry(frame, width=40)
        entry_task.pack(side=tk.LEFT, padx=5)
        entry_task.focus_set()
        
        button_add = tk.Button(frame, text="Add Task", width=10, command=add_task)
        button_add.pack(side=tk.LEFT, padx=5)
        
        button_done = tk.Button(frame, text="Done", width=10, command=done)
        button_done.pack(side=tk.LEFT, padx=5)
        
        listbox_tasks = tk.Listbox(dialog_window, width=50)
        listbox_tasks.pack(pady=5)
        
        original_tasks = self.tasks.copy()
        for task in self.tasks:
            listbox_tasks.insert(tk.END, task)

    def separate_tasks(self):
        self.eisenhower_matrix_results = {}
        urgent_important = []
        not_urgent_important = []
        urgent_not_important = []
        not_urgent_not_important = []

        for task in self.tasks:
            urgency = self.yes_no_prompt("Eisenhower Matrix", f"Is '{task}' Urgent?")
            importance = self.yes_no_prompt("Eisenhower Matrix", f"Is '{task}' Important?")

            if urgency == 'Yes' and importance == 'Yes':
                urgent_important.append(task)
            elif urgency == 'No' and importance == 'Yes':
                not_urgent_important.append(task)
            elif urgency == 'Yes' and importance == 'No':
                urgent_not_important.append(task)
            else:
                not_urgent_not_important.append(task)

        self.eisenhower_matrix_results["Urgent and Important"] = urgent_important
        self.eisenhower_matrix_results["Not Urgent, but Important"] = not_urgent_important
        self.eisenhower_matrix_results["Urgent, but Not Important"] = urgent_not_important
        self.eisenhower_matrix_results["Not Urgent and Not Important"] = not_urgent_not_important
        self.display_eisenhower_matrix_results()  
        self.save_data()

    def create_morning_routine(self):
        response = self.yes_no_prompt("Morning Routine", f"Current Morning Routine:\n{', '.join(self.morning_routine)}\n\nWould you like to adjust your morning routine?")
        if response.lower() == 'yes':
            new_routine = simpledialog.askstring("Morning Routine", "Enter your adjusted morning routine (separate tasks with comma):")
            if new_routine is not None:
                self.morning_routine = [task.strip() for task in new_routine.split(',')]
        self.save_data()

    def stop_overloading_list(self):
        if len(self.tasks) > 5:
            self.deleted_tasks = self.tasks[5:]
            self.tasks = self.tasks[:5]
        self.save_data()

    def confirm_stop_overloading_list(self):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to trim the task list?")
        if confirm:
            self.stop_overloading_list()
            messagebox.showinfo("Success", "Task list trimmed successfully.")
        else:
            messagebox.showinfo("Cancelled", "Operation cancelled.")

    def connect_tasks_to_goals(self, tasks_to_connect=None):
        if tasks_to_connect is None:
            tasks_to_connect = self.tasks

        for task in tasks_to_connect:
            goal = simpledialog.askstring("Connect Tasks to Goals", f"What is the goal behind '{task}'?:", parent=self.root)
            self.task_goals[task] = goal
        self.save_data()

    def retrieve_task_goals(self):
        current_tasks = set(self.tasks)
        goals_to_display = {task: goal for task, goal in self.task_goals.items() if task in current_tasks}
        if goals_to_display:
            goals = "\n".join([f"- {task}: {goal}" for task, goal in goals_to_display.items()])
            messagebox.showinfo("Task Goals", "Tasks and their associated goals:\n" + goals)
        else:
            messagebox.showinfo("Task Goals", "No task goals have been set yet.")

    def retrieve_deleted_tasks(self):
        if self.deleted_tasks:
            tasks = "\n".join(self.deleted_tasks)
            messagebox.showinfo("Deleted Tasks", "Deleted tasks:\n" + tasks)
        else:
            messagebox.showinfo("Deleted Tasks", "No tasks have been deleted yet.")

    def review_day(self):
        if self.last_review_results:
            last_review = self.last_review_results
            completed_tasks = last_review.get("completed_tasks", [])
            incompleted_tasks = last_review.get("incompleted_tasks", [])
            completed = "\n".join([f"- {task}" for task in completed_tasks])
            incompleted = "\n".join([f"- {task}" for task in incompleted_tasks])
            messagebox.showinfo("Last Review Results", f"Completed Tasks (from last review):\n{completed}\n\nUncompleted Tasks (from last review):\n{incompleted}")
        else:
            messagebox.showinfo("Last Review Results", "No previous review results available.")

        if self.eisenhower_matrix_results:
            categories = ""
            for category, tasks in self.eisenhower_matrix_results.items():
                tasks_str = "\n".join([f"- {task}" for task in tasks])
                categories += f"{category}:\n{tasks_str}\n\n"
            messagebox.showinfo("Eisenhower Matrix Results", categories)
        else:
            messagebox.showinfo("Eisenhower Matrix Results", "No tasks have been categorized yet.")
        
        completed_tasks = []
        for task in self.tasks:
            response = self.yes_no_prompt("Review Day", f"Did you complete '{task}'?")
            if response.lower() == 'yes':
                completed_tasks.append(task)
        incompleted_tasks = [task for task in self.tasks if task not in completed_tasks]
        self.last_review_results = {"completed_tasks": completed_tasks, "incompleted_tasks": incompleted_tasks}
        self.display_eisenhower_matrix_results()  
        self.save_data()

        review_text = f"Completed Tasks (from last review):\n{', '.join(completed_tasks)}\n\nUncompleted Tasks (from last review):\n{', '.join(incompleted_tasks)}"
        self.review_text_widget.delete(1.0, tk.END)
        self.review_text_widget.insert(tk.END, review_text)

    def list_all_tasks(self):
        tasks = "\n".join([f"- {task}" for task in self.tasks])
        messagebox.showinfo("All Current Tasks", "All Current Tasks:\n" + tasks)

    def remove_task(self):
        def remove_selected_task():
            selected_task = listbox_tasks.curselection()
            if selected_task:
                task_index = selected_task[0]
                task_to_remove = listbox_tasks.get(task_index)
                self.tasks.remove(task_to_remove)
                listbox_tasks.delete(task_index)
                messagebox.showinfo("Remove a Task", f"'{task_to_remove}' has been removed.")
                dialog_window.destroy()
            else:
                messagebox.showwarning("Remove a Task", "Please select a task to remove.")

        dialog_window = tk.Toplevel(self.root)
        dialog_window.title("Remove a Task")
        dialog_window.attributes('-topmost', True)

        frame = tk.Frame(dialog_window)
        frame.pack(padx=10, pady=10)

        label_prompt = tk.Label(frame, text="Select the task to remove:")
        label_prompt.pack()

        listbox_tasks = tk.Listbox(dialog_window, width=50)
        listbox_tasks.pack(pady=5)

        for task in self.tasks:
            listbox_tasks.insert(tk.END, task)

        button_remove = tk.Button(frame, text="Remove Task", width=15, command=remove_selected_task)
        button_remove.pack(pady=5)

    def clear_all_tasks(self):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to clear all tasks?")
        if confirm:
            self.tasks = []  
            self.eisenhower_matrix_results = None  
            self.save_data()
            self.display_eisenhower_matrix_results()  
            messagebox.showinfo("Success", "All tasks cleared successfully.")
        else:
            messagebox.showinfo("Cancelled", "Operation cancelled.")

    def about(self):
        about_dialog = AboutDialog(self.root)

    def retrieve_future_ideas(self):
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                future_ideas = data.get("future_ideas", [])
                if future_ideas:
                    idea_list = "\n".join([f"Idea: {idea['idea']}\nOutline: {idea['outline']}\n" for idea in future_ideas])
                    messagebox.showinfo("Future Ideas", idea_list)
                else:
                    messagebox.showinfo("Future Ideas", "No future ideas have been entered yet.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while retrieving future ideas: {str(e)}")

    def enter_future_ideas(self):
        dialog_window = tk.Toplevel(self.root)
        dialog_window.title("Enter Future Ideas")
        dialog_window.attributes('-topmost', True)

        frame = tk.Frame(dialog_window)
        frame.pack(padx=10, pady=10)

        label_idea = tk.Label(frame, text="Enter Future Idea:")
        label_idea.grid(row=0, column=0, sticky=tk.W)

        entry_idea = tk.Entry(frame, width=50)
        entry_idea.grid(row=0, column=1, padx=5)

        label_outline = tk.Label(frame, text="Enter Outline:")
        label_outline.grid(row=1, column=0, sticky=tk.W)

        entry_outline = tk.Entry(frame, width=50)
        entry_outline.grid(row=1, column=1, padx=5)

        def save_idea():
            idea = entry_idea.get().strip()
            outline = entry_outline.get().strip()
            if idea and outline:
                with open(self.data_file, 'r+') as f:
                    data = json.load(f)
                    future_ideas = data.get("future_ideas", [])
                    future_ideas.append({"idea": idea, "outline": outline})
                    f.seek(0)
                    json.dump(data, f)
                    messagebox.showinfo("Success", "Future idea and outline saved successfully.")
            else:
                messagebox.showwarning("Incomplete Information", "Please enter both idea and outline.")

        button_save = tk.Button(frame, text="Save", command=save_idea)
        button_save.grid(row=2, column=0, columnspan=2, pady=5)

    def save_data(self):
        data = {
            "tasks": self.tasks,
            "task_goals": self.task_goals,
            "morning_routine": self.morning_routine,
            "deleted_tasks": self.deleted_tasks,
            "eisenhower_matrix_results": self.eisenhower_matrix_results,
            "last_review_results": self.last_review_results,
            "future_ideas": []  # Initialize future_ideas as an empty list
        }
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving data: {str(e)}")


    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.tasks = data.get("tasks", [])
                self.task_goals = data.get("task_goals", {})
                self.morning_routine = data.get("morning_routine", [])
                self.deleted_tasks = data.get("deleted_tasks", [])
                self.eisenhower_matrix_results = data.get("eisenhower_matrix_results")
                self.last_review_results = data.get("last_review_results")
        except FileNotFoundError:
            messagebox.showinfo("File Not Found", "No previous data found. Starting with empty data.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading data: {str(e)}")

    def load_backup_data(self):
        try:
            shutil.copyfile(self.data_file, self.backup_file)
        except FileNotFoundError:
            pass

    def display_eisenhower_matrix_results(self):
        if self.eisenhower_matrix_results:
            categories = ""
            for category, tasks in self.eisenhower_matrix_results.items():
                tasks_str = "\n".join([f"- {task}" for task in tasks])
                categories += f"{category}:\n{tasks_str}\n\n"
            self.eisenhower_matrix_display.delete(1.0, tk.END)
            self.eisenhower_matrix_display.insert(tk.END, categories)
        else:
            self.eisenhower_matrix_display.delete(1.0, tk.END)
            self.eisenhower_matrix_display.insert(tk.END, "No tasks have been categorized yet.")

    def run(self):
        self.root.mainloop()

    def yes_no_prompt(self, title, question):
        answer = messagebox.askyesno(title, question)
        if answer:
            return 'Yes'
        else:
            return 'No'

if __name__ == "__main__":
    planner_gui = DailyPlannerGUI()
    planner_gui.run()
