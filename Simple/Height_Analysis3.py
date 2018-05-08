# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 19:10:09 2017

@author: TWang

Height Analysis 3.0 

update: focus on fix camera 

through video playing, select reference plane, then select known height reference object 

"""
import cv2

import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageTk

import tkinter.messagebox

import time

import numpy as np

from skimage import feature, color, transform, io

class Video_Player:
    
    def __init__(self):
        """ Initialize application which uses OpenCV + Tkinter. """
        
        #some flags 
        self.current_image = None  # current image from the camera
        self.isPlaying = True; # Video Playing status flag 

        self.Frame_Step = 1   #default frame step 
        
        self.In_Previous = False #default previous and latter are false
        self.In_Latter = False
        
        self.video_status = None
        

        self.window = tk.Tk()  # initialize root window
        self.window.title('OSI Video Player')  # set window title
        self.window.geometry('1920x1080')
        
        self.window.protocol('WM_DELETE_WINDOW', self.destructor)  # self.destructor function gets fired when the window is closed
        
        #define operation menu bar 
        menubar =tk.Menu(self.window)
        
        ##deine a empty parent-menu(file)
        filemenu =tk.Menu(menubar,tearoff=0)
        
        ##name previous defined empty menu unit as File 
        menubar.add_cascade(label="File", menu=filemenu)
        
        #define three son menus 
        filemenu.add_command(label="Open", command=self.File_open)
        
        filemenu.add_command(label="Play", command=self.File_Play)
        
        filemenu.add_command(label="Close", command=self.destructor)
        
        self.window.config(menu=menubar)
        
        #define second empty parent-menu (model)
        about_menu=tk.Menu(menubar,tearoff=0)
        
        menubar.add_cascade(label="About", menu=about_menu)
        
        about_menu.add_command(label = 'About', compound = 'left', command = self.display_about_messagebox)
        
        about_menu.add_command(label='Help', compound='left', command = self.display_help_messagebox)
        
        #video display area
        self.panel = tk.Label(self.window, text ="video display area",font="Verdana 16 bold",bg = "light gray")  # initialize image panel
        self.panel.place(x=10, y=10, width=1280, height=720)
        
        #Height analysis area
        self.canvas_height = tk.Canvas(self.window, bg = "light gray")  # initialize image panel
        self.canvas_height.create_text(10,10,anchor="nw", text = "Height Analysis",font="Verdana 14 bold")
        self.canvas_height.place(x=1300, y=170, width=610, height=150)
        
        # create a button, that when pressed, open height analysis module
        btn_Height_Analysis = tk.Button(self.canvas_height, text='Height Analysis', command=self.Height_Analysis_Click)
        btn_Height_Analysis.place(x=10, y=50)
        
        #select height reference selection
        button_Reference_Selection = tk.Button(self.canvas_height, text='Reference Selection', command=self.Reference_Selection_Click)
        button_Reference_Selection.place(x=150, y=50)
        
        #fix camera height analysis
        button_Fix_Cam_Height_Analysis = tk.Button(self.canvas_height, text='Fix_Cam_Height_Analysis', command=self.Fix_Cam_Height_Analysis)
        button_Fix_Cam_Height_Analysis.place(x=10, y=100)
        
        '''video player operation control panel'''
        #panel area
        self.canvas_control_panel = tk.Canvas(self.window, bg = "light gray")
        self.canvas_control_panel.create_text(10,10,anchor="nw", text = "control panel",font="Verdana 14 bold")
        self.canvas_control_panel.place(x=10, y=745, width=1280, height=230)
        
        #some texts
        self.canvas_control_panel.create_text(10,60,anchor="nw", text = "step :",font="Verdana 12 ")
        self.canvas_control_panel.create_text(10,120,anchor="nw", text = "Current Frame :",font="Verdana 12 ")
        self.canvas_control_panel.create_text(10,180,anchor="nw", text = "File :",font="Verdana 12 ")
        
        #define step ebetween the current and next frame
        self.step = tk.IntVar()
        self.step.set(self.Frame_Step)
        self.step_entry = tk.Entry(self.canvas_control_panel, textvariable=self.step, width = 10)
        self.step_entry.place(x=80, y=60)
        
        #define step entry save button
        button_save_step_entry = tk.Button(self.canvas_control_panel, text = 'Save', font="Verdana 10 ", bg = "SkyBlue1", command=self.button_save_step_entry)
        button_save_step_entry.place(x = 160, y =60)
        #define current frame variable label 
        self.Current_Frame = tk.StringVar()
        self.Current_Frame.set('')
        self.Current_Frame_Label = tk.Label(self.canvas_control_panel, textvariable=self.Current_Frame, bg = "light gray",font="Verdana 12 ")
        self.Current_Frame_Label.place(x=150, y=120)
        
        #define video file name label 
        self.Video_Name = tk.StringVar()
        self.Video_Name.set('')
        self.Video_Name_Label = tk.Label(self.canvas_control_panel, textvariable=self.Video_Name, bg = "light gray",font="Verdana 12 ")
        self.Video_Name_Label.place(x=80, y=180)
        
        # define video status
        self.canvas_control_panel.create_text(600,60,anchor="nw", text = "Status :",font="Verdana 12 ")
        self.Status = tk.StringVar()
        self.Status.set('')
        self.Status_Label = tk.Label(self.canvas_control_panel, textvariable=self.Status, bg = "light gray",font="Verdana 12 ")
        self.Status_Label.place(x=700, y=60)
        
        #define four control buttons
        button_previous = tk.Button(self.canvas_control_panel, text = 'Previous', font="Verdana 10 ", bg = "SkyBlue1", command=self.Previous_Frame)
        button_previous.place(x=530, y=120)
        
        button_play = tk.Button(self.canvas_control_panel, text = 'Continue', font="Verdana 10 ", bg = "SkyBlue1", command=self.Continue_Frame)
        button_play.place(x=605, y=120)
        
        button_previous = tk.Button(self.canvas_control_panel, text = 'Stop', font="Verdana 10 ", bg = "SkyBlue1", command=self.Stop_Frame)
        button_previous.place(x=680, y=120)
        
        button_play = tk.Button(self.canvas_control_panel, text = 'Latter', font="Verdana 10 ", bg = "SkyBlue1", command=self.Latter_Frame)
        button_play.place(x=730, y=120)
        
        button_Save_Frame = tk.Button(self.canvas_control_panel, text = 'Save Frame', font="Verdana 10 ", bg = "SkyBlue1", command=self.Save_Frame)
        button_Save_Frame.place(x=790, y=120)
        
        #define total frames
        self.canvas_control_panel.create_text(600,180,anchor="nw", text = "Total Frames :",font="Verdana 12 ")
        self.Total_Frames = tk.StringVar()
        self.Total_Frames.set('')
        self.Total_Frames_Label = tk.Label(self.canvas_control_panel, textvariable=self.Total_Frames, bg = "light gray",font="Verdana 12 ")
        self.Total_Frames_Label.place(x=750, y=180)
        
        #define FPS
        self.canvas_control_panel.create_text(950,120,anchor="nw", text = "FPS :",font="Verdana 12 ")
        self.FPS = tk.StringVar()
        self.FPS.set('')
        self.FPS_Label = tk.Label(self.canvas_control_panel, textvariable=self.FPS, bg = "light gray",font="Verdana 12 ")
        self.FPS_Label.place(x=1000, y=120)
        
        #define the slider
        self.Slider_button_width = 15
        self.slider_button_height = 10
        self.Slider_IsMoving = False #True when slider is moving
        self.slider_canvas = tk.Canvas(self.window, bg = "DarkOrange1")
        self.slider_canvas.place(x=10, y=730, width=1280, height=15)
        
        self.Slider_button_x0 = 0
        self.Slider_button_y0 = 0
        self.slider_canvas.create_rectangle(self.Slider_button_x0, self.Slider_button_y0, self.Slider_button_x0 + 15, self.Slider_button_y0 +15, fill='gray26')
    
    
    def Fix_Cam_Height_Analysis(self):
        '''
        step 1 : Line detection using canny edge detection
        '''
        if self.isPlaying == False:
            
            self.current_Frame = int (self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            
            self.Current_Frame.set(self.current_Frame)
                
            success, Height_Analysis_Img = self.cap.read()
            
            '''
            step 1 : Line detection using canny edge detection
            
            Uses canny edge detection and then finds (small) lines using probabilstic
            hough transform as edgelets.
            Parameters
            ----------
            image: ndarray
                Image for which edgelets are to be computed.
            sigma: float
                Smoothing to be used for canny edge detection.
            Returns
            -------
            locations: ndarray of shape (n_edgelets, 2)
                Locations of each of the edgelets.
            directions: ndarray of shape (n_edgelets, 2)
                Direction of the edge (tangent) at each of the edgelet.
            strengths: ndarray of shape (n_edgelets,)
                Length of the line segments detected for the edgelet.
            '''
#==============================================================================
#             #compute median of singel channel pixel intensities
#             median_intensity = np.median(Height_Analysis_Img)
#             
#             #apply cutomatic thresholding
#             sigma = 0.33
#             lower = int (max(0, (1.0 - sigma) * median_intensity))
#             upper = int (min(255, (1.0 + sigma) * median_intensity))
#             
#             Height_Analysis_Img_Gray = cv2.cvtColor(Height_Analysis_Img, cv2.COLOR_BGR2GRAY)
#             
#             Height_Analysis_Img_blurred = cv2.GaussianBlur(Height_Analysis_Img_Gray, (3, 3),0)
#             
#             Canny_edge = cv2.Canny(Height_Analysis_Img_blurred, lower, upper)
#==============================================================================
            Height_Analysis_Img_Gray = color.rgb2gray(Height_Analysis_Img)
            
            sigma = 3
            
            Canny_edge = feature.canny(Height_Analysis_Img_Gray, sigma)
            
            lines = transform.probabilistic_hough_line(Canny_edge, line_length = 3, line_gap = 2)
            
            locations = []
            directions = []
            strengths = []

            for p0, p1 in lines:
                p0, p1 = np.array(p0), np.array(p1)
                locations.append((p0 + p1) / 2)
                directions.append(p1 - p0)
                strengths.append(np.linalg.norm(p1 - p0))
                
            #convert to numpy arrays and normalize
            locations = np.array(locations)
            directions = np.array(directions)
            strengths = np.array(strengths)
            
            directions = np.array(directions) / \
                np.linalg.norm(directions, axis=1)[:, np.newaxis]

            """
            Step 2 : Compute lines in homogenous system for edglets.
            Parameters
            ----------
            edgelets: tuple of ndarrays
                (locations, directions, strengths) as computed by `compute_edgelets`.
            Returns
            -------
            lines: ndarray of shape (n_edgelets, 3)
                Lines at each of edgelet locations in homogenous system.
            """
            

            cv2.imshow("canny edge", Canny_edge)
            cv2.waitKey(5000)
            
            cv2.destroyWindow()
            
    
    def Reference_Selection_Click(self):
        
        if self.isPlaying == False:
            pass
        
    
    def Height_Analysis_Click(self):
        '''
        after pedestrain detection, input bounding box, conduct height analysis for each box, return height value(High, Meidum, Short)
        adaptive reference window:count each frame bounding box number, find a window containing more bounding box 
        for box in reference window, sort them accoding to box height, then find medium, short and high
        '''
        print('self.Height_Analysis = True ')
        self.Height_Analysis = True  # Height Analysis flag
        
    def display_about_messagebox(self,event=None):
        tk.messagebox.showinfo('About', '{}{}'.format('OSI Video Player', '\n Write using Opencv Python tkinter \n Make by Tao WANG  '))
        
    def display_help_messagebox(self, event=None):
        tk.messagebox.showinfo('Help', 'Email:shawnli@yahoo.com')
        
    def button_save_step_entry(self):
        print(self.step_entry.get())
        self.Frame_Step = int (self.step_entry.get())
        
    def Save_Frame(self):
        '''
        save Frame to file 
        
        '''
        if self.isPlaying == False :
            
            self.current_Frame = int (self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            
            self.Current_Frame.set(self.current_Frame)
                
            reti, Saved_Img = self.cap.read()
    
            file_Save_Frame = filedialog.asksaveasfile(mode='w', defaultextension=".png", filetypes=(("PNG file", "*.png"),("All Files", "*.*") ))
            
            if file_Save_Frame:
                cv2.imwrite(file_Save_Frame.name, Saved_Img)
                
        print("[INFO] Save_Frame Done...")
            
    
    def Previous_Frame(self):
        '''
        To show the previous Frame of video 
        '''
        print("[INFO] Previous Frame...")
        
        if self.isPlaying == False and self.In_Previous ==False:
            
            self.In_Previous = True
            
            self.current_Frame = int (self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            
            self.Current_Frame.set(self.current_Frame)
            
            if self.current_Frame + self.Frame_Step < self.total:
                
                self.current_Frame = self.current_Frame - self.Frame_Step
                self.cap.set(cv2.CAP_PROP_POS_FRAMES,self.current_Frame)
                
                print(self.current_Frame)
                ret,frame = self.cap.read()
                
                if ret:
                    
                    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
                        
                    current_image = Image.fromarray(cv2image)  # convert image for PIL
                
                    imgtk = ImageTk.PhotoImage(image=current_image)  # convert image for tkinter
                
                    self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
                
                    self.panel.config(image=imgtk)  # show the image
                    
                    #video playing, slider moving 
                    self.Slider_Moving_width = (self.current_Frame / self.total) * 1280 
                    self.slider_canvas.create_rectangle(self.Slider_button_x0 + self.Slider_Moving_width, self.Slider_button_y0, self.Slider_Moving_width +  self.Slider_button_x0 + 15, self.Slider_button_y0 +15, fill='gray26')
                
        elif self.isPlaying ==False and self.In_Previous ==True:
            
            if self.current_Frame + self.Frame_Step < self.total:
                
                self.current_Frame = self.current_Frame - self.Frame_Step
                self.cap.set(cv2.CAP_PROP_POS_FRAMES,self.current_Frame)
                
                self.Current_Frame.set(self.current_Frame)
                
                ret,frame = self.cap.read()
                
                if ret:
                    
                    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
                        
                    current_image = Image.fromarray(cv2image)  # convert image for PIL
                
                    imgtk = ImageTk.PhotoImage(image=current_image)  # convert image for tkinter
                
                    self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
                
                    self.panel.config(image=imgtk)  # show the image
                    
                    #video playing, slider moving 
                    self.Slider_Moving_width = (self.current_Frame / self.total) * 1280 
                    self.slider_canvas.create_rectangle(self.Slider_button_x0 + self.Slider_Moving_width, self.Slider_button_y0, self.Slider_Moving_width +  self.Slider_button_x0 + 15, self.Slider_button_y0 +15, fill='gray26')
                
        else:
            
            pass
                
    def Continue_Frame(self):
        if self.isPlaying == False:
            
            self.isPlaying = True
            self.File_Play()
        else:
            pass
        
        
    def Stop_Frame(self):
        self.isPlaying = False
        #change status to Playing 
        self.status = 'Stop'
        self.Status.set(self.status)
        
        self.slider_canvas.tag_bind('objTag','<ButtonPress-1>',self.onObjectClick)

    def Latter_Frame(self):
        '''
        To show the Latter Frame of video 
        '''
        print("[INFO] Latter Frame...")
        
        if self.isPlaying == False and self.In_Latter ==False :
            
            self.In_Latter = True
            
            self.current_Frame = int (self.cap.get(cv2.CAP_PROP_POS_FRAMES))
    
            
            if self.current_Frame + self.Frame_Step < self.total:
                
                self.current_Frame = self.current_Frame + self.Frame_Step
                
                self.cap.set(cv2.CAP_PROP_POS_FRAMES,self.current_Frame)
                
                self.Current_Frame.set(self.current_Frame)
                
                ret,frame = self.cap.read()
                
                if ret:
                    
                    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
                        
                    current_image = Image.fromarray(cv2image)  # convert image for PIL
                
                    imgtk = ImageTk.PhotoImage(image=current_image)  # convert image for tkinter
                
                    self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
                
                    self.panel.config(image=imgtk)  # show the image
                    
                    #video playing, slider moving 
                    self.Slider_Moving_width = (self.current_Frame / self.total) * 1280 
                    self.slider_canvas.create_rectangle(self.Slider_button_x0 + self.Slider_Moving_width, self.Slider_button_y0, self.Slider_Moving_width +  self.Slider_button_x0 + 15, self.Slider_button_y0 +15, fill='gray26')
                
                    
        elif self.isPlaying ==False and self.In_Latter ==True:
            
            if self.current_Frame + self.Frame_Step < self.total:
                
                self.current_Frame = self.current_Frame + self.Frame_Step
                
                self.cap.set(cv2.CAP_PROP_POS_FRAMES,self.current_Frame)
                
                self.Current_Frame.set(self.current_Frame)
                
                ret,frame = self.cap.read()
                
                if ret:
                    
                    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
                        
                    current_image = Image.fromarray(cv2image)  # convert image for PIL
                
                    imgtk = ImageTk.PhotoImage(image=current_image)  # convert image for tkinter
                
                    self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
                
                    self.panel.config(image=imgtk)  # show the image
                    
                    #video playing, slider moving 
                    self.Slider_Moving_width = (self.current_Frame / self.total) * 1280 
                    self.slider_canvas.create_rectangle(self.Slider_button_x0 + self.Slider_Moving_width, self.Slider_button_y0, self.Slider_Moving_width +  self.Slider_button_x0 + 15, self.Slider_button_y0 +15, fill='gray26')
    
        else:
           
           pass
    
    
    def File_open(self):
            #return filedialog.askopenfilename()
            self.window.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("video files","*.mp4"),("all files","*.*")))
            print (self.window.filename)
            self.Video_Name.set(self.window.filename)
            self.cap = cv2.VideoCapture(self.window.filename)
            self.isPlaying = True
            
            
            
            print("File_open done!")
            
    def File_Play(self):
            """ Get frame from the video stream and show it in Tkinter """
            if self.isPlaying == True: 
                success, frame = self.cap.read() # read frame from video stream             
        
                if success:  # frame captured without any errors 
                    
                    if self.Frame_Step == 1:
                
                        tic = time.time()
                    
                        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
                        
                        self.current_image = Image.fromarray(cv2image)  # convert image for PIL
                    
                        imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
                    
                        self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
                    
                        self.panel.config(image=imgtk)  # show the image
                        
                        toc = time.time()
                        
                        durr = float(toc - tic)
                        
                        self.fps = 1.0 / durr
                        
                        self.FPS.set(int(self.fps))
                        
                        #change status to Playing 
                        self.status = 'Playing'
                        self.Status.set(self.status)
                        
                        #total frames                      
                        self.total = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))                        
                        self.Total_Frames.set(self.total)
                        
                        #current frame
                        self.current_Frame = int (self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                        self.Current_Frame.set(self.current_Frame)
                        
                        #video playing, slider moving 
                        self.Slider_Moving_width = (self.current_Frame / self.total) * 1280 
                        self.slider_canvas.create_rectangle(self.Slider_button_x0 + self.Slider_Moving_width, self.Slider_button_y0, self.Slider_Moving_width +  self.Slider_button_x0 + 15, self.Slider_button_y0 +15, fill='gray26')
                        
                                
                    else :
                        
                        self.current_Frame = int (self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                
                        
                        if self.current_Frame + self.Frame_Step < self.total:
                            
                            self.current_Frame = self.current_Frame + self.Frame_Step
                            
                            self.cap.set(cv2.CAP_PROP_POS_FRAMES,self.current_Frame)
                            
                            self.Current_Frame.set(self.current_Frame)
                            
                            ret,frame = self.cap.read()
                            
                            if ret:
                                
                                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
                                    
                                current_image = Image.fromarray(cv2image)  # convert image for PIL
                            
                                imgtk = ImageTk.PhotoImage(image=current_image)  # convert image for tkinter
                            
                                self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
                            
                                self.panel.config(image=imgtk)  # show the image
                                
                                #video playing, slider moving 
                                self.Slider_Moving_width = (self.current_Frame / self.total) * 1280 
                                self.slider_canvas.create_rectangle(self.Slider_button_x0 + self.Slider_Moving_width, self.Slider_button_y0, self.Slider_Moving_width +  self.Slider_button_x0 + 15, self.Slider_button_y0 +15, fill='gray26')
                            
                        
                self.window.after(5, self.File_Play)  # call the same function after 5 milliseconds
                
    
    def destructor(self):
        """ Destroy the window object and release all resources """
        print("[INFO] closing...")
        self.window.destroy()
        self.cap.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application
          
Run = Video_Player()

Run.window.mainloop()
