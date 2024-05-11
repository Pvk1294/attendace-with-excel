import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import datetime
import subprocess
import numpy as np
import os
import util
import pandas as pd


class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry('1200x520+350+100')

        self.log_button_main_window = util.get_button(self.main_window, 'login', 'green', self.login)
        self.log_button_main_window.place(x=750, y=300)

        self.register_new_user_button_main_window = util.get_button(self.main_window, 'register new user', 'red', self.register_new_user, fg='black')
        self.register_new_user_button_main_window.place(x=750, y=400)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.excel_path = os.path.abspath('./attendance_log.xlsx')
        self.create_excel_sheet()

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)

        self._label = label
        self.process_webcam()

    def create_excel_sheet(self):
        if not os.path.exists(self.excel_path):
            df = pd.DataFrame(columns=['Serial No', 'Name', 'Date/Time' , 'Present'])
            df.to_excel(self.excel_path, index=False)

    def process_webcam(self):
        ret, frame = self.cap.read()

        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(10, self.process_webcam)

    def login(self):
        unknown_img_path = './.temp.jpg'

        cv2.imwrite(unknown_img_path, self.most_recent_capture_arr)

        try:
            output = str(subprocess.check_output(['face_recognition', '--tolerance', '0.6', self.db_dir, unknown_img_path]))
        except subprocess.CalledProcessError as e:
            output = str(e.output)

        name = util.recognize(self.most_recent_capture_arr, self.db_dir)

        if name == 'unknown_person' or name == 'no_person_found':
           util.msg_box('Error', 'Unknown user. Please register new user or try again')
        else:
            self.mark_attendance(name)
            util.msg_box('Error', 'Unknown user. Please register a new user or try again')


        os.remove(unknown_img_path)

    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry('1200x520+370+120')

        self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Accept', 'green', self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=750, y=300)

        self.try_again_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Try again', 'red', self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750, y=400)

        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=20, y=10, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.entry_text_register_new_user = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=750, y=150)

        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'Please, \ninput Name: ')
        self.text_label_register_new_user.place(x=750, y=70)

        self.register_new_user_window.capture_label = self.capture_label

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def start(self):
        self.main_window.mainloop()

    def accept_register_new_user(self):
        name = self.entry_text_register_new_user.get(1.0, "end-1c")

        df = pd.read_excel(self.excel_path)
        if name in df['Name'].tolist():
            util.msg_box('Error', 'User {} already exists!' .format(name))
            return
        
        registerd_face_path = os.path.join(self.db_dir, '{}.jpg'.format(name))

        cv2.imwrite(os.path.join(self.db_dir, '{}.jpg'.format(name)), self.register_new_user_capture)

        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        serial_no = len(df) + 1
        new_data = {'Serial No': serial_no, 'Name': name, 'Present': 'Yes', 'Date/Time': current_date}
        new_df = pd.DataFrame([new_data])
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_excel(self.excel_path, index=False)

        util.msg_box('Success!', 'User {} was registered successfully!' .format(name))

        self.register_new_user_window.destroy()

    def mark_attendance(self, name):
        df = pd.read_excel(self.excel_path)

        current_date = datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S%f")

        if name not in df['Name'].tolist():
            serial_no = len(df)+1
            new_data = {'Serial No':serial_no, 'Name': name,'Date/Time': current_date, 'Present': 'Yes'} 
            new_df = pd.DataFrame([new_data])
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_excel(self.excel_path, index=False)

if __name__ == "__main__":
    app = App()
    app.start()
