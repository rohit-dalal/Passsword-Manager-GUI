from cryptography.fernet import Fernet
from customtkinter import (
    CTk,
    CTkButton,
    CTkEntry,
    CTkFrame,
    CTkLabel,
    CTkSlider,
    CTkToplevel,
)
from pathlib import Path
import sqlite3
from tkinter import ttk, IntVar, Menu
from _tkinter import TclError
from random import choice
from string import ascii_letters
from pyperclip import copy
from os import system, mkdir, path, environ, stat
import platform
from re import match
from tkinter.messagebox import showerror, showinfo, showwarning
from webbrowser import open as open_link




class App(CTk):
    def __init__(self):
        super().__init__()
        self.count = True

        self.db_path = self.get_db_path()
        self.key_path = self.get_key_path()

        # Writing up db and key files
        self.dirFile_setup()

        # Secret key
        self.b64key = self.key()

        self.title("Password Manager")
        # set_default_color_theme('blue')
        self.geometry("720x480")

        # Creating a top menu
        self.top_menu_bar = Menu(self)

        # Configure the top menu
        self.config(menu=self.top_menu_bar)

        # File menu
        self.file_menu = Menu(self.top_menu_bar, tearoff=0)
        self.top_menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Home", command=self.show_home)
        self.file_menu.add_command(
            label="Generate Password", command=self.show_generatepass
        )
        self.file_menu.add_command(label="Show Key", command=lambda: self.alert('warning', text=str(self.b64key)))
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)

        # Database menu
        self.file_menu = Menu(self.top_menu_bar, tearoff=0)
        self.top_menu_bar.add_cascade(label="Database", menu=self.file_menu)
        self.file_menu.add_command(label="Reset", command=self.reset_db_confirm_window)

        # Developer menu
        self.file_menu = Menu(self.top_menu_bar, tearoff=0)
        self.top_menu_bar.add_cascade(label="Developer", menu=self.file_menu)
        self.file_menu.add_command(label="Support me", command=self.support_me)

        # Creating frames for top menu bar
        self.home_frame = CTkFrame(self)
        self.generatepass_frame = CTkFrame(self)

        # Showing home (db tabes) window
        self.show_home()

        # Generate password frame
        slider_frame = CTkFrame(self.generatepass_frame)
        slider_frame.pack(padx=20, pady=20)
        CTkLabel(
            slider_frame,
            text="Password length",
        ).pack()
        self.slider_label = CTkLabel(
            slider_frame, text="8 ", corner_radius=10, width=40
        )
        self.slider_label.pack(side="left")
        self.slider_ = CTkSlider(
            slider_frame,
            from_=5,
            to=20,
            variable=IntVar(value=8),
            number_of_steps=15,
            command=self.slider_value,
        )
        self.slider_.pack(padx=1, pady=20)
        self.generate_btn = CTkButton(
            self.generatepass_frame,
            text="Generate password",
            command=self.generate_pass,
        ).pack()

        self.gen_pass_output_frame = CTkFrame(self.generatepass_frame)
        self.generated_output_ = CTkLabel(
            self.gen_pass_output_frame, text="", width=200
        )
        self.copy_ = CTkButton(
            self.gen_pass_output_frame, text="Copy", width=20, command=self.copy_text
        )
        self.generated_output_.pack(side="left")
        self.copy_.pack()
        # self.gen_pass_output_frame.pack()

        # Database table setup
        self.tree = ttk.Treeview(
            self.home_frame, columns=["App", "Email", "Password"], show="headings"
        )
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 13, "bold"))
        style.configure("Treeview", font=(None, 11))

        self.tree.column("0", anchor="center")
        self.tree.column("1", anchor="center")
        self.tree.column("2", anchor="center")

        self.tree.heading("App", text="APP")
        self.tree.heading("Email", text="EMAIL")
        self.tree.heading("Password", text="PASSWORD")

        # Create a right-click menu
        self.right_click_menu = Menu(self.tree, tearoff=0)
        self.right_click_menu.add_command(label="Copy", command=self.copy_mailPass)
        self.right_click_menu.add_command(label="Add", command=self.add_item_window)
        self.right_click_menu.add_command(
            label="Delete", command=self.delete_item_confirm_window
        )
        self.right_click_menu.add_command(label="Edit", command=self.update_item_window)

        self.setup_db()
        self.insert_data_to_table()

        # Binding the righ-click functionality
        self.tree.bind("<Button-3>", self.popup_menu)
        # self.tree.bind('<TreeviewSelect>', self.selected_item)
        self.tree.pack(fill="both", expand=True)

        # Binding scrolbar to table
        vsb = ttk.Scrollbar(self.tree, command=self.tree.yview)

        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")

    def show_home(self):
        self.generatepass_frame.pack_forget()
        self.home_frame.pack(fill="both", expand=1)

    def show_generatepass(self):
        self.home_frame.pack_forget()
        self.generatepass_frame.pack(fill="both", expand=1)

    def reset_db_confirm_window(self):
        self.reset_window = CTkToplevel(self)
        self.reset_window.title("Reset database")
        self.reset_window.geometry("400x200")
        CTkLabel(
            self.reset_window, text="Do you want to Reset Database?", font=("bold", 20)
        ).pack(pady=20)
        btn_frame = CTkFrame(
            self.reset_window,
            width=40,
        )
        CTkButton(
            btn_frame,
            text="Yes",
            command=self.reset_db,
        ).pack()
        CTkButton(
            btn_frame, text="No", command=lambda: self.reset_window.destroy()
        ).pack()
        btn_frame.pack()

    def insert_data_to_table(self):
        table_data = self.tree.get_children()

        if len(table_data) == 0:
            data = self.show_db_data()
            for i in range(len(data)):
                self.tree.insert("", "end", values=[data[i][0], data[i][1], data[i][2]])
        elif len(table_data) != 0:
            # Deleting table data
            for item in table_data:
                self.tree.delete(item)
            # Inserting data into table
            data = self.show_db_data()
            for i in range(len(data)):
                self.tree.insert("", "end", values=[data[i][0], data[i][1], data[i][2]])
            self.tree.update()

    def reset_db(self):
        try:
            if platform.system() == "Windows":
                system(f"del {self.db_path}")
            elif platform.system() == "Linux":
                system(f"rm {self.db_path}")
            else:
                self.alert("error", "[-] It is soon comming for your OS.")
            self.quit()

        except Exception as e:
            print("[-] Error occurred::\n", e)

    def update_item_to_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE passwords SET APP=?, EMAIL=?, PASSWORD=? WHERE (APP=? AND EMAIL=?)""",
                (
                    self.update_name.get(),
                    self.update_email.get(),
                    self.encrypt(self.update_password.get()),
                    self.item[0],
                    self.item[1],
                ),
            )
            conn.commit()

        except sqlite3.Error as e:
            print("[-] Error occurred::\n", e)
        finally:
            self.update_frame.destroy()
            # Refreshing tables
            self.insert_data_to_table()
            conn.close()

    def update_item_validation(self):
        name_, email_, passwd_ = (
            self.update_name.get(),
            self.update_email.get(),
            self.update_password.get(),
        )

        app_valid = name_.isalnum() and len(name_) >= 3
        email_valid = match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email_)
        passwd_valid = len(passwd_) >= 8

        if app_valid and email_valid and passwd_valid:
            self.update_item_to_db()
        else:
            if not app_valid:
                self.erase_color_after_delay(self.update_name, "red")
            if not email_valid:
                self.erase_color_after_delay(self.update_email, "red")
            if not passwd_valid:
                self.erase_color_after_delay(self.update_password, "red")

    def update_item_window(self):
        try:
            id = self.tree.selection()[0]
            self.item = self.tree.item(id)["values"]

            # Creating new frame to update new items
            self.update_frame = CTkToplevel(self)
            self.update_frame.title("Update")
            self.update_frame.geometry("300x300")

            self.update_name = CTkEntry(
                self.update_frame, placeholder_text="App Name", width=250
            )
            self.update_name.pack(padx=10, pady=10)
            self.update_name.insert(0, self.item[0])
            self.update_email = CTkEntry(
                self.update_frame, placeholder_text="Email Address", width=250
            )
            self.update_email.pack(padx=10, pady=10)
            self.update_email.insert(0, self.item[1])
            self.update_password = CTkEntry(
                self.update_frame, placeholder_text="Password", width=250
            )
            self.update_password.pack(padx=10, pady=10)
            self.update_password.insert(0, self.decrypt(self.item[2]))
            CTkButton(
                self.update_frame, text="Update", command=self.update_item_validation
            ).pack()
            CTkButton(
                self.update_frame,
                text="Cancel",
                command=lambda: self.update_frame.destroy(),
            ).pack()

        except IndexError:
            self.alert("error", "Item is not selected.")
        except Exception as e:
            print("[-] Error occurred::\n", e)

    def delete_item_confirm_window(self):
        try:
            # Check row is selected or not
            self.tree.selection()[0]

            # Delte window frame
            self.delete_window = CTkToplevel(self)
            self.delete_window.title("Delete")
            self.delete_window.geometry("400x200")
            CTkLabel(
                self.delete_window, text="Do you want to Delete?", font=("bold", 20)
            ).pack(pady=20)
            btn_frame = CTkFrame(
                self.delete_window,
                width=40,
            )
            CTkButton(btn_frame, text="Yes", command=self.delete_item_from_db).pack()
            CTkButton(
                btn_frame, text="No", command=lambda: self.delete_window.destroy()
            ).pack()
            btn_frame.pack()

        except IndexError:
            self.alert("error", "Item is not selected.")
        except Exception as e:
            print("[-] Error occurred::\n", e)

    def delete_item_from_db(self):
        id = self.tree.selection()[0]
        item = self.tree.item(id)["values"]

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """DELETE FROM passwords WHERE (APP=? AND EMAIL=?)""",
                (item[0], item[1]),
            )
            conn.commit()
        except IndexError:
            self.alert("error", "Item is not selected.")

        except sqlite3.Error as e:
            print("Error occurred:", e)

        finally:
            self.delete_window.destroy()
            # Refreshing table
            self.insert_data_to_table()
            conn.close()

    def add_to_db(self):
        title, email, passwd = (
            self.app_name.get(),
            self.email.get(),
            self.password.get(),
        )

        if (title and email and passwd) is not (None or ""):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO passwords (APP, EMAIL, PASSWORD) VALUES (?, ?, ?)""",
                    (title, email, self.encrypt(passwd)),
                )
                conn.commit()

            except sqlite3.Error as e:
                print("[-] Error occurred::\n", e)
            finally:
                self.add_frame.destroy()
                # Refreshing tables
                self.insert_data_to_table()
                conn.close()
        else:
            self.alert("error", "You haven't entered anything.")

    def add_item_validation(self):
        app_name, email_addr, passwd = (
            self.app_name.get(),
            self.email.get(),
            self.password.get(),
        )

        app_valid = app_name.isalnum() and len(app_name) >= 3
        email_valid = match(
            "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email_addr
        )
        passwd_valid = len(passwd) >= 8

        if app_valid and email_valid and passwd_valid:
            self.add_to_db()
        else:
            if not app_valid:
                self.app_name.configure(fg_color='red')
            if not email_valid:
                self.email.configure(fg_color='red')
            if not passwd_valid:
                self.password.configure(fg_color='red')

    # def erase_color_after_delay(self, widget, color, delay=1000):
    #     try:
    #         widget.configure(fg_color=color)  # Set the color
    #         self.after(delay, lambda: widget.configure(fg_color="white"))
    #     except TclError:
    #         pass

    def add_item_window(self):
        # Creating new frame to add new items
        self.add_frame = CTkToplevel(self)
        self.add_frame.title("Add")
        self.add_frame.geometry("300x300")

        self.app_name = CTkEntry(self.add_frame, placeholder_text="App Name", width=250)
        self.app_name.pack(padx=10, pady=10)
        self.email = CTkEntry(
            self.add_frame, placeholder_text="Email Address", width=250
        )
        self.email.pack(padx=10, pady=10)
        self.password = CTkEntry(self.add_frame, placeholder_text="Password", width=250)
        self.password.pack(padx=10, pady=10)
        CTkButton(self.add_frame, text="Add", command=self.add_item_validation).pack()
        CTkButton(
            self.add_frame, text="Cancel", command=lambda: self.add_frame.destroy()
        ).pack()

    def popup_menu(self, event):
        # Display the right-click menu at the clicked position
        self.right_click_menu.post(event.x_root, event.y_root)

    def copy_mailPass(self):
        try:
            id = self.tree.selection()[0]
            item = self.tree.item(id)["values"]
            copy(f"{item[1]:[2]}")

        except IndexError:
            self.alert('error', 'Item is not selected.')

    def copy_text(self):
        try:
            value = self.generated_output_.cget("text")
            return copy(value)
        
        except Exception as e:
            print("[-] Error occurred::\n", e)
            

    def slider_value(self, value):
        self.slider_label.configure(text=int(value))

    def generate_pass(self):
        pas_length = int(self.slider_.get())
        letters = ascii_letters + "!@#$%&*+({[}]|=)"
        password = "".join(choice(letters) for _ in range(pas_length))
        self.generated_output_.configure(text=password)
        self.gen_pass_output_frame.pack(padx=20, pady=20)

    def get_key_path(self):
        if platform.system() == "Windows":
            key_path_windows = "C:\\Users\\" + environ["USERNAME"]+ "\\.PasswordManager"
            return key_path_windows + "\\PassManager.key"
        
        elif platform.system() == "Linux":
            linux_base_path = "/home/" + environ["USERNAME"]+ "/.PasswordManager"
            return linux_base_path + "/.PasswordManager" + "/PassManger.key"
        
    def get_db_path(self):
        if platform.system() == 'Windows':
            db_path_windows = "C:\\Users\\" + environ["USERNAME"]+ "\\.PasswordManager"
            return db_path_windows + "\\PassManager.db"
        
        elif platform.system() == "Linux":
            linux_base_path = "/home/" + environ["USERNAME"]+ "/.PasswordManager"
            return linux_base_path + "/.PasswordManager" + "/PassManger.db"
            

    def dirFile_setup(self):
        # Checking the key and db to abvoid overwrite

        if platform.system() == "Windows":
            dir_path_windows = "C:\\Users\\" + environ["USERNAME"]+ "\\.PasswordManager"
            
            if not path.exists(dir_path_windows):
                mkdir(dir_path_windows)
                if not path.isfile(self.get_db_path()):
                    Path(self.get_db_path()).touch()

                if not path.isfile(self.get_key_path()):
                    Path(self.get_key_path()).touch()

            else:
                if not path.isfile(self.get_db_path()):
                    Path(self.get_db_path()).touch()

                if not path.isfile(self.get_key_path()):
                    Path(self.get_key_path()).touch()

        elif platform.system() == "Linux":
            base_path_linux = "/home/" + environ["USERNAME"]+ "/.PasswordManager"

            if not path.exists(base_path_linux):
                mkdir(base_path_linux)
                if not path.isfile(self.get_db_path()):
                    Path(self.get_db_path()).touch()

                if not path.isfile(self.get_key_path()):
                    Path(self.get_key_path()).touch()

            else:
                if not path.isfile(self.get_db_path()):
                    Path(self.get_db_path()).touch()

                if not path.isfile(self.get_key_path()):
                    Path(self.get_key_path()).touch()
        else:
            self.alert(
                'warning', text="We haven't tested it out on your OS, it may not work properly."
            )

    def setup_db(self):
        try:
            if stat(self.db_path).st_size == 0:
                print('table created.') #---------------------chech it out
                if self.count:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute(
                        """CREATE TABLE IF NOT EXISTS passwords (APP VARCHAR(255), EMAIL VARCHAR(255), PASSWORD VARCHAR(255))"""
                    )
                    conn.commit()
                    conn.close()
                    self.count = False
                else:
                    print("[-] Database setup is not created::")
        except sqlite3.DatabaseError:
            self.alert('error', 'Database file is corrupted.')

    def show_db_data(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM passwords")
            rows = cursor.fetchall()
            return rows
        except sqlite3.Error as e:
            print("[-] Error occurred::\n", e)
        finally:
            conn.close()

    def key(self):
        # Checking if file already exists or not
        try:# Assign key to file
            if path.exists(self.key_path) and stat(self.key_path).st_size == 0:
                key_ = Fernet.generate_key()
                with open(self.key_path, "wb") as file:
                    file.write(key_)
                    file.close()
                return key_
            
            else:  # Opening exist file
                with open(self.key_path, "r") as file:
                    return file.readlines()[0]
        except TypeError:
            self.alert("error", "There is some issue with writing 'key' to file.")

    def encrypt(self, text):
        try:
            fernet = Fernet(self.b64key)
            Crypto = fernet.encrypt(text.encode("utf-8")).decode("utf-8")
            return Crypto
        except ValueError:
            self.alert('error', 'Encryption "key" is corrupted.')

    def decrypt(self, CryptoText):
        try:
            fernet = Fernet(self.b64key)
            decMessage = fernet.decrypt(CryptoText.encode("utf-8")).decode("utf-8")
            return decMessage
        except ValueError:
            self.alert('error', 'Encryption "key" is corrupted.')

    def alert(self, title, text):
        if title == "error":
            showerror(title.capitalize(), text.capitalize())
        elif title == "info":
            showinfo(title.capitalize(), text.capitalize())
        elif title == 'warning':
            print(text)
            showwarning(title.capitalize(), text.capitalize())
        else:
            print(f"Messagebox doesn't support {title}.")

    def support_me(self):
        return open_link("https://www.buymeacoffee.com/rohitdalal0")


if __name__ == "__main__":
    app = App()
    app.mainloop()