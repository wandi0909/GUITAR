# FR EXTRACTION GUI #

#importing relevant packages

from tkinter import *
from tkinter.ttk import *
import tkinter as tki
import tkinter.font
from tkinter.filedialog import askopenfilenames 
import time
import numpy as np
import glob
import sys
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pyvista as pv
import diplib as dip
from skimage import measure
import cv2
from matplotlib.animation import FuncAnimation


# TO DO: 
#        add ability to select file type for saving plots (eps, png, pdf, ...)
#        spherical coords?? - medium high prio
#        allow oblique twist/extraction planes - medium prio
#        include stepsize for analysis?? - low prio
#        show error messages (e.g., when nothing loaded in) - low prio
#        allow different shapes for MM algs - low prio
#        show pre-view of plot customization? - low prio
#        visualize sampling - low prio


Name = 'Detect_FluxRope'

### Window for asking operation mode ###

ws2 = Tk()

col2_px = 500
col3_px = 800
basecol1_px = 170
basecol2_px = 945

if sys.platform.startswith('linux'):
    horsz = 1250
    horsz_ws2 = 320
    horsz_plotws = 340
    saved_px = 1175
    upload_px = 355
else:
    horsz = 1200
    horsz_ws2 = 260
    saved_px = 1145
    upload_px = 325
    horsz_plotws = 300

ws2.geometry(str(horsz_ws2)+'x175')
default_font = tki.font.nametofont("TkDefaultFont")
default_font2 = tki.font.nametofont("TkTextFont")
default_font3 = tki.font.nametofont("TkFixedFont")
default_font.configure(size=9)
default_font2.configure(size=9)
default_font3.configure(size=9)
ws2.title("What Operation Mode?")

Style().configure("TButton", padding=1)

spacing = 1.05
wi = 9
#mode options
Modes = ('Full Extraction', 'Post-Processing', 'Get Source Points', 'Get Difference Map Points')
mode_var = tki.StringVar(value='')
mode_var.set(Modes)

#mode listbox
Label(ws2, text="Please indicate the mode you want to use: ").place(x = 20, y = 10)
listbox1 = tki.Listbox(ws2, listvariable = mode_var, width = 35, height=4, selectmode=tki.SINGLE)
listbox1.place(x = 20, y = 40)

#variable that controls which "main" window to open
selected_index = -1

#plotting variables:
#colormap strings
global cmaps
cmaps = []
for cmap_id in plt.colormaps():
    cmaps.append(cmap_id)

global color_val
color_val = tki.StringVar(value='') #for colormap    
color_val.set(tuple(cmaps))

#function to kill a window
def destroy_widget(widget):
    widget.destroy()

#change listbox variable to the selected mode
def items_selected(event):
    global selected_index
    selected_index = listbox1.curselection()[0]
listbox1.bind('<<ListboxSelect>>', items_selected)

#destroy window if a mode is selected
def destroy_ws2(selected_index):
    if selected_index != -1:
        ws2.destroy()

def destroy_varws(varws, x_str, y_str, z_str, proxy_str):
    testvar = 4
    strings = [x_str, y_str, z_str, proxy_str]
    for j in range(4):
        if strings[j] == '':
            testvar -= 1
    if testvar == 4:
        varws.destroy()

def destroy_varws2(varws, proxy_str):
    if proxy_str != '':
        varws.destroy()

#confirm-button which destroys the window if a mode has been selected        
conf_btn = Button(ws2, text='Confirm', command = lambda:destroy_ws2(selected_index))
conf_btn.place(x = 85, y = 120)
ws2.mainloop()


####### main window ########

#open main window if corresponding mode is selected
if selected_index == 0:
    ws = Tk()
    ws.title(Name)
    ws.geometry(str(horsz)+'x670') 
    
    default_font = tki.font.nametofont("TkDefaultFont")
    default_font2 = tki.font.nametofont("TkTextFont")
    default_font3 = tki.font.nametofont("TkFixedFont")
    default_font.configure(size=9)
    default_font2.configure(size=9)
    default_font3.configure(size=9)
    Style().configure("TButton", padding=1)
    
    # create default values/pre-define variables
    file_path = []
    twist1 = []
    num = 0
    canv_num = 0
    basename = tki.StringVar(value='')
    x_str = tki.StringVar(value = '')
    y_str = tki.StringVar(value = '')
    z_str = tki.StringVar(value = '')
    proxy_str = tki.StringVar(value = '')
    spin_val = tki.StringVar(value=0)
    spin2_val = tki.StringVar(value=0)
    spin3_val = tki.StringVar(value=0)
    spin4_val = tki.StringVar(value=0)
    spin5_val = tki.StringVar(value=0)
    spin6_val = tki.StringVar(value=0)
    spin7_val = tki.StringVar(value=0)
    spin8_val = tki.StringVar(value=0)
    spin9_val = tki.StringVar(value=0)
    x1_in = tki.StringVar(value = 0)
    x2_in = tki.StringVar(value = 0)
    y1_in = tki.StringVar(value = 0)
    y2_in = tki.StringVar(value = 0)
    x11_in = tki.StringVar(value = 0)
    x22_in = tki.StringVar(value = 0)
    y11_in = tki.StringVar(value = 0)
    y22_in = tki.StringVar(value = 0)
    xsteps = tki.StringVar(value = 0)
    lower = tki.StringVar(value = 1)
    upper = tki.StringVar(value = 2)
    overlap = tki.StringVar(value = 0.1)
    ope = tki.StringVar(value = 0)
    ope2 = tki.StringVar(value = 0)
    Thr = tki.StringVar(value = 0.8)
    Thr2 = tki.StringVar(value = 1)
    TwistPolarity = tki.StringVar(value=1)
    
    #cX variables tell if a function has been called for the first time
    #this has the purpose to create the widgets only once, to not overload the GUI with hidden widgets
    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    c11, c12, c13, c14, c15, c16, c17, c18, c19, c20 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    c21 = 0
    
    #file-types that can be read in
    Allowed_Types = ('npz', 'npz+vtr', 'vtr (not recommended - slow!)')
    type_var = tki.StringVar(value='')
    type_var.set(Allowed_Types)
    
    #listbox for selecting which file type to read in
    type_lbl = Label(ws, text="Please indicate the type of files you want to load: ")
    type_lbl.place(x = 20, y = 10)
    listbox2 = tki.Listbox(ws, listvariable = type_var, height=3, width = 50, selectmode=tki.SINGLE)
    listbox2.place(x = 20, y = 35)
    
    #variable that controls what file type has been selected
    selected_type = -1
    
    # selection function
    def type_selected(event):
        global selected_type
        selected_type = listbox2.curselection()[0]    
    
    listbox2.bind('<<ListboxSelect>>', type_selected)
    
    #function that destroys selection and opens read-in process
    def TypeDestroy():
        if selected_type != -1:
            destroy_widget(type_lbl)
            destroy_widget(listbox2)
            destroy_widget(conf_btn2)
        
        #read in buttons for npz
        if (selected_type == 0):
            ws.wm_title(Name+" <Full Extraction Mode> npz")
            addat = Label(ws, text='Load Proxy Maps as .npz:')
            addat.place(x = 20, y = 10)
            
            addatbtn = Button(ws, text ='Choose Files', command = lambda:open_file_npz()) 
            addatbtn.place(in_ = addat, y = 0, relx = spacing)
        
            varws = tki.Toplevel(ws)
            varws.title("Variable Specifications")
            varws.geometry(str(horsz_plotws)+'x200')
            varws.grab_set()
            
            default_font = tki.font.nametofont("TkDefaultFont")
            default_font2 = tki.font.nametofont("TkTextFont")
            default_font3 = tki.font.nametofont("TkFixedFont")
            default_font.configure(size=9)
            default_font2.configure(size=9)
            default_font3.configure(size=9)
            
            xlabel = Label(varws, text = 'Insert Coordinate 1:')
            xlabel.place(x = 20, y = 10)            
            xcoord = Entry(varws, textvariable = x_str, width = 10)
            xcoord.place(in_ = xlabel, y = 0, relx = spacing)
            
            ylabel = Label(varws, text = 'Insert Coordinate 2:')
            ylabel.place(x = 20, y = 40)            
            ycoord = Entry(varws, textvariable = y_str, width = 10)
            ycoord.place(in_ = ylabel, y = 0, relx = spacing)
        
            zlabel = Label(varws, text = 'Insert Coordinate 3:')
            zlabel.place(x = 20, y = 70)            
            zcoord = Entry(varws, textvariable = z_str, width = 10)
            zcoord.place(in_ = zlabel, y = 0, relx = spacing)
        
            proxy_label = Label(varws, text = 'Insert Proxy:')
            proxy_label.place(x = 20, y = 100)            
            proxy_coord = Entry(varws, textvariable = proxy_str, width = 10)
            proxy_coord.place(in_ = proxy_label, y = 0, relx = spacing)
            
            conf_btn3 = Button(varws, text='Confirm', command = lambda:destroy_varws(varws, x_str.get(), y_str.get(), z_str.get(), proxy_str.get()))
            conf_btn3.place(x = 110, y = 150)

            upld = Button(ws, text='Load Files', command = lambda:uploadFiles_npz_only(file_path_npz, x_str.get(), y_str.get(), z_str.get(), proxy_str.get(), c1))
            upld.place(in_ = addatbtn, y = 0, relx = spacing)
            
        #read in buttons for vtr+npz 
        elif (selected_type == 1):
            ws.wm_title(Name+" <Full Extraction Mode> vtr+npz")
            addat = Label(ws, text='Load Proxy Maps as .vtr:')
            addat.place(x = 20, y = 10)
            
            addatbtn = Button(ws, text ='Choose Files', command = lambda:open_file())
            addatbtn.place(in_ = addat, y = 0, relx = spacing)
            
            upld = Button(ws, text='Load Files', command = lambda:uploadFiles(file_path))
            upld.place(in_ = addatbtn, y = 0, relx = spacing)
            
            varws = tki.Toplevel(ws)
            varws.title("Variable Specifications")
            varws.geometry(str(horsz_plotws)+'x100')
            varws.grab_set()
            
            default_font = tki.font.nametofont("TkDefaultFont")
            default_font2 = tki.font.nametofont("TkTextFont")
            default_font3 = tki.font.nametofont("TkFixedFont")
            default_font.configure(size=9)
            default_font2.configure(size=9)
            default_font3.configure(size=9)

            proxy_label = Label(varws, text = 'Insert Proxy:')
            proxy_label.place(x = 20, y = 10)            
            proxy_coord = Entry(varws, textvariable = proxy_str, width = 10)
            proxy_coord.place(in_ = proxy_label, y = 0, relx = spacing)
            
            conf_btn3 = Button(varws, text='Confirm', command = lambda:destroy_varws2(varws, proxy_str.get()))
            conf_btn3.place(x = 110, y = 60)
            
        #read in buttons for vtr
        elif (selected_type == 2):
            ws.wm_title(Name+" <Full Extraction Mode> vtr")
            addat = Label(ws, text='Load Proxy Maps as .vtr:')
            addat.place(x = 20, y = 10)

            addatbtn = Button(ws, text ='Choose Files', command = lambda:open_file())
            addatbtn.place(in_ = addat, y = 0, relx = spacing)
            
            upld = Button(ws, text='Load Files', command = lambda:uploadFiles_vtr(file_path, proxy_str.get(), c3))
            upld.place(in_ = addatbtn, y = 0, relx = spacing)
    
    #confirm button to destroy the selection widget
    conf_btn2 = Button(ws, text='Confirm', command = lambda:TypeDestroy())
    conf_btn2.place(x = 110, y = 95)
    
    #opens selected vtr files
    def open_file():
        global file_path
        file_path = askopenfilenames(initialdir='./', filetypes=[('VTR Files', '*vtr')])
    
    #opens selected npz files
    def open_file_npz():
        global file_path_npz
        file_path_npz = askopenfilenames(initialdir='./', filetypes=[('NPZ Files', '*npz')])  
    
    #function for saving plots
    def savefunc(Plotstr, contr, twist, filenames):
    
        #invoke window to customize plotting options
        plotws = tki.Toplevel(ws)
        plotws.title("Plot Specifications")
        plotws.geometry(str(horsz_plotws)+'x640')
        plotws.grab_set()
        
        default_font = tki.font.nametofont("TkDefaultFont")
        default_font2 = tki.font.nametofont("TkTextFont")
        default_font3 = tki.font.nametofont("TkFixedFont")
        default_font.configure(size=9)
        default_font2.configure(size=9)
        default_font3.configure(size=9)
        
        #Set colormap:
        global cmap_to_use
        cmap_to_use = "RdBu_r"
        
        #enable listbox if customize option is on
        def set_colormap(boxon):
            if boxon % 2 == 1:
                listbox3.config(state = "normal")
            else:
                listbox3.config(state = "disabled")

        #customization checkbox
        def_colormap = tki.IntVar(value = 0)
        check_default_colormap = Checkbutton(plotws, text = "Customize", variable = def_colormap, command = lambda:set_colormap(def_colormap.get()))        
        check_default_colormap.place(x = 10, y = 90)
        
        listbox3 = tki.Listbox(plotws, height=7, width = 25, selectmode=tki.SINGLE, exportselection=False)
        
        #listbox for colormaps
        for j in range(len(cmaps)):
            listbox3.insert(tki.END, cmaps[j])
        listbox3.place(x = 120, y = 35)
        listbox3.config(state = "disabled")
        
        colormap_lbl = Label(plotws, text = 'Choose Colormap:')    
        colormap_lbl.place(x = 120, y = 10)   
        
        #get selected colormap
        def color_selected(event):
            global cmap_to_use
            cmap_to_use = cmaps[int(listbox3.curselection()[0])]
    
        listbox3.bind('<<ListboxSelect>>', color_selected)       
        
        #Set figure size checkbox:
        def_figsize = tki.IntVar(value = 0)
        check_default_figsize = Checkbutton(plotws, text = "Customize", variable = def_figsize, command = lambda:set_figsize(def_figsize.get()))        
        check_default_figsize.place(x = 10, y = 180)   
        
        Label(plotws, text='Choose Figure Size:').place(x = 120, y = 180)
        
        #default figure sizes
        figure_x = tki.StringVar(value = "12")
        figure_y = tki.StringVar(value = "12")
        
        #entry boxes for figuresizes
        xfig = Label(plotws, text = 'x =')
        xfig.place(x = 120, y = 210)
        Enter_figx = Entry(plotws, textvariable = figure_x, width = 4)
        Enter_figx.place(in_ = xfig, y = 0, relx = spacing)
        yfig = Label(plotws, text = 'y =')
        yfig.place(in_ = Enter_figx, y = 0, relx = spacing)
        Enter_figy = Entry(plotws, textvariable = figure_y, width = 4)
        Enter_figy.place(in_ = yfig, y = 0, relx = spacing)
        
        Enter_figx.config(state = "disabled")
        Enter_figy.config(state = "disabled")
        
        #enable/disable figure entry boxes
        def set_figsize(boxon):
            if boxon % 2 == 1:
                Enter_figx.config(state = "normal")
                Enter_figy.config(state = "normal")
            else:
                Enter_figx.config(state = "disabled")
                Enter_figy.config(state = "disabled")
                
        #same thing with the plot title:
        def_title = tki.IntVar(value = 0)
        check_default_title = Checkbutton(plotws, text = "Customize", variable = def_title, command = lambda:set_plottitle(def_title.get()))        
        check_default_title.place(x = 10, y = 240)
        
        Label(plotws, text='Choose Figure Title:').place(x = 120, y = 240)
        
        figure_title = tki.StringVar(value = "")
        text_title = Text(plotws, height = 1, width = 20)
        text_title.place(x = 120, y = 270)        
        text_title.config(state = "disabled")
        
        def set_plottitle(boxon):
            if boxon % 2 == 1:
                text_title.config(state = "normal")
            else:
                text_title.config(state = "disabled")
        
        #same thing with the titlesize 
        def_titlesize = tki.IntVar(value = 0)
        check_default_titlesize = Checkbutton(plotws, text = "Customize", variable = def_titlesize, command = lambda:set_titlesize(def_titlesize.get()))        
        check_default_titlesize.place(x = 10, y = 300)   
        
        Label(plotws, text='Choose Title Size:').place(x = 120, y = 300)
        
        titlesize = tki.StringVar(value = "14")
        Enter_titlesize = Entry(plotws, textvariable = titlesize, width = 6)
        Enter_titlesize.place(x = 120, y = 330)       
        Enter_titlesize.config(state = "disabled")
        
        def set_titlesize(boxon):
            if boxon % 2 == 1:
                Enter_titlesize.config(state = "normal")
            else:
                Enter_titlesize.config(state = "disabled")
        
        #Same thing with the ticksizes 
        def_ticksize = tki.IntVar(value = 0)
        check_default_ticksize = Checkbutton(plotws, text = "Customize", variable = def_ticksize, command = lambda:set_ticksize(def_ticksize.get()))        
        check_default_ticksize.place(x = 10, y = 360)   
        
        Label(plotws, text='Choose Ticksize:').place(x = 120, y = 360)
        
        ticksize = tki.StringVar(value = "14")
        Enter_ticksize = Entry(plotws, textvariable = ticksize, width = 6)
        Enter_ticksize.place(x = 120, y = 390)       
        Enter_ticksize.config(state = "disabled")
        
        def set_ticksize(boxon):
            if boxon % 2 == 1:
                Enter_ticksize.config(state = "normal")
            else:
                Enter_ticksize.config(state = "disabled")

        #Same thing with the axis labels
        def_label = tki.IntVar(value = 0)
        check_default_label = Checkbutton(plotws, text = "Customize", variable = def_label, command = lambda:set_label(def_label.get()))        
        check_default_label.place(x = 10, y = 420)   
        
        Label(plotws, text='Choose Labels:').place(x = 120, y = 420)
        
        label_x = tki.StringVar(value = "")
        label_y = tki.StringVar(value = "")
        
        axx_lbl = Label(plotws, text = 'x =')
        axx_lbl.place(x = 120, y = 450)
        Enter_labelx = Entry(plotws, textvariable = label_x, width = 6)
        Enter_labelx.place(in_ = axx_lbl, y = 0, relx = spacing)
        axy_lbl = Label(plotws, text = 'y =')
        axy_lbl.place(in_ = Enter_labelx, y = 0, relx = spacing)
        Enter_labely = Entry(plotws, textvariable = label_y, width = 6)
        Enter_labely.place(in_ = axy_lbl, y = 0, relx = spacing)
        
        Enter_labelx.config(state = "disabled")
        Enter_labely.config(state = "disabled")
        
        def set_label(boxon):
            if boxon % 2 == 1:
                Enter_labelx.config(state = "normal")
                Enter_labely.config(state = "normal")
            else:
                Enter_labelx.config(state = "disabled")
                Enter_labely.config(state = "disabled")
                
        #same thing with the axis labelsize      
        def_labelsize = tki.IntVar(value = 0)
        check_default_labelsize = Checkbutton(plotws, text = "Customize", variable = def_labelsize, command = lambda:set_labelsize(def_labelsize.get()))        
        check_default_labelsize.place(x = 10, y = 480)   
        
        Label(plotws, text='Choose Labelsize:').place(x = 120, y = 480)
        
        labelsize = tki.StringVar(value = "14")
        Enter_labelsize = Entry(plotws, textvariable = labelsize, width = 6)
        Enter_labelsize.place(x = 120, y = 510)       
        Enter_labelsize.config(state = "disabled")
        
        def set_labelsize(boxon):
            if boxon % 2 == 1:
                Enter_labelsize.config(state = "normal")
            else:
                Enter_labelsize.config(state = "disabled")
        
        #Setting vmin/vmax values for the colormap
        def_minmax = tki.IntVar(value = 0)
        check_default_minmax = Checkbutton(plotws, text = "Customize", variable = def_minmax, command = lambda:set_minmax(def_minmax.get()))        
        check_default_minmax.place(x = 10, y = 540)   
        
        Label(plotws, text='Choose Colormap Limits:').place(x = 120, y = 540)
        
        vmin = tki.IntVar(value = -5)
        vmax = tki.IntVar(value = 5)
        
        vmin_lbl = Label(plotws, text = 'vmin =')
        vmin_lbl.place(x = 120, y = 570)
        Enter_vmin = Entry(plotws, textvariable = vmin, width = 4)
        Enter_vmin.place(in_ = vmin_lbl, y = 0, relx = spacing)
        vmax_lbl = Label(plotws, text = 'vmax =')
        vmax_lbl.place(in_ = Enter_vmin, y = 0, relx = spacing)
        Enter_vmax = Entry(plotws, textvariable = vmax, width = 4)
        Enter_vmax.place(in_ = vmax_lbl, y = 0, relx = spacing)
        
        Enter_vmin.config(state = "disabled")
        Enter_vmax.config(state = "disabled")
        
        def set_minmax(boxon):
            if boxon % 2 == 1:
                Enter_vmin.config(state = "normal")
                Enter_vmax.config(state = "normal")
            else:
                Enter_vmin.config(state = "disabled")
                Enter_vmax.config(state = "disabled")
        
        #confirm button to grab all variables from customization window and to destroy this window
        conf_btn3 = Button(plotws, text='Confirm', command = lambda:destroy_widget_2(plotws, def_colormap.get(), def_figsize.get(), def_title.get(), \
        def_titlesize.get(), def_ticksize.get(), def_label.get(), def_labelsize.get(), def_minmax.get(), figure_x.get(), figure_y.get(), text_title.get('1.0','end-1c'), titlesize.get(), \
        ticksize.get(), label_x.get(), label_y.get(), labelsize.get(), vmin.get(), vmax.get(), cmap_to_use))
        
        conf_btn3.place(x = 120, y = 605)
        
        #plotting+saving function, which saves the plot and destroys the customization window
        #boxonX are the variables communicating to the plotting function if the customization checkbox was on or off
        def destroy_widget_2(widget, boxon1, boxon2, boxon3, boxon4, boxon5, boxon6, boxon7, boxon8, figx, figy, title_name, titlesize, ticksize, labelx, labely,\
        labelsize, vmin, vmax, cmap_to_use):

            L = len(twist)
            
            #if not customized, use default values/settings:            
            if boxon1 % 2 == 0:
                cmap_to_use = "RdBu_r"
                
            if boxon2 % 2 == 0:
                figx = dim[1]/50
                figy = dim[0]/50
            else:
                figx = int(figx)
                figy = int(figy)
            
            if boxon4 % 2 == 0:
                titlesize = 14
            else:
                titlesize = int(titlesize)

            if boxon5 % 2 == 0:
                ticksize = 14
            else:
                ticksize = int(ticksize)

            if boxon7 % 2 == 0:
                labelsize = 14
            else:
                labelsize = int(labelsize)
            
            
            #plotting and saving the figuresizes
            
            #Plotstr controls which array to plot
            #contr tells which dimensions (for cartesian: x, y, z) to use
            for j in range(L):
                fig = Figure(figsize=(figx, figy))
                plot1 = fig.add_subplot(111)
                if Plotstr == 'Tw':
                    if contr == 'X': 
                        if boxon8 % 2 == 0:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = -5, vmax = 5, extent = [MinX, MaxX, MinZ, MaxZ])
                        else:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinZ, MaxZ])
                        if boxon3 % 2 == 0:
                            plot1.set_title("Proxy map no. "+str(j), fontsize = titlesize)
                        else: 
                            plot1.set_title(title_name, fontsize = titlesize)
                        if boxon6 % 2 == 0:
                            plot1.set_ylabel("y", fontsize = labelsize)
                            plot1.set_xlabel("x", fontsize = labelsize)
                        else: 
                            plot1.set_ylabel(labely, fontsize = labelsize)
                            plot1.set_xlabel(labelx, fontsize = labelsize)                            
                        plot1.tick_params(labelsize = ticksize)
                        fig.savefig(filenames+str(j)+'.png')
                    elif contr == 'Y':
                        if boxon8 % 2 == 0:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = -5, vmax = 5, extent = [MinY, MaxY, MinZ, MaxZ])
                        else:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinY, MaxY, MinZ, MaxZ])
                        if boxon3 % 2 == 0:
                            plot1.set_title("Proxy map no. "+str(j), fontsize = titlesize)
                        else: 
                            plot1.set_title(title_name, fontsize = titlesize)
                        if boxon6 % 2 == 0:
                            plot1.set_ylabel("y", fontsize = labelsize)
                            plot1.set_xlabel("x", fontsize = labelsize)
                        else: 
                            plot1.set_ylabel(labely, fontsize = labelsize)
                            plot1.set_xlabel(labelx, fontsize = labelsize)  
                        plot1.tick_params(labelsize = ticksize)
                        fig.savefig(filenames+str(j)+'.png')
                    elif contr == 'Z':
                        if boxon8 % 2 == 0:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = -5, vmax = 5, extent = [MinX, MaxX, MinY, MaxY])
                        else:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinY, MaxY])
                        if boxon3 % 2 == 0:
                            plot1.set_title("Proxy map no. "+str(j), fontsize = titlesize)
                        else: 
                            plot1.set_title(title_name, fontsize = titlesize)
                        if boxon6 % 2 == 0:
                            plot1.set_ylabel("y", fontsize = labelsize)
                            plot1.set_xlabel("x", fontsize = labelsize)
                        else: 
                            plot1.set_ylabel(labely, fontsize = labelsize)
                            plot1.set_xlabel(labelx, fontsize = labelsize)  
                        plot1.tick_params(labelsize = ticksize)
                        fig.savefig(filenames+str(j)+'.png')
                elif Plotstr == 'GrdTw':
                    if contr == 'X': 
                        if boxon8 % 2 == 0:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = -5, vmax = 5, extent = [MinX, MaxX, MinZ, MaxZ])
                        else:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinZ, MaxZ])
                        if boxon3 % 2 == 0:
                            plot1.set_title("Gradient+Twist no. "+str(j), fontsize = titlesize)
                        else: 
                            plot1.set_title(title_name, fontsize = titlesize)
                        if boxon6 % 2 == 0:                        
                            plot1.set_ylabel("y", fontsize = labelsize)
                            plot1.set_xlabel("x", fontsize = labelsize)
                        else: 
                            plot1.set_ylabel(labely, fontsize = labelsize)
                            plot1.set_xlabel(labelx, fontsize = labelsize)                             
                        plot1.tick_params(labelsize = ticksize)
                        fig.savefig(filenames+str(j)+'.png')
                    elif contr == 'Y':
                        if boxon8 % 2 == 0:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = -5, vmax = 5, extent = [MinY, MaxY, MinZ, MaxZ])
                        else:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinY, MaxY, MinZ, MaxZ])
                        if boxon3 % 2 == 0:
                            plot1.set_title("Gradient+Twist no. "+str(j), fontsize = titlesize)
                        else: 
                            plot1.set_title(title_name, fontsize = titlesize)
                        if boxon6 % 2 == 0:                            
                            plot1.set_ylabel("y", fontsize = labelsize)
                            plot1.set_xlabel("x", fontsize = labelsize)
                        else: 
                            plot1.set_ylabel(labely, fontsize = labelsize)
                            plot1.set_xlabel(labelx, fontsize = labelsize)                             
                        plot1.tick_params(labelsize = ticksize)
                        fig.savefig(filenames+str(j)+'.png')
                    elif contr == 'Z':
                        if boxon8 % 2 == 0:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = -5, vmax = 5, extent = [MinX, MaxX, MinY, MaxY])
                        else:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinY, MaxY])
                        if boxon3 % 2 == 0:
                            plot1.set_title("Gradient+Twist no. "+str(j), fontsize = titlesize)
                        else: 
                            plot1.set_title(title_name, fontsize = titlesize)
                        if boxon6 % 2 == 0:                            
                            plot1.set_ylabel("y", fontsize = labelsize)
                            plot1.set_xlabel("x", fontsize = labelsize)
                        else: 
                            plot1.set_ylabel(labely, fontsize = labelsize)
                            plot1.set_xlabel(labelx, fontsize = labelsize)                             
                        plot1.tick_params(labelsize = ticksize)
                        fig.savefig(filenames+str(j)+'.png')
                elif Plotstr == 'track':
                    if contr == 'X': 
                        if boxon8 % 2 == 0:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinZ, MaxZ])
                        else:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinZ, MaxZ])
                        if boxon3 % 2 == 0:
                            plot1.set_title("Tracked Shape, Frame "+str(j), fontsize = titlesize)
                        else: 
                            plot1.set_title(title_name, fontsize = titlesize)
                        if boxon6 % 2 == 0:                            
                            plot1.set_ylabel("y", fontsize = labelsize)
                            plot1.set_xlabel("x", fontsize = labelsize)
                        else: 
                            plot1.set_ylabel(labely, fontsize = labelsize)
                            plot1.set_xlabel(labelx, fontsize = labelsize)                             
                        plot1.tick_params(labelsize = ticksize)
                        fig.savefig(filenames+str(j)+'.png')
                    elif contr == 'Y':
                        if boxon8 % 2 == 0:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = 0, vmax = 1.5, extent = [MinY, MaxY, MinZ, MaxZ])
                        else:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinY, MaxY, MinZ, MaxZ])
                        if boxon3 % 2 == 0:
                            plot1.set_title("Tracked Shape, Frame "+str(j), fontsize = titlesize)
                        else: 
                            plot1.set_title(title_name, fontsize = titlesize)
                        if boxon6 % 2 == 0:                            
                            plot1.set_ylabel("y", fontsize = labelsize)
                            plot1.set_xlabel("x", fontsize = labelsize)
                        else: 
                            plot1.set_ylabel(labely, fontsize = labelsize)
                            plot1.set_xlabel(labelx, fontsize = labelsize)                             
                        plot1.tick_params(labelsize = ticksize)
                        fig.savefig(filenames+str(j)+'.png')
                    if contr == 'Z': 
                        if boxon8 % 2 == 0:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinY, MaxY])
                        else:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinY, MaxY])
                        if boxon3 % 2 == 0:
                            plot1.set_title("Tracked Shape, Frame "+str(j), fontsize = titlesize)
                        else: 
                            plot1.set_title(title_name, fontsize = titlesize)
                        if boxon6 % 2 == 0:                            
                            plot1.set_ylabel("y", fontsize = labelsize)
                            plot1.set_xlabel("x", fontsize = labelsize)
                        else: 
                            plot1.set_ylabel(labely, fontsize = labelsize)
                            plot1.set_xlabel(labelx, fontsize = labelsize)                             
                        plot1.tick_params(labelsize = ticksize)
                        fig.savefig(filenames+str(j)+'.png')
                elif Plotstr == 'processed':
                    if contr == 'X': 
                        if boxon8 % 2 == 0:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinZ, MaxZ])
                        else:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinZ, MaxZ])
                        if boxon3 % 2 == 0:
                            plot1.set_title("Tracked Shape, Frame "+str(j), fontsize = titlesize)
                        else: 
                            plot1.set_title(title_name, fontsize = titlesize)
                        if boxon6 % 2 == 0:                            
                            plot1.set_ylabel("y", fontsize = labelsize)
                            plot1.set_xlabel("x", fontsize = labelsize)
                        else: 
                            plot1.set_ylabel(labely, fontsize = labelsize)
                            plot1.set_xlabel(labelx, fontsize = labelsize)                             
                        plot1.tick_params(axis='both', which='major', labelsize = ticksize)
                        fig.savefig(filenames+str(j)+'.png')
                    elif contr == 'Y':
                        if boxon8 % 2 == 0:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = 0, vmax = 1.5, extent = [MinY, MaxY, MinZ, MaxZ])
                        else:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinY, MaxY, MinZ, MaxZ])
                        if boxon3 % 2 == 0:
                            plot1.set_title("Tracked Shape, Frame "+str(j), fontsize = titlesize)
                        else: 
                            plot1.set_title(title_name, fontsize = titlesize)
                        if boxon6 % 2 == 0:                            
                            plot1.set_ylabel("y", fontsize = labelsize)
                            plot1.set_xlabel("x", fontsize = labelsize)
                        else: 
                            plot1.set_ylabel(labely, fontsize = labelsize)
                            plot1.set_xlabel(labelx, fontsize = labelsize)                             
                        plot1.tick_params(axis='both', which='major', labelsize = ticksize)
                        fig.savefig(filenames+str(j)+'.png')
                    elif contr == 'Z':
                        if boxon8 % 2 == 0:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinY, MaxY])
                        else:
                            plot1.imshow(twist[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinY, MaxY])
                        if boxon3 % 2 == 0:
                            plot1.set_title("Tracked Shape, Frame "+str(j), fontsize = titlesize)
                        else: 
                            plot1.set_title(title_name, fontsize = titlesize)
                        if boxon6 % 2 == 0:                            
                            plot1.set_ylabel("y", fontsize = labelsize)
                            plot1.set_xlabel("x", fontsize = labelsize)
                        else: 
                            plot1.set_ylabel(labely, fontsize = labelsize)
                            plot1.set_xlabel(labelx, fontsize = labelsize)                             
                        plot1.tick_params(axis='both', which='major', labelsize = ticksize)
                        fig.savefig(filenames+str(j)+'.png')
            
            #correctly place label to indicate that the plot was indeed saved
            save_lbl = Label(ws, text = 'Saved!', foreground = 'green')    
            if Plotstr == 'Tw':
                save_lbl.place(x = 420, y = 500)
            elif Plotstr == 'GrdTw':
                save_lbl.place(x = 420, y = 560)    
            elif (Plotstr == 'processed'):
                save_lbl.place(x = saved_px, y = 280)
            elif (Plotstr == 'Open'):
                save_lbl.place(x = saved_px, y = 280)
            elif (Plotstr == 'track'):
                save_lbl.place(x = saved_px, y = 280)  
            
            #destroy the "saved" label
            ws.after(2000, destroy_widget, save_lbl)
            plotws.destroy()
        

    def savearr(arr, filename, Plotstr):
        L = len(arr)
        
        if contr == 'X':
            x_vec = np.linspace(MinX, MaxX, dim[1])
            z_vec = np.linspace(MinZ, MaxZ, dim[0])
            np.savez(filename+".npz", data = arr, x = x_vec, y = [yy], z = z_vec)
        elif contr == 'Y':
            y_vec = np.linspace(MinY, MaxY, dim[1])
            z_vec = np.linspace(MinZ, MaxZ, dim[0])
            np.savez(filename+".npz", data = arr, x = [xx], y = y_vec, z = z_vec)
        elif contr == 'Z':
            y_vec = np.linspace(MinY, MaxY, dim[0])
            x_vec = np.linspace(MinX, MaxX, dim[1])
            np.savez(filename+".npz", data = arr, x = x_vec, y = y_vec, z = [zz])
        
        save_lbl = Label(ws, text = 'Saved!', foreground = 'green')  
        
        if Plotstr == 'GrdTw':
            save_lbl.place(x = 420, y = 590) 
        elif (Plotstr == 'processed'):
            save_lbl.place(x = saved_px, y = 310)
        elif (Plotstr == 'Tw'):
            save_lbl.place(x = 420, y = 500)  
    
        ws.after(2000, destroy_widget, save_lbl)
    
    def uploadFiles_npz_only(file_path_npz, x_str, y_str, z_str, proxy_str, c):
        Test = []
        global twist1
        twist1 = []
        for j in range(0, len(file_path_npz)):
            Test.append(np.load(file_path_npz[j], allow_pickle = True))
            twist1.append(np.transpose(Test[int(j)][proxy_str]))
        
        global dim, MinX, MaxX, MinY, MaxY, MinZ, MaxZ, dx, dy, dz, contr
            
            #keylist = list(Test.keys())
        if ((len(Test[0][x_str]) > 1) & (len(Test[0][y_str]) > 1)):
            global zz
            zz = Test[0][z_str]
            #print(np.shape(Test[0]['z']))
            dim = [len(Test[0][y_str]), len(Test[0][x_str])]
            MinX = min(Test[0][x_str])
            MaxX = max(Test[0][x_str])
            MX = (MaxX-MinX)
            dx = MX/(dim[1]-1)
            MinY = min(Test[0][y_str])
            MaxY = max(Test[0][y_str])
            MY = (MaxY-MinY)
            dy = MY/(dim[0]-1)
            contr = 'Z'                
        elif (len(Test[0][x_str]) > 1):
            global yy
            yy = Test[0][y_str]
            #print(np.shape(Test[0]['x']))
            dim = [len(Test[0][z_str]), len(Test[0][x_str])]
            MinX = min(Test[0][x_str])
            MaxX = max(Test[0][x_str])
            MX = (MaxX-MinX)
            dx = MX/(dim[1]-1)
            MinZ = min(Test[0][z_str])
            MaxZ = max(Test[0][z_str])
            MZ = (MaxZ-MinZ)
            dz = MZ/(dim[0]-1)
            contr = 'X'
        elif (len(Test[0][y_str]) > 1):
            global xx
            xx = Test[0][x_str]
            dim = [len(Test[0][z_str]), len(Test[0][y_str])]
            MinY = min(Test[0][y_str])
            MaxY = max(Test[0][y_str])
            MY = (MaxY-MinY)
            dy = MY/(dim[1]-1)
            MinZ = min(Test[0][z_str])
            MaxZ = max(Test[0][z_str])
            MZ = (MaxZ-MinZ)
            dz = MZ/(dim[0]-1)
            contr = 'Y'
                
        Uploadnpz_lbl = Label(ws, text='Files Loaded Successfully!', foreground='green')
        Uploadnpz_lbl.place(x = 165, y = 40)
            
        ws.after(2000, destroy_widget, Uploadnpz_lbl)
        
        if c == 0:
            global Im_lbl
            Im_lbl = Label(ws, text = 'Choose Image Frame no.:')
            Im_lbl.place(x = 20, y = 70)
            global spin
            spin = Spinbox(ws, from_ = 0, to = len(file_path_npz)-1, textvariable = spin_val, wrap = True, width = wi)
            spin.place(in_ = Im_lbl, y = 0, relx = spacing)
            global vis_btn
            vis_btn = Button(ws, text='Visualize Proxy', command = lambda:Vis(contr, twist1, spin_val.get(), canv_num, c4, c5))
            vis_btn.place(in_ = spin, y = 0, relx = spacing)
        else: 
            spin.destroy()
            spin = Spinbox(ws, from_ = 0, to = len(file_path_npz)-1, textvariable = spin_val, wrap = True, width = wi)
            spin.place(in_ = Im_lbl, y = 0, relx = spacing)
            vis_btn.destroy()
            vis_btn = Button(ws, text='Visualize Proxy', command = lambda:Vis(contr, twist1, spin_val.get(), canv_num, c4, c5))
            vis_btn.place(in_ = spin, y = 0, relx = spacing)
        
        global c1
        c1 = 1
        
    def uploadFiles_npz(file_path_npz, proxy_str, c):
        Test = []
        global twist1
        twist1 = []
        for j in range(0, len(file_path_npz)):
            Test.append(np.load(file_path_npz[j], allow_pickle = True))
            twist1.append(np.transpose(Test[int(j)][proxy_str]))
        
        Uploadnpz_lbl = Label(ws, text='Files Loaded Successfully!', foreground='green')
        Uploadnpz_lbl.place(x = upload_px, y = 40)
        
        ws.after(2000, destroy_widget, Uploadnpz_lbl)
        
        if c == 0:
            global Im_lbl
            Im_lbl = Label(ws, text = 'Choose Image Frame no.:')
            Im_lbl.place(x = 20, y = 70)
            global spin
            spin = Spinbox(ws, from_ = 0, to = len(file_path_npz)-1, textvariable = spin_val, wrap = True, width = wi)
            spin.place(in_ = Im_lbl, y = 0, relx = spacing)
            global vis_btn        
            vis_btn = Button(ws, text='Visualize Proxy', command = lambda:Vis(contr, twist1, spin_val.get(), canv_num, c4, c5))
            vis_btn.place(in_ = spin, y = 0, relx = spacing)
        else: 
            spin.destroy()
            spin = Spinbox(ws, from_ = 0, to = len(file_path_npz)-1, textvariable = spin_val, wrap = True, width = wi)
            spin.place(in_ = Im_lbl, y = 0, relx = spacing)
            vis_btn.destroy()      
            vis_btn = Button(ws, text='Visualize Proxy', command = lambda:Vis(contr, twist1, spin_val.get(), canv_num, c4, c5))
            vis_btn.place(in_ = spin, y = 0, relx = spacing)
            
        global c2
        c2 = 1
    
    def uploadFiles(file_path):
        Dataset = pv.read(file_path)
        
        #take dimensions from data header
        xdim = Dataset[0].dimensions[0]
        ydim = Dataset[0].dimensions[1]
        zdim = Dataset[0].dimensions[2]
        global dim, MinX, MaxX, MinY, MaxY, MinZ, MaxZ, dx, dy, dz, contr
        
        if ((xdim > 1) & (ydim > 1)):
            dim = [ydim, xdim]
            #twist1 = np.zeros([N,zdim,xdim])   
            global zz
            X = Dataset[0].points[:,0]
            Y = Dataset[0].points[:,1]
            Z = Dataset[0].points[:,2]
            zz = Z[0]
            MinY = min(Y)
            MaxY = max(Y)
            MY = (max(Y)-min(Y))
            MinX = min(X)
            MaxX = max(X)
            MX = (max(X)-min(X))
            dy = MY/(dim[0]-1)
            dx = MX/(dim[1]-1)
            contr = 'Z'
        elif xdim > 1:            
            dim = [zdim, xdim]
            #twist1 = np.zeros([N,zdim,xdim])
            global yy
            X = Dataset[0].points[:,0]
            Y = Dataset[0].points[:,1]
            Z = Dataset[0].points[:,2]
            yy = Y[0]
            MinZ = min(Z)
            MaxZ = max(Z)
            MZ = (max(Z)-min(Z))
            MinX = min(X)
            MaxX = max(X)
            MX = (max(X)-min(X))
    
            dz = MZ/(dim[0]-1)
            dx = MX/(dim[1]-1)
            contr = 'X'
        else:
            dim = [zdim, ydim]
            #twist1 = np.zeros([N,zdim,ydim])
            global xx
            X = Dataset[0].points[:,0]
            Y = Dataset[0].points[:,1]
            Z = Dataset[0].points[:,2]
            xx = X[0]
            MinZ = min(Z)
            MaxZ = max(Z)
            MZ = (max(Z)-min(Z))
            MinY = min(Y)
            MaxY = max(Y)
            MY = (max(Y)-min(Y))
            contr = 'Y'
    
            dz = MZ/(dim[0]-1)
            dy = MY/(dim[1]-1)
                
        Uploadvtr_lbl = Label(ws, text='File Loaded Successfully!', foreground='green')
        Uploadvtr_lbl.place(x = upload_px, y = 10)
        
        ws.after(2000, destroy_widget, Uploadvtr_lbl)
        
        add = Label(ws, text='Load Proxy Maps as .npz:')
        add.place(x = 20, y = 40)
    
        add_btn = Button(ws, text ='Choose Files', command = lambda:open_file_npz()) 
        add_btn.place(in_ = add, y = 0, relx = spacing)
    
        upld2 = Button(ws, text='Load Files', command = lambda:uploadFiles_npz(file_path_npz, proxy_str.get(), c2))
        upld2.place(in_ = add_btn, y = 0, relx = spacing)
    
    def uploadFiles_vtr(file_path, proxy_str, c):
        Dataset = pv.read(file_path)
        
        #take dimensions from data header
        xdim = Dataset[0].dimensions[0]
        ydim = Dataset[0].dimensions[1]
        zdim = Dataset[0].dimensions[2]
        global dim, MinX, MaxX, MinY, MaxY, MinZ, MaxZ, dx, dy, dz, contr, twist1
        if ((xdim > 1) & (ydim > 1)):
            dim = [ydim, xdim]
            twist1 = np.zeros([len(file_path),ydim,xdim])   
            global zz
            X = Dataset[0].points[:,0]
            Y = Dataset[0].points[:,1]
            Z = Dataset[0].points[:,2]
            zz = Z[0]
            MinY = min(Y)
            MaxY = max(Y)
            MY = (max(Y)-min(Y))
            MinX = min(X)
            MaxX = max(X)
            MX = (max(X)-min(X))
            
            dy = MY/(dim[0]-1)
            dx = MX/(dim[1]-1)
            contr = 'Z'           
        elif xdim > 1:
            dim = [zdim, xdim]
            twist1 = np.zeros([len(file_path),zdim,xdim])   
            global yy
            X = Dataset[0].points[:,0]
            Y = Dataset[0].points[:,1]
            Z = Dataset[0].points[:,2]
            yy = Y[0]
            MinZ = min(Z)
            MaxZ = max(Z)
            MZ = (max(Z)-min(Z))
            MinX = min(X)
            MaxX = max(X)
            MX = (max(X)-min(X))
    
            dz = MZ/(dim[0]-1)
            dx = MX/(dim[1]-1)
            contr = 'X'              
        else:
            dim = [zdim, ydim]
            twist1 = np.zeros([len(file_path),zdim,ydim])
            global xx
            X = Dataset[0].points[:,0]
            Y = Dataset[0].points[:,1]
            Z = Dataset[0].points[:,2]
            xx = X[0]
            MinZ = min(Z)
            MaxZ = max(Z)
            MZ = (max(Z)-min(Z))
            MinY = min(Y)
            MaxY = max(Y)
            MY = (max(Y)-min(Y))
            contr = 'Y'
    
            dz = MZ/(dim[0]-1)
            dy = MY/(dim[1]-1)
        
        for j in range(0, len(file_path)):
            twist1[j,:,:] = np.reshape(Dataset[j][proxy_str], [dim[0],dim[1]])
                
        Uploadvtr_lbl = Label(ws, text='File loaded Successfully!', foreground='green')
        Uploadvtr_lbl.place(x = 165, y = 40)
        
        ws.after(2000, destroy_widget, Uploadvtr_lbl)
    
        if c == 0:
            global Im_lbl
            Im_lbl = Label(ws, text = 'Choose image frame no.:')
            Im_lbl.place(x = 20, y = 70)
            global spin
            spin = Spinbox(ws, from_ = 0, to = len(file_path)-1, textvariable = spin_val, wrap = True, width = wi)
            spin.place(in_ = Im_lbl, y = 0, relx = spacing)
            global vis_btn
            vis_btn = Button(ws, text='Visualize Proxy', command = lambda:Vis(contr, twist1, spin_val.get(), canv_num, c4, c5))
            vis_btn.place(in_ = spin, y = 0, relx = spacing)
        else:
            spin.destroy()
            spin = Spinbox(ws, from_ = 0, to = len(file_path)-1, textvariable = spin_val, wrap = True, width = wi)
            spin.place(in_ = Im_lbl, y = 0, relx = spacing)      
            vis_btn.destroy()
            vis_btn = Button(ws, text='Visualize Proxy', command = lambda:Vis(contr, twist1, spin_val.get(), canv_num, c4, c5))
            vis_btn.place(in_ = spin, y = 0, relx = spacing)
            
        global c3
        c3 = 1
    
    def Vis(contr, twist, num, num2, c, cc):
        plt.close()
        
        #fig = plt.figure()
        num = int(num)
        
        fig = Figure(figsize=(4.5,3.5))
        plot1 = fig.add_subplot(111)
        if contr == 'X': 
            plot1.imshow(twist[num], origin = "lower", cmap = "RdBu_r", vmin = -5, vmax = 5, extent = [MinX, MaxX, MinZ, MaxZ])
            plot1.set_title("Proxy map no. "+str(num), fontsize = 9)
            plot1.set_ylabel("y", fontsize = 9)
            plot1.set_xlabel("x", fontsize = 9)
            plot1.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Y': 
            plot1.imshow(twist[num], origin = "lower", cmap = "RdBu_r", vmin = -5, vmax = 5, extent = [MinY, MaxY, MinZ, MaxZ])
            plot1.set_title("Proxy map no. "+str(num), fontsize = 9)
            plot1.set_ylabel("y", fontsize = 9)
            plot1.set_xlabel("x", fontsize = 9)
            plot1.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Z':
            plot1.imshow(twist[num], origin = "lower", cmap = "RdBu_r", vmin = -5, vmax = 5, extent = [MinX, MaxX, MinY, MaxY])
            plot1.set_title("Proxy map no. "+str(num), fontsize = 9)
            plot1.set_ylabel("y", fontsize = 9)
            plot1.set_xlabel("x", fontsize = 9)
            plot1.tick_params(axis='both', which='major', labelsize=7)        
        
        if num2 == 0:
            global canvas
            canvas = FigureCanvasTkAgg(fig, master=ws)
            canvas.draw()
            canvas.get_tk_widget().place(x = 20, y = 100)
        else:
            canvas.get_tk_widget().destroy()
            canvas = FigureCanvasTkAgg(fig, master=ws)
            canvas.draw()
            canvas.get_tk_widget().place(x = 20, y = 100)
  
        global canv_num
        canv_num = 1
        
        global Plotstr
        Plotstr = 'Tw'
        
        if c == 0:
            TwPol = Label(ws, text='Indicate Polarity:')
            TwPol.place(x = 20, y = 470)
            
            spinPol = Spinbox(ws, values = (-1, 1), textvariable = TwistPolarity, wrap = True, width = wi)
            spinPol.place(in_ = TwPol, y = 0, relx = spacing)
            
            base_name = Text(ws, height = 1, width = 30)
            base_name.place(x = basecol1_px, y = 500)
            save_frames = Button(ws, text = 'Save Frames', command = lambda:savefunc(Plotstr, contr, twist, base_name.get('1.0','end-1c')))
            save_frames.place(x = 20, y = 500)
            
            base_name3 = Text(ws, height = 1, width = 30)
            base_name3.place(x = basecol1_px, y = 530)
            
            save_anim = Button(ws, text = 'Save Animation', command = lambda:saveanim_tw(twist1, base_name3.get('1.0','end-1c'), contr))
            save_anim.place(x = 20, y = 530)
            
            lower_lbl = Label(ws, text='Lower SE Size')
            lower_lbl.place(x = col2_px, y = 10)
            Grd_lower_entry = Entry(ws, textvariable = lower, width = wi)
            Grd_lower_entry.place(in_ = lower_lbl, y = 0, relx = spacing)
            upper_lbl = Label(ws, text='Upper SE Size')
            upper_lbl.place(x = col2_px, y = 40)
            Grd_upper_entry = Entry(ws, textvariable = upper, width = wi)
            Grd_upper_entry.place(in_ = upper_lbl, y = 0, relx = spacing)
            
            global Grd_button
            Grd_button = Button(ws, text = 'Calculate Grad+Proxy', command = lambda:Calc_grd_twist(lower.get(),upper.get(),twist1, TwistPolarity.get(), c5))
            Grd_button.place(x = col2_px, y = 70)        
        
        else:
            Grd_button.destroy()
            Grd_button = Button(ws, text = 'Calculate Grad+Proxy', command = lambda:Calc_grd_twist(lower.get(),upper.get(),twist1, TwistPolarity.get(), c5))
            Grd_button.place(x = col2_px, y = 70)    
            
        global c4
        c4 = 1
        
        if cc == 0:
            global vis_btn2
        elif cc == 1:
            vis_btn2.destroy()
            vis_btn2 = Button(ws, text='Visualize Grad+Proxy', command = lambda:Vis_GrdTwist(contr, Grd, spin_val.get(), canvas, c6))
            vis_btn2.place(in_ = Grd_button, y = 0, relx = spacing)     
    
    def saveanim_tw(arr, filename, contr):
        plotws = tki.Toplevel(ws)
        plotws.title("Plot Specifications")
        plotws.geometry(str(horsz_plotws)+'x640')
        plotws.grab_set()
        
        default_font = tki.font.nametofont("TkDefaultFont")
        default_font2 = tki.font.nametofont("TkTextFont")
        default_font3 = tki.font.nametofont("TkFixedFont")
        default_font.configure(size=9)
        default_font2.configure(size=9)
        default_font3.configure(size=9)
        
        #Set colormap:
        global cmap_to_use
        cmap_to_use = "RdBu_r"
        
        def set_colormap(boxon):
            if boxon % 2 == 1:
                listbox3.config(state = "normal")
            else:
                listbox3.config(state = "disabled")

        def_colormap = tki.IntVar(value = 0)
        check_default_colormap = Checkbutton(plotws, text = "Customize", variable = def_colormap, command = lambda:set_colormap(def_colormap.get()))        
        check_default_colormap.place(x = 10, y = 90)
        
        #cmap_to_use = tki.StringVar(value = '')
        listbox3 = tki.Listbox(plotws, height=7, width = 25, selectmode=tki.SINGLE, exportselection=False)
        
        for j in range(len(cmaps)):
            listbox3.insert(tki.END, cmaps[j])
        listbox3.place(x = 120, y = 35)
        listbox3.config(state = "disabled")
        
        colormap_lbl = Label(plotws, text = 'Choose Colormap:')    
        colormap_lbl.place(x = 120, y = 10)   
        
        def color_selected(event):
            global cmap_to_use
            cmap_to_use = cmaps[int(listbox3.curselection()[0])]
    
        listbox3.bind('<<ListboxSelect>>', color_selected)
        
        #Set figure size:
        def_figsize = tki.IntVar(value = 0)
        check_default_figsize = Checkbutton(plotws, text = "Customize", variable = def_figsize, command = lambda:set_figsize(def_figsize.get()))        
        check_default_figsize.place(x = 10, y = 180)   
        
        Label(plotws, text='Choose Figure Size:').place(x = 120, y = 180)
        
        figure_x = tki.StringVar(value = "12")
        figure_y = tki.StringVar(value = "12")
        
        xfig = Label(plotws, text = 'x =')
        xfig.place(x = 120, y = 210)
        Enter_figx = Entry(plotws, textvariable = figure_x, width = 4)
        Enter_figx.place(in_ = xfig, y = 0, relx = spacing)
        yfig = Label(plotws, text = 'y =')
        yfig.place(in_ = Enter_figx, y = 0, relx = spacing)
        Enter_figy = Entry(plotws, textvariable = figure_y, width = 4)
        Enter_figy.place(in_ = yfig, y = 0, relx = spacing)
        
        Enter_figx.config(state = "disabled")
        Enter_figy.config(state = "disabled")
        
        def set_figsize(boxon):
            if boxon % 2 == 1:
                Enter_figx.config(state = "normal")
                Enter_figy.config(state = "normal")
            else:
                Enter_figx.config(state = "disabled")
                Enter_figy.config(state = "disabled")  
        
        #Set title:
        def_title = tki.IntVar(value = 0)
        check_default_title = Checkbutton(plotws, text = "Customize", variable = def_title, command = lambda:set_plottitle(def_title.get()))        
        check_default_title.place(x = 10, y = 240)   
        
        Label(plotws, text='Choose Figure Title:').place(x = 120, y = 240)
        
        figure_title = tki.StringVar(value = "")
        text_title = Text(plotws, height = 1, width = 20)
        text_title.place(x = 120, y = 270)        
        text_title.config(state = "disabled")
        
        def set_plottitle(boxon):
            if boxon % 2 == 1:
                text_title.config(state = "normal")
            else:
                text_title.config(state = "disabled")
        
        #Set titlesize 
        def_titlesize = tki.IntVar(value = 0)
        check_default_titlesize = Checkbutton(plotws, text = "Customize", variable = def_titlesize, command = lambda:set_titlesize(def_titlesize.get()))        
        check_default_titlesize.place(x = 10, y = 300)   
        
        Label(plotws, text='Choose Title Size:').place(x = 120, y = 300)
        
        titlesize = tki.StringVar(value = "14")
        Enter_titlesize = Entry(plotws, textvariable = titlesize, width = 6)
        Enter_titlesize.place(x = 120, y = 330)       
        Enter_titlesize.config(state = "disabled")
        
        def set_titlesize(boxon):
            if boxon % 2 == 1:
                Enter_titlesize.config(state = "normal")
            else:
                Enter_titlesize.config(state = "disabled")
        
        #Set ticksize 
        def_ticksize = tki.IntVar(value = 0)
        check_default_ticksize = Checkbutton(plotws, text = "Customize", variable = def_ticksize, command = lambda:set_ticksize(def_ticksize.get()))        
        check_default_ticksize.place(x = 10, y = 360)   
        
        Label(plotws, text='Choose Ticksize:').place(x = 120, y = 360)
        
        ticksize = tki.StringVar(value = "14")
        Enter_ticksize = Entry(plotws, textvariable = ticksize, width = 6)
        Enter_ticksize.place(x = 120, y = 390)       
        Enter_ticksize.config(state = "disabled")
        
        def set_ticksize(boxon):
            if boxon % 2 == 1:
                Enter_ticksize.config(state = "normal")
            else:
                Enter_ticksize.config(state = "disabled")

        #Set label
        def_label = tki.IntVar(value = 0)
        check_default_label = Checkbutton(plotws, text = "Customize", variable = def_label, command = lambda:set_label(def_label.get()))        
        check_default_label.place(x = 10, y = 420)   
        
        Label(plotws, text='Choose Labels:').place(x = 120, y = 420)
        
        label_x = tki.StringVar(value = "")
        label_y = tki.StringVar(value = "")
        
        axx_lbl = Label(plotws, text = 'x =')
        axx_lbl.place(x = 120, y = 450)
        Enter_labelx = Entry(plotws, textvariable = label_x, width = 6)
        Enter_labelx.place(in_ = axx_lbl, y = 0, relx = spacing)
        axy_lbl = Label(plotws, text = 'y =')
        axy_lbl.place(in_ = Enter_labelx, y = 0, relx = spacing)
        Enter_labely = Entry(plotws, textvariable = label_y, width = 6)
        Enter_labely.place(in_ = axy_lbl, y = 0, relx = spacing)
        
        Enter_labelx.config(state = "disabled")
        Enter_labely.config(state = "disabled")
        
        def set_label(boxon):
            if boxon % 2 == 1:
                Enter_labelx.config(state = "normal")
                Enter_labely.config(state = "normal")
            else:
                Enter_labelx.config(state = "disabled")
                Enter_labely.config(state = "disabled")
                
        #Set labelsize      
        def_labelsize = tki.IntVar(value = 0)
        check_default_labelsize = Checkbutton(plotws, text = "Customize", variable = def_labelsize, command = lambda:set_labelsize(def_labelsize.get()))        
        check_default_labelsize.place(x = 10, y = 480)   
        
        Label(plotws, text='Choose Labelsize:').place(x = 120, y = 480)
        
        labelsize = tki.StringVar(value = "14")
        Enter_labelsize = Entry(plotws, textvariable = labelsize, width = 6)
        Enter_labelsize.place(x = 120, y = 510)       
        Enter_labelsize.config(state = "disabled")
        
        def set_labelsize(boxon):
            if boxon % 2 == 1:
                Enter_labelsize.config(state = "normal")
            else:
                Enter_labelsize.config(state = "disabled")
        
        #Set vmin/vmax
        def_minmax = tki.IntVar(value = 0)
        check_default_minmax = Checkbutton(plotws, text = "Customize", variable = def_minmax, command = lambda:set_minmax(def_minmax.get()))        
        check_default_minmax.place(x = 10, y = 540)   
        
        Label(plotws, text='Choose Colormap Limits:').place(x = 120, y = 540)
        
        vmin = tki.IntVar(value = -5)
        vmax = tki.IntVar(value = 5)                
        
        vmin_lbl = Label(plotws, text = 'vmin =')
        vmin_lbl.place(x = 120, y = 570)
        Enter_vmin = Entry(plotws, textvariable = vmin, width = 4)
        Enter_vmin.place(in_ = vmin_lbl, y = 0, relx = spacing)
        vmax_lbl = Label(plotws, text = 'vmax =')
        vmax_lbl.place(in_ = Enter_vmin, y = 0, relx = spacing)
        Enter_vmax = Entry(plotws, textvariable = vmax, width = 4)
        Enter_vmax.place(in_ = vmax_lbl, y = 0, relx = spacing)        
        
        Enter_vmin.config(state = "disabled")
        Enter_vmax.config(state = "disabled")
        
        def set_minmax(boxon):
            if boxon % 2 == 1:
                Enter_vmin.config(state = "normal")
                Enter_vmax.config(state = "normal")
            else:
                Enter_vmin.config(state = "disabled")
                Enter_vmax.config(state = "disabled")
        
        conf_btn3 = Button(plotws, text='Confirm', command = lambda:destroy_widget_3(plotws, def_colormap.get(), def_figsize.get(), def_title.get(), \
        def_titlesize.get(), def_ticksize.get(), def_label.get(), def_labelsize.get(), def_minmax.get(), figure_x.get(), figure_y.get(), text_title.get('1.0','end-1c'), titlesize.get(), \
        ticksize.get(), label_x.get(), label_y.get(), labelsize.get(), vmin.get(), vmax.get(), cmap_to_use))
        
        conf_btn3.place(x = 120, y = 605)
        
        def destroy_widget_3(widget, boxon1, boxon2, boxon3, boxon4, boxon5, boxon6, boxon7, boxon8, figx, figy, title_name, titlesize, ticksize, labelx, labely,\
        labelsize, vmin, vmax, cmap_to_use):

            L = len(arr)
            if boxon1 % 2 == 0:
                cmap_to_use = "RdBu_r"
                
            if boxon2 % 2 == 0:
                figx = dim[1]/50
                figy = dim[0]/50
            else:
                figx = int(figx)
                figy = int(figy)
            
            if boxon4 % 2 == 0:
                titlesize = 14
            else:
                titlesize = int(titlesize)

            if boxon5 % 2 == 0:
                ticksize = 14
            else:
                ticksize = int(ticksize)

            if boxon7 % 2 == 0:
                labelsize = 14
            else:
                labelsize = int(labelsize)
            
            if boxon8 % 2 == 0:
                vmin = -5
                vmax = 5
            else:
                vmin = float(vmin)
                vmax = float(vmax)
        
            fig_anim = plt.figure(figsize=(figx, figy))
            if contr == 'X':
                ax_anim = plt.axes(xlim=(MinX, MaxX), ylim=(MinZ, MaxZ))
                nanarray = np.empty((dim[1], dim[0]))
                nanarray[:] = np.nan
                im = plt.imshow(nanarray, origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinZ, MaxZ])
                if boxon3 % 2 == 0:
                    ax_anim.set_title("Proxy map", fontsize = titlesize)
                else: 
                    ax_anim.set_title(title_name, fontsize = titlesize)
                if boxon6 % 2 == 0:
                    ax_anim.set_ylabel("y", fontsize = labelsize)
                    ax_anim.set_xlabel("x", fontsize = labelsize)
                else: 
                    ax_anim.set_ylabel(labely, fontsize = labelsize)
                    ax_anim.set_xlabel(labelx, fontsize = labelsize) 
                ax_anim.tick_params(labelsize = ticksize)
            elif contr == 'Y': 
                ax_anim = plt.axes(xlim=(MinY, MaxY), ylim=(MinZ, MaxZ))
                nanarray = np.empty((dim[1], dim[0]))
                nanarray[:] = np.nan
                im = plt.imshow(nanarray, origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinY, MaxY, MinZ, MaxZ])
                if boxon6 % 2 == 0:
                    ax_anim.set_ylabel("y", fontsize = labelsize)
                    ax_anim.set_xlabel("x", fontsize = labelsize)
                else: 
                    ax_anim.set_ylabel(labely, fontsize = labelsize)
                    ax_anim.set_xlabel(labelx, fontsize = labelsize)
                if boxon3 % 2 == 0:
                    ax_anim.set_title("Proxy map", fontsize = titlesize)
                else: 
                    ax_anim.set_title(title_name, fontsize = titlesize) 
                ax_anim.tick_params(labelsize = ticksize)
            elif contr == 'Z': 
                ax_anim = plt.axes(xlim=(MinX, MaxX), ylim=(MinY, MaxY))
                nanarray = np.empty((dim[1], dim[0]))
                nanarray[:] = np.nan
                im = plt.imshow(nanarray, origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinY, MaxY])
                if boxon6 % 2 == 0:
                    ax_anim.set_ylabel("y", fontsize = labelsize)
                    ax_anim.set_xlabel("x", fontsize = labelsize)
                else: 
                    ax_anim.set_ylabel(labely, fontsize = labelsize)
                    ax_anim.set_xlabel(labelx, fontsize = labelsize)
                if boxon3 % 2 == 0:
                    ax_anim.set_title("Proxy map", fontsize = titlesize)
                else: 
                    ax_anim.set_title(title_name, fontsize = titlesize) 
                ax_anim.tick_params(labelsize = ticksize)
                
            def init():
                im.set_data(nanarray)
                #plt.axis('off')
                return [im]
        
            def animate(j):
                im.set_array(arr[j])
                #plt.axis('off')
                return [im]
        
            anim = FuncAnimation(fig_anim, animate, init_func=init,
                                    frames=L, interval=120, blit=True)
        
            anim.save(filename+'.gif', writer='imagemagick')
            
            plt.close()
            
            save_lbl = Label(ws, text = 'Saved!', foreground = 'green')    
            save_lbl.place(x = 420, y = 530)
            
            ws.after(2000, destroy_widget, save_lbl)
            plotws.destroy()
            
    def Calc_grd_twist(lower, upper, twist, twistpol, c):
        global Grd
        lower = int(lower)
        upper = int(upper)
        Grd = np.zeros(np.shape(twist))
        N = len(twist)
        
        if twistpol == "1":
            for j in range(N):
                Grd[j] = dip.MultiScaleMorphologicalGradient(twist[j], lowerSize = lower, upperSize = upper)+twist1[j]
            Grd[np.array(twist) < 0.0] = 0
        elif twistpol == "-1":
            for j in range(N):
                Grd[j] = dip.MultiScaleMorphologicalGradient(twist[j], lowerSize = lower, upperSize = upper)-twist1[j]
            Grd[np.array(twist) > 0.0] = 0
        elif twistpol == "0":
            for j in range(N):
                Grd[j] = dip.MultiScaleMorphologicalGradient(twist[j], lowerSize = lower, upperSize = upper)+twist1[j]   
           
        #calc_lbl = Label(ws, text='Calculation done!', foreground='green')
        #calc_lbl.place(x = 640, y = 70)
        
        #ws.after(2000, destroy_widget, calc_lbl)    
        
        if c == 0:
            global vis_btn2
            vis_btn2 = Button(ws, text='Visualize Grad+Proxy', command = lambda:Vis_GrdTwist(contr, Grd, spin_val.get(), canvas, c6))
            vis_btn2.place(in_ = Grd_button, y = 0, relx = spacing) 
            
            Thr_lbl = Label(ws, text = 'Threshold:')
            Thr_lbl.place(x = col2_px, y = 100)
            global Enter_thr
            Enter_thr = Entry(ws, textvariable = Thr, width = wi)
            Enter_thr.place(in_ = Thr_lbl, y = 0, relx = spacing)
            global Thresh
            Thresh = Button(ws, text = 'Apply Threshold', command = lambda:Thresholding(Grd, Thr.get(), contr2, c7))
            Thresh.place(in_ = Enter_thr, y = 0, relx = spacing)
        else:
            vis_btn2.destroy()
            vis_btn2 = Button(ws, text='Visualize Grad+Proxy', command = lambda:Vis_GrdTwist(contr, Grd, spin_val.get(), canvas, c6))
            vis_btn2.place(in_ = Grd_button, y = 0, relx = spacing)     
            Thresh.destroy()
            Thresh = Button(ws, text = 'Apply Threshold', command = lambda:Thresholding(Grd, Thr.get(), contr2, c7))
            Thresh.place(in_ = Enter_thr, y = 0, relx = spacing)            
        
        global c5
        c5 = 1
        
        global contr2
        contr2 = 0       
        
    def Vis_GrdTwist(contr, Grd, num, canvas, c):
        plt.close()
        canvas.get_tk_widget().destroy()
        num = int(num)
        fig2 = plt.figure(figsize = (4.5,3.5))
        plot2 = fig2.add_subplot(111)
        if contr == 'X': 
            plot2.imshow(Grd[num], origin = "lower", cmap = "RdBu_r", vmin = -5, vmax = 5, extent = [MinX, MaxX, MinZ, MaxZ])
            plot2.set_title("Gradtwist_map no. "+str(num), fontsize = 9)
            plot2.set_ylabel("y", fontsize = 9)
            plot2.set_xlabel("x", fontsize = 9)
            plot2.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Y': 
            plot2.imshow(Grd[num], origin = "lower", cmap = "RdBu_r", vmin = -5, vmax = 5, extent = [MinY, MaxY, MinZ, MaxZ])
            plot2.set_title("Gradtwist_map no. "+str(num), fontsize = 9)
            plot2.set_ylabel("y", fontsize = 9)
            plot2.set_xlabel("x", fontsize = 9)
            plot2.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Z': 
            plot2.imshow(Grd[num], origin = "lower", cmap = "RdBu_r", vmin = -5, vmax = 5, extent = [MinX, MaxX, MinY, MaxY])
            plot2.set_title("Gradtwist_map no. "+str(num), fontsize = 9)
            plot2.set_ylabel("y", fontsize = 9)
            plot2.set_xlabel("x", fontsize = 9)
            plot2.tick_params(axis='both', which='major', labelsize=7)
            
        canvas = FigureCanvasTkAgg(fig2, master=ws)
        canvas.draw()
        canvas.get_tk_widget().place(x = 20, y = 100)
        Plotstr = 'GrdTw'
                
        if c == 0:
            base_name2 = Text(ws, height = 1, width = 30)
            base_name2.place(x = basecol1_px, y = 560)
            save_frames_grdtwist = Button(ws, text = 'Save Frames MM', command = lambda:savefunc(Plotstr, contr, Grd, base_name2.get('1.0','end-1c')))
            save_frames_grdtwist.place(x = 20, y = 560)
            
            base_name_grd = Text(ws, height = 1, width = 30)
            base_name_grd.place(x = basecol1_px, y = 590)
            save_anim2 = Button(ws, text = 'Save MM Animation', command = lambda:saveanim_grd(Grd, base_name_grd.get('1.0','end-1c'), contr))
            save_anim2.place(x = 20, y = 590)
            
        global c6
        c6 = 1
    
    def saveanim_grd(arr, filename, contr):
        plotws = tki.Toplevel(ws)
        plotws.title("Plot Specifications")
        plotws.geometry(str(horsz_plotws)+'x640')
        plotws.grab_set()
        
        default_font = tki.font.nametofont("TkDefaultFont")
        default_font2 = tki.font.nametofont("TkTextFont")
        default_font3 = tki.font.nametofont("TkFixedFont")
        default_font.configure(size=9)
        default_font2.configure(size=9)
        default_font3.configure(size=9)
        
        #Set colormap:
        global cmap_to_use
        cmap_to_use = "RdBu_r"
        
        def set_colormap(boxon):
            if boxon % 2 == 1:
                listbox3.config(state = "normal")
            else:
                listbox3.config(state = "disabled")

        def_colormap = tki.IntVar(value = 0)
        check_default_colormap = Checkbutton(plotws, text = "Customize", variable = def_colormap, command = lambda:set_colormap(def_colormap.get()))        
        check_default_colormap.place(x = 10, y = 90)
        
        #cmap_to_use = tki.StringVar(value = '')
        listbox3 = tki.Listbox(plotws, height=7, width = 25, selectmode=tki.SINGLE, exportselection=False)
        
        for j in range(len(cmaps)):
            listbox3.insert(tki.END, cmaps[j])
        listbox3.place(x = 120, y = 35)
        listbox3.config(state = "disabled")
        
        colormap_lbl = Label(plotws, text = 'Choose Colormap:')    
        colormap_lbl.place(x = 120, y = 10)   
        
        def color_selected(event):
            global cmap_to_use
            cmap_to_use = cmaps[int(listbox3.curselection()[0])]
    
        listbox3.bind('<<ListboxSelect>>', color_selected)
        
        #Set figure size:
        def_figsize = tki.IntVar(value = 0)
        check_default_figsize = Checkbutton(plotws, text = "Customize", variable = def_figsize, command = lambda:set_figsize(def_figsize.get()))        
        check_default_figsize.place(x = 10, y = 180)   
        
        Label(plotws, text='Choose Figure Size:').place(x = 120, y = 180)
        
        figure_x = tki.StringVar(value = "12")
        figure_y = tki.StringVar(value = "12")
        
        xfig = Label(plotws, text = 'x =')
        xfig.place(x = 120, y = 210)
        Enter_figx = Entry(plotws, textvariable = figure_x, width = 4)
        Enter_figx.place(in_ = xfig, y = 0, relx = spacing)
        yfig = Label(plotws, text = 'y =')
        yfig.place(in_ = Enter_figx, y = 0, relx = spacing)
        Enter_figy = Entry(plotws, textvariable = figure_y, width = 4)
        Enter_figy.place(in_ = yfig, y = 0, relx = spacing)
        
        Enter_figx.config(state = "disabled")
        Enter_figy.config(state = "disabled")
        
        def set_figsize(boxon):
            if boxon % 2 == 1:
                Enter_figx.config(state = "normal")
                Enter_figy.config(state = "normal")
            else:
                Enter_figx.config(state = "disabled")
                Enter_figy.config(state = "disabled")  
        
        #Set title:
        def_title = tki.IntVar(value = 0)
        check_default_title = Checkbutton(plotws, text = "Customize", variable = def_title, command = lambda:set_plottitle(def_title.get()))        
        check_default_title.place(x = 10, y = 240)   
        
        Label(plotws, text='Choose Figure Title:').place(x = 120, y = 240)
        
        figure_title = tki.StringVar(value = "")
        text_title = Text(plotws, height = 1, width = 20)
        text_title.place(x = 120, y = 270)        
        text_title.config(state = "disabled")
        
        def set_plottitle(boxon):
            if boxon % 2 == 1:
                text_title.config(state = "normal")
            else:
                text_title.config(state = "disabled")
        
        #Set titlesize 
        def_titlesize = tki.IntVar(value = 0)
        check_default_titlesize = Checkbutton(plotws, text = "Customize", variable = def_titlesize, command = lambda:set_titlesize(def_titlesize.get()))        
        check_default_titlesize.place(x = 10, y = 300)   
        
        Label(plotws, text='Choose Title Size:').place(x = 120, y = 300)
        
        titlesize = tki.StringVar(value = "14")
        Enter_titlesize = Entry(plotws, textvariable = titlesize, width = 6)
        Enter_titlesize.place(x = 120, y = 330)       
        Enter_titlesize.config(state = "disabled")
        
        def set_titlesize(boxon):
            if boxon % 2 == 1:
                Enter_titlesize.config(state = "normal")
            else:
                Enter_titlesize.config(state = "disabled")
        
        #Set ticksize 
        def_ticksize = tki.IntVar(value = 0)
        check_default_ticksize = Checkbutton(plotws, text = "Customize", variable = def_ticksize, command = lambda:set_ticksize(def_ticksize.get()))        
        check_default_ticksize.place(x = 10, y = 360)   
        
        Label(plotws, text='Choose Ticksize:').place(x = 120, y = 360)
        
        ticksize = tki.StringVar(value = "14")
        Enter_ticksize = Entry(plotws, textvariable = ticksize, width = 6)
        Enter_ticksize.place(x = 120, y = 390)       
        Enter_ticksize.config(state = "disabled")
        
        def set_ticksize(boxon):
            if boxon % 2 == 1:
                Enter_ticksize.config(state = "normal")
            else:
                Enter_ticksize.config(state = "disabled")

        #Set label
        def_label = tki.IntVar(value = 0)
        check_default_label = Checkbutton(plotws, text = "Customize", variable = def_label, command = lambda:set_label(def_label.get()))        
        check_default_label.place(x = 10, y = 420)   
        
        Label(plotws, text='Choose Labels:').place(x = 120, y = 420)
        
        label_x = tki.StringVar(value = "")
        label_y = tki.StringVar(value = "")
        
        axx_lbl = Label(plotws, text = 'x =')
        axx_lbl.place(x = 120, y = 450)
        Enter_labelx = Entry(plotws, textvariable = label_x, width = 6)
        Enter_labelx.place(in_ = axx_lbl, y = 0, relx = spacing)
        axy_lbl = Label(plotws, text = 'y =')
        axy_lbl.place(in_ = Enter_labelx, y = 0, relx = spacing)
        Enter_labely = Entry(plotws, textvariable = label_y, width = 6)
        Enter_labely.place(in_ = axy_lbl, y = 0, relx = spacing)
        
        Enter_labelx.config(state = "disabled")
        Enter_labely.config(state = "disabled")
        
        def set_label(boxon):
            if boxon % 2 == 1:
                Enter_labelx.config(state = "normal")
                Enter_labely.config(state = "normal")
            else:
                Enter_labelx.config(state = "disabled")
                Enter_labely.config(state = "disabled")
                
        #Set labelsize      
        def_labelsize = tki.IntVar(value = 0)
        check_default_labelsize = Checkbutton(plotws, text = "Customize", variable = def_labelsize, command = lambda:set_labelsize(def_labelsize.get()))        
        check_default_labelsize.place(x = 10, y = 480)   
        
        Label(plotws, text='Choose Labelsize:').place(x = 120, y = 480)
        
        labelsize = tki.StringVar(value = "14")
        Enter_labelsize = Entry(plotws, textvariable = labelsize, width = 6)
        Enter_labelsize.place(x = 120, y = 510)       
        Enter_labelsize.config(state = "disabled")
        
        def set_labelsize(boxon):
            if boxon % 2 == 1:
                Enter_labelsize.config(state = "normal")
            else:
                Enter_labelsize.config(state = "disabled")
        
        #Set vmin/vmax
        def_minmax = tki.IntVar(value = 0)
        check_default_minmax = Checkbutton(plotws, text = "Customize", variable = def_minmax, command = lambda:set_minmax(def_minmax.get()))        
        check_default_minmax.place(x = 10, y = 540)   
        
        Label(plotws, text='Choose Colormap Limits:').place(x = 120, y = 540)
        
        vmin = tki.IntVar(value = -5)
        vmax = tki.IntVar(value = 5)
      
        vmin_lbl = Label(plotws, text = 'vmin =')
        vmin_lbl.place(x = 120, y = 570)
        Enter_vmin = Entry(plotws, textvariable = vmin, width = 4)
        Enter_vmin.place(in_ = vmin_lbl, y = 0, relx = spacing)
        vmax_lbl = Label(plotws, text = 'vmax =')
        vmax_lbl.place(in_ = Enter_vmin, y = 0, relx = spacing)
        Enter_vmax = Entry(plotws, textvariable = vmax, width = 4)
        Enter_vmax.place(in_ = vmax_lbl, y = 0, relx = spacing)
               
        Enter_vmin.config(state = "disabled")
        Enter_vmax.config(state = "disabled")
        
        def set_minmax(boxon):
            if boxon % 2 == 1:
                Enter_vmin.config(state = "normal")
                Enter_vmax.config(state = "normal")
            else:
                Enter_vmin.config(state = "disabled")
                Enter_vmax.config(state = "disabled")
        
        conf_btn3 = Button(plotws, text='Confirm', command = lambda:destroy_widget_4(plotws, def_colormap.get(), def_figsize.get(), def_title.get(), \
        def_titlesize.get(), def_ticksize.get(), def_label.get(), def_labelsize.get(), def_minmax.get(), figure_x.get(), figure_y.get(), text_title.get('1.0','end-1c'), titlesize.get(), \
        ticksize.get(), label_x.get(), label_y.get(), labelsize.get(), vmin.get(), vmax.get(), cmap_to_use))
        
        conf_btn3.place(x = 120, y = 605)
    
    
        def destroy_widget_4(widget, boxon1, boxon2, boxon3, boxon4, boxon5, boxon6, boxon7, boxon8, figx, figy, title_name, titlesize, ticksize, labelx, labely,\
        labelsize, vmin, vmax, cmap_to_use):

            L = len(arr)
            if boxon1 % 2 == 0:
                cmap_to_use = "RdBu_r"
                
            if boxon2 % 2 == 0:
                figx = dim[1]/50
                figy = dim[0]/50
            else:
                figx = int(figx)
                figy = int(figy)
            
            if boxon4 % 2 == 0:
                titlesize = 14
            else:
                titlesize = int(titlesize)

            if boxon5 % 2 == 0:
                ticksize = 14
            else:
                ticksize = int(ticksize)

            if boxon7 % 2 == 0:
                labelsize = 14
            else:
                labelsize = int(labelsize)
            
            if boxon8 % 2 == 0:
                vmin = 0
                vmax = 2
            else:
                vmin = float(vmin)
                vmax = float(vmax)
        
            fig_anim = plt.figure(figsize=(figx, figy))
            if contr == 'X':
                ax_anim = plt.axes(xlim=(MinX, MaxX), ylim=(MinZ, MaxZ))
                nanarray = np.empty((dim[1], dim[0]))
                nanarray[:] = np.nan
                im = plt.imshow(nanarray, origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinZ, MaxZ])
                if boxon3 % 2 == 0:
                    ax_anim.set_title("Proxy map", fontsize = titlesize)
                else: 
                    ax_anim.set_title(title_name, fontsize = titlesize)
                if boxon6 % 2 == 0:
                    ax_anim.set_ylabel("y", fontsize = labelsize)
                    ax_anim.set_xlabel("x", fontsize = labelsize)
                else: 
                    ax_anim.set_ylabel(labely, fontsize = labelsize)
                    ax_anim.set_xlabel(labelx, fontsize = labelsize) 
                ax_anim.tick_params(labelsize = ticksize)
            elif contr == 'Y': 
                ax_anim = plt.axes(xlim=(MinY, MaxY), ylim=(MinZ, MaxZ))
                nanarray = np.empty((dim[1], dim[0]))
                nanarray[:] = np.nan
                im = plt.imshow(nanarray, origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinY, MaxY, MinZ, MaxZ])
                if boxon6 % 2 == 0:
                    ax_anim.set_ylabel("y", fontsize = labelsize)
                    ax_anim.set_xlabel("x", fontsize = labelsize)
                else: 
                    ax_anim.set_ylabel(labely, fontsize = labelsize)
                    ax_anim.set_xlabel(labelx, fontsize = labelsize)
                if boxon3 % 2 == 0:
                    ax_anim.set_title("Proxy map", fontsize = titlesize)
                else: 
                    ax_anim.set_title(title_name, fontsize = titlesize) 
                ax_anim.tick_params(labelsize = ticksize)
            elif contr == 'Z': 
                ax_anim = plt.axes(xlim=(MinX, MaxX), ylim=(MinY, MaxY))
                nanarray = np.empty((dim[1], dim[0]))
                nanarray[:] = np.nan
                im = plt.imshow(nanarray, origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinY, MaxY])
                if boxon6 % 2 == 0:
                    ax_anim.set_ylabel("y", fontsize = labelsize)
                    ax_anim.set_xlabel("x", fontsize = labelsize)
                else: 
                    ax_anim.set_ylabel(labely, fontsize = labelsize)
                    ax_anim.set_xlabel(labelx, fontsize = labelsize)
                if boxon3 % 2 == 0:
                    ax_anim.set_title("Proxy map", fontsize = titlesize)
                else: 
                    ax_anim.set_title(title_name, fontsize = titlesize) 
                ax_anim.tick_params(labelsize = ticksize)
                
            def init():
                im.set_data(nanarray)
                #plt.axis('off')
                return [im]
        
            def animate(j):
                im.set_array(arr[j])
                #plt.axis('off')
                return [im]
        
            anim = FuncAnimation(fig_anim, animate, init_func=init,
                                    frames=L, interval=120, blit=True)
        
            anim.save(filename+'.gif', writer='imagemagick')
            
            plt.close()
        
            save_lbl = Label(ws, text = 'Saved!', foreground = 'green')    
            save_lbl.place(x = 420, y = 590)
        
            ws.after(2000, destroy_widget, save_lbl)
            plotws.destroy()
            
    def Thresholding(arr, Thr, contr2, c):
        global GrdTw_Thr
        GrdTw_Thr = np.zeros(np.shape(arr))
        Thr = float(Thr)
        GrdTw_Thr[arr > Thr] = 1
        
        if contr2 == 0:
            pass
        elif contr2 == 1:
            calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
            calc_lbl.place(x = 720, y = 370)
            ws.after(2000, destroy_widget, calc_lbl) 
        elif contr2 == 2:
            calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
            calc_lbl.place(x = 720, y = 400)   
            ws.after(2000, destroy_widget, calc_lbl)    

        if c == 0:
            vis3_btn = Button(ws, text='Visualize Mask', command = lambda:Vis_Thresholding(contr, GrdTw_Thr, spin_val.get(), Thr, canvas, c8))
            vis3_btn.place(x = col2_px, y = 130)      
        #else:
            #spin3.destroy()
            #spin3 = Spinbox(ws, from_ = 0, to = len(arr)-1, textvariable = spin3_val, wrap = True)
            #spin3.place(x = 580, y = 160)
    
        contr2 = 0
        global contr3
        contr3 = 0
        
    def Vis_Thresholding(contr, arr, num, Thr, canvas, c):
        plt.close()
        canvas.get_tk_widget().destroy()
        num = int(num)
        fig3 = plt.figure(figsize = (4.5,3.5))
        plot3 = fig3.add_subplot(111)
        if contr == 'X': 
            plot3.imshow(arr[num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinZ, MaxZ])
            plot3.set_title("Gradtwist Threshold "+str(Thr)+" no. "+str(num), fontsize = 8)
            plot3.set_ylabel("y", fontsize = 9)
            plot3.set_xlabel("x", fontsize = 9)
            plot3.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Y': 
            plot3.imshow(arr[num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinY, MaxY, MinZ, MaxZ])
            plot3.set_title("Gradtwist Threshold "+str(Thr)+" no. "+str(num), fontsize = 8)
            plot3.set_ylabel("y", fontsize = 9)
            plot3.set_xlabel("x", fontsize = 9)
            plot3.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Z': 
            plot3.imshow(arr[num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinY, MaxY])
            plot3.set_title("Gradtwist Threshold "+str(Thr)+" no. "+str(num), fontsize = 8)
            plot3.set_ylabel("y", fontsize = 9)
            plot3.set_xlabel("x", fontsize = 9)
            plot3.tick_params(axis='both', which='major', labelsize=7)  
            
        canvas = FigureCanvasTkAgg(fig3, master=ws)
        canvas.draw()
        canvas.get_tk_widget().place(x = 20, y = 100)
        #Plotstr = 'GrdTw_Thr'
        
        if c == 0:
            Style().configure("gray.TSeparator", background="gray")
            Sep = Separator(ws, takefocus=0, orient='horizontal', style = "gray.TSeparator")
            Sep.place(x=col2_px, y=158, relwidth = 0.22)
            Label(ws, text= "Pre-Processing (optional)").place(x = col2_px, y = 160)
            
            global Undo_btn
            op_lbl = Label(ws, text = 'Opening Size')
            op_lbl.place(x = col2_px, y = 190)
            Enter_ope = Entry(ws, textvariable = ope, width = wi)
            Enter_ope.place(in_ = op_lbl, y = 0, relx = spacing)
            
            opspin_lbl = Label(ws, text = 'Frame no.:')
            opspin_lbl.place(x = col2_px, y = 220) 
            global spin4
            spin4 = Spinbox(ws, from_ = 0, to = len(arr)-1, textvariable = spin4_val, wrap = True, width = wi)
            spin4.place(in_ = opspin_lbl, y = 0, relx = spacing)
            
            subim_lbl = Label(ws, text = 'Sub-image')
            subim_lbl.place(x = col2_px, y = 250)
            xlbl = Label(ws, text = 'x =')
            xlbl.place(in_ = subim_lbl, y = 0, relx = spacing)
            Enter_opeX1 = Entry(ws, textvariable = x1_in, width = wi)
            Enter_opeX1.place(in_ = xlbl, y = 0, relx = spacing)
            to1 = Label(ws, text = 'to')
            to1.place(in_ = Enter_opeX1, y = 0, relx = spacing)
            Enter_opeX2 = Entry(ws, textvariable = x2_in, width = wi)
            Enter_opeX2.place(in_ = to1, y = 0, relx = spacing)
            
            ylbl = Label(ws, text = 'y =')
            ylbl.place(in_ = subim_lbl, y = 30, relx = spacing)
            Enter_opeY1 = Entry(ws, textvariable = y1_in, width = wi)
            Enter_opeY1.place(in_ = ylbl, y = 0, relx = spacing)
            to2 = Label(ws, text = 'to')
            to2.place(in_ = Enter_opeY1, y = 0, relx = spacing)
            Enter_opeY2 = Entry(ws, textvariable = y2_in, width = wi)
            Enter_opeY2.place(in_ = to2, y = 0, relx = spacing)
            
            openall_btn = Button(ws, text = 'Opening All Frames', command = lambda:OpeningAll(GrdTw_Thr, ope.get(), x1_in.get(), x2_in.get(), y1_in.get(), y2_in.get(), c11))
            openall_btn.place(x = col2_px, y = 340)
            
            open_btn = Button(ws, text = 'Apply Opening', command = lambda:OpeningStep(GrdTw_Thr, ope.get(), spin4_val.get(), x1_in.get(), x2_in.get(), y1_in.get(), y2_in.get(), c10))
            open_btn.place(x = col2_px, y = 310)
            
            subthr_lbl = Label(ws, text = 'Sub-image Threshold:')
            subthr_lbl.place(x = col2_px, y = 370)
            Enter_thr2 = Entry(ws, textvariable = Thr2, width = wi)
            Enter_thr2.place(in_ = subthr_lbl, y = 0, relx = spacing)
            Thresh2 = Button(ws, text = 'Apply Threshold', command = lambda:Thresholding2(Grd, GrdTw_Thr, spin4_val.get(), Thr2.get(), x1_in.get(), x2_in.get(), y1_in.get(), y2_in.get(), contr2, c9))
            Thresh2.place(x = col2_px, y = 400)
            
            Sep2 = Separator(ws, takefocus=0, orient='horizontal', style = "gray.TSeparator")
            Sep2.place(x=col2_px, y=457, relwidth = 0.22)
            
            init_track_btn = Button(ws, text = 'Initialize Tracking', command = lambda:init_tracking(GrdTw_Thr, spin5_val.get(), c12))
            init_track_btn.place(x = col2_px, y = 490)
            
            init_lbl1 = Label(ws, text = 'Start tracking from frame: ')
            init_lbl1.place(x = col2_px, y = 460)
            global spin5
            spin5 = Spinbox(ws, from_ = 0, to = len(arr)-1, textvariable = spin5_val, wrap = True, width = wi)
            spin5.place(in_ = init_lbl1, y = 0, relx = spacing)            
        else:
            spin4.destroy()
            spin5.destroy()

            spin4 = Spinbox(ws, from_ = 0, to = len(arr)-1, textvariable = spin4_val, wrap = True, width = wi)
            spin4.place(in_ = opspin_lbl, y = 0, relx = spacing)         
            spin5 = Spinbox(ws, from_ = 0, to = len(arr)-1, textvariable = spin5_val, wrap = True, width = wi)
            spin5.place(in_ = init_lbl1, y = 0, relx = spacing)    
            
    def Thresholding2(arr, arr2, num, Thr, x1_in, x2_in, y1_in, y2_in, contr2, c):
        #global undo_str
        #undo_str = 'Thresh'
        
        global arr_before
        arr_before = arr2.copy()
        
        num = int(num)
        Thr = float(Thr)
        x1_in = float(x1_in)
        x2_in = float(x2_in)
        y1_in = float(y1_in)
        y2_in = float(y2_in)
        
        if (x1_in >= x2_in) or (y1_in >= y2_in):
            Corr = arr.copy()
            Corr_op = np.zeros(np.shape(Corr))
            Corr_op[num][Corr[num] > Thr] = 1
            GrdTw_Thr[num] = Corr_op[num].copy()
        else:
            if contr == 'X': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Y': 
                x1_conv = int(np.floor((x1_in-MinY)/dy))
                x2_conv = int(np.floor((x2_in-MinY)/dy))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Z': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinY)/dy))
                y2_conv = int(np.floor((y2_in-MinY)/dy))
                
            Corr = arr[num, y1_conv:y2_conv, x1_conv:x2_conv].copy()
            Corr_op = np.zeros(np.shape(Corr))
            Corr_op[Corr > Thr] = 1
            GrdTw_Thr[num, y1_conv:y2_conv, x1_conv:x2_conv] = Corr_op
    
        calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        calc_lbl.place(x = 630, y = 400)        
        ws.after(2000, destroy_widget, calc_lbl)
        
        contr2 = 1
        
        if c == 0:
            global Undo_btn
            try:
                Undo_btn.destroy()
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:UndoOpen(arr_before, Undo_btn))
                Undo_btn.place(x = 500, y = 430)
            except:
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:UndoOpen(arr_before, Undo_btn))
                Undo_btn.place(x = 500, y = 430)
        
        Undo_btn.config(state = "normal")
        
        global c9
        c9 = 1

    def OpeningStep(arr, ope_size, num, x1_in, x2_in, y1_in, y2_in, c):
        #global undo_str
        #undo_str = 'Open'
        
        global arr_before
        arr_before = GrdTw_Thr.copy()
        
        num = int(num)
        ope_size = float(ope_size)
        x1_in = float(x1_in)
        x2_in = float(x2_in)
        y1_in = float(y1_in)
        y2_in = float(y2_in)
        
        if (x1_in >= x2_in) or (y1_in >= y2_in):
            arr[num] = dip.Opening(arr[num], ope_size)
        else:
            if contr == 'X': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Y': 
                x1_conv = int(np.floor((x1_in-MinY)/dy))
                x2_conv = int(np.floor((x2_in-MinY)/dy))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Z': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinY)/dy))
                y2_conv = int(np.floor((y2_in-MinY)/dy))
                
            Corr = np.zeros(np.shape(arr[num, y1_conv:y2_conv, x1_conv:x2_conv]))
            Corr[arr[num, y1_conv:y2_conv, x1_conv:x2_conv] > 0.8] = 1
            Corr_op = dip.Opening(Corr, ope_size)
            arr[num, y1_conv:y2_conv, x1_conv:x2_conv] = Corr_op
    
        calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        calc_lbl.place(x = 630, y = 310)
        
        ws.after(2000, destroy_widget, calc_lbl)
        
        contr2 = 1
        if c == 0:
            global Undo_btn
            try:
                Undo_btn.destroy()
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:UndoOpen(arr_before, Undo_btn))
                Undo_btn.place(x = 500, y = 430)
            except:
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:UndoOpen(arr_before, Undo_btn))
                Undo_btn.place(x = 500, y = 430)
        
        Undo_btn.config(state = "normal")
        
        global c10
        c10 = 1
    
    def UndoOpen(arr_2, Undo_btn):
        global GrdTw_Thr
        GrdTw_Thr = arr_2.copy()
        
        Undo_btn.config(state = "disabled")
        
        #if undo_str == 'Open':
        #    calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        #    calc_lbl.place(x = 730, y = 310)
        #elif undo_str == 'OpenAll':
        #    calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        #    calc_lbl.place(x = 730, y = 340)
        #elif undo_str == "Thresh":
        #    calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        #    calc_lbl.place(x = 730, y = 400)        
        
        calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        calc_lbl.place(x = 630, y = 430)
        ws.after(2000, destroy_widget, calc_lbl)

    
    def OpeningAll(arr, ope_size, x1_in, x2_in, y1_in, y2_in, c):
        #global undo_str
        #undo_str = 'OpenAll'
        
        global arr_before2
        arr_before2 = arr.copy()
        
        ope_size = float(ope_size)
        x1_in = float(x1_in)
        x2_in = float(x2_in)
        y1_in = float(y1_in)
        y2_in = float(y2_in)
        
        if (x1_in >= x2_in) or (y1_in >= y2_in):
            for j in range(len(arr)):
                arr[j] = dip.Opening(arr[j], ope_size)
        else:
            if contr == 'X': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Y': 
                x1_conv = int(np.floor((x1_in-MinY)/dy))
                x2_conv = int(np.floor((x2_in-MinY)/dy))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Z': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinY)/dy))
                y2_conv = int(np.floor((y2_in-MinY)/dy))
                
            for j in range(len(arr)):
                Corr = np.zeros(np.shape(arr[j, y1_conv:y2_conv, x1_conv:x2_conv]))
                Corr[arr[j, y1_conv:y2_conv, x1_conv:x2_conv] > 0.8] = 1
                Corr_op = dip.Opening(Corr, ope_size)
                arr[j, y1_conv:y2_conv, x1_conv:x2_conv] = Corr_op
    
        calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        calc_lbl.place(x = 630, y = 340)
    
        ws.after(2000, destroy_widget, calc_lbl)   
        
        contr2 = 2
        
        if c == 0:
            global Undo_btn
            try:
                Undo_btn.destroy()
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:UndoOpen(arr_before, Undo_btn))
                Undo_btn.place(x = 500, y = 430)
            except:
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:UndoOpen(arr_before, Undo_btn))
                Undo_btn.place(x = 500, y = 430)
        
        Undo_btn.config(state = "normal")
        
        global c11
        c11 = 1
        
    def init_tracking(arr, num, c):
        arr[:,0,0] = 1
        arr[:,-1,0] = 1
        arr[:,0,-1] = 1
        arr[:,-1,-1] = 1
        
        #track backwards in time from this frame on (N-1 = last)
        num = int(num)
        
        labels0, num0 = measure.label(arr[num,:,:], connectivity = 1, return_num = True)
        props0 = measure.regionprops(labels0)
        l0 = len(props0)
        
        global C0, C1, C2, C3
        
        #calculate size of extracted areas
        areas0 = np.zeros(l0)
        for k in range(0,l0):
            areas0[k] = props0[k]["area"]
        
        #calculate index of largest area and track it as feature 0, then do the same after removing area 0, etc.
        index_area0 = np.argmax(areas0)
        C0 = (props0[index_area0]['coords'])
        
        areas1 = areas0.copy()
        areas1[index_area0] = 0
        index_area1 = np.argmax(areas1)
        C1 = (props0[index_area1]['coords'])
        
        areas2 = areas1.copy()
        areas2[index_area1] = 0
        index_area2 = np.argmax(areas2)
        C2 = (props0[index_area2]['coords'])
        
        areas3 = areas2.copy()
        areas3[index_area2] = 0
        index_area3 = np.argmax(areas3)
        C3 = (props0[index_area3]['coords'])
        
        #set the found twist regions to 1 in new binary arrays
        
        global Tw_region0, Tw_region1, Tw_region2, Tw_region3
        Tw_region0 = np.zeros((num+1, np.shape(arr)[1], np.shape(arr)[2]))
        Tw_region1 = np.zeros((num+1, np.shape(arr)[1], np.shape(arr)[2]))
        Tw_region2 = np.zeros((num+1, np.shape(arr)[1], np.shape(arr)[2]))
        Tw_region3 = np.zeros((num+1, np.shape(arr)[1], np.shape(arr)[2]))
        
        Tw_region0[num,C0[0:-1,0],C0[0:-1,1]] = 1
        Tw_region1[num,C1[0:-1,0],C1[0:-1,1]] = 1
        Tw_region2[num,C2[0:-1,0],C2[0:-1,1]] = 1
        Tw_region3[num,C3[0:-1,0],C3[0:-1,1]] = 1
        
        global LastFrame
        LastFrame = [Tw_region0, Tw_region1, Tw_region2, Tw_region3]
        
        init_lbl = Label(ws, text = 'Tracking initialized!', foreground = 'green')
        init_lbl.place(x = 640, y = 490)
        ws.after(2000, destroy_widget, init_lbl)
        
        #buttons to visualize last frame
        if c == 0:
            shape_lbl = Label(ws, text = 'Choose Shape')
            shape_lbl.place(x = col2_px, y = 520)
            spin6 = Spinbox(ws, from_ = 0, to = 3, textvariable = spin6_val, wrap = True, width = wi)
            spin6.place(in_ = shape_lbl, y = 0, relx = spacing)
            
            vis4_btn = Button(ws, text='Visualize', command = lambda:Vis_Init(contr, LastFrame, spin5_val.get(), spin6_val.get(), canvas, c13))
            vis4_btn.place(in_ = spin6, y = 0, relx = spacing)

        global c12
        c12 = 1
            
        
    def Vis_Init(contr, arr, num, num2, canvas, c):
        plt.close()
        canvas.get_tk_widget().destroy()
        num = int(num) #initialization frame
        num2 = int(num2) #Twist region identifier
        fig4 = plt.figure(figsize = (4.5,3.5))
        plot4 = fig4.add_subplot(111)
        if contr == 'X': 
            plot4.imshow(arr[num2][num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinZ, MaxZ])
            plot4.set_title("Initial Shape "+str(num2), fontsize = 8)
            plot4.set_ylabel("y", fontsize = 9)
            plot4.set_xlabel("x", fontsize = 9)
            plot4.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Y': 
            plot4.imshow(arr[num2][num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinY, MaxY, MinZ, MaxZ])
            plot4.set_title("Initial Shape "+str(num2), fontsize = 8)
            plot4.set_ylabel("y", fontsize = 9)
            plot4.set_xlabel("x", fontsize = 9)
            plot4.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Z': 
            plot4.imshow(arr[num2][num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinY, MaxY])
            plot4.set_title("Initial Shape "+str(num2), fontsize = 8)
            plot4.set_ylabel("y", fontsize = 9)
            plot4.set_xlabel("x", fontsize = 9)
            plot4.tick_params(axis='both', which='major', labelsize=7)
            
        canvas = FigureCanvasTkAgg(fig4, master=ws)
        canvas.draw()
        canvas.get_tk_widget().place(x = 20, y = 100)
        
        if c == 0:
            over_lbl = Label(ws, text = 'Overlap fraction:')
            over_lbl.place(x = col2_px, y = 550)
            Enter_overl = Entry(ws, textvariable = overlap, width = wi)
            Enter_overl.place(in_ = over_lbl, y = 0, relx = spacing)
            Track_btn = Button(ws, text = 'Track', command = lambda:Track(GrdTw_Thr, C0, C1, C2, C3, spin5_val.get(), spin6_val.get(), overlap.get(), contr3, c14))
            Track_btn.place(x = col2_px, y = 580)
            
        global c13
        c13 = 1    
        
    def Track(GrdTw_Thr, C0, C1, C2, C3, num, num2, overlap, contr3, c):
        num = int(num) #initialization frame
        num2 = int(num2) #twist region identifier
        overlap = float(overlap)
        Match = np.ones((4,4)) #overlap matrix
        
        GrdTw_Thr = np.array(GrdTw_Thr)

        GrdTw_Thr[:,0,0] = 1
        GrdTw_Thr[:,-1,0] = 1
        GrdTw_Thr[:,0,-1] = 1
        GrdTw_Thr[:,-1,-1] = 1
        
        #Testmaps for comparison
        Testmap0 = np.zeros(np.shape(Tw_region0[0,:,:]))
        Testmap1 = np.zeros(np.shape(Tw_region0[0,:,:]))
        Testmap2 = np.zeros(np.shape(Tw_region0[0,:,:]))
        Testmap3 = np.zeros(np.shape(Tw_region0[0,:,:]))
        
        for j in range(num, 0, -1):    
            all_labels = measure.label(GrdTw_Thr[j-1,:,:], connectivity = 1, return_num = False)
            props = measure.regionprops(all_labels)
            l1 = len(props)
            
            areas = np.zeros(l1)
            for k in range(0,l1):
                areas[k] = props[k]["area"]
                
            index_area = np.argmax(areas)
            areas[index_area] = 0
            index_area_1 = np.argmax(areas)
            areas[index_area_1] = 0
            index_area_2 = np.argmax(areas)                
            areas[index_area_2] = 0
            index_area_3 = np.argmax(areas)
            
            Testmap0[props[index_area]['coords'][0:-1,0],props[index_area]['coords'][0:-1,1]] = 1
            Testmap1[props[index_area_1]['coords'][0:-1,0],props[index_area_1]['coords'][0:-1,1]] = 1
            Testmap2[props[index_area_2]['coords'][0:-1,0],props[index_area_2]['coords'][0:-1,1]] = 1
            Testmap3[props[index_area_3]['coords'][0:-1,0],props[index_area_3]['coords'][0:-1,1]] = 1
            
            Sum0 = np.add(Testmap0, Tw_region0[j,:,:])
            Sum1 = np.add(Testmap1, Tw_region0[j,:,:])
            Sum2 = np.add(Testmap2, Tw_region0[j,:,:])
            Sum3 = np.add(Testmap3, Tw_region0[j,:,:])
            
            S0 = np.count_nonzero(Sum0 == 2)
            S1 = np.count_nonzero(Sum1 == 2)
            S2 = np.count_nonzero(Sum2 == 2)
            S3 = np.count_nonzero(Sum3 == 2)
            
            Match[0,0] = S0/len(C0)
            Match[1,0] = S1/len(C0)
            Match[2,0] = S2/len(C0)
            Match[3,0] = S3/len(C0)
            
            if Match[0,0] >= overlap:
                C0 = (props[index_area]['coords'])
            elif Match[1,0] >= overlap:
                C0 = (props[index_area_1]['coords'])
            elif Match[2,0] >= overlap:
                C0 = (props[index_area_2]['coords'])
            elif Match[3,0] >= overlap:
                C0 = (props[index_area_3]['coords'])
        
            
            Sum0 = np.add(Testmap0, Tw_region1[j,:,:])
            Sum1 = np.add(Testmap1, Tw_region1[j,:,:])
            Sum2 = np.add(Testmap2, Tw_region1[j,:,:])
            Sum3 = np.add(Testmap3, Tw_region1[j,:,:])
            
            S0 = np.count_nonzero(Sum0 == 2)
            S1 = np.count_nonzero(Sum1 == 2)
            S2 = np.count_nonzero(Sum2 == 2)
            S3 = np.count_nonzero(Sum3 == 2)
            
            Match[0,1] = S0/len(C1)
            Match[1,1] = S1/len(C1)
            Match[2,1] = S2/len(C1)
            Match[3,1] = S3/len(C1)
        
            if Match[0,1] >= overlap:
                C1 = (props[index_area]['coords'])  
            elif Match[1,1] >= overlap:
                C1 = (props[index_area_1]['coords'])   
            elif Match[2,1] >= overlap:
                C1 = (props[index_area_2]['coords'])   
            elif Match[3,1] >= overlap:
                C1 = (props[index_area_3]['coords'])
        
            Sum0 = np.add(Testmap0, Tw_region2[j,:,:])
            Sum1 = np.add(Testmap1, Tw_region2[j,:,:])
            Sum2 = np.add(Testmap2, Tw_region2[j,:,:])
            Sum3 = np.add(Testmap3, Tw_region2[j,:,:])
            
            S0 = np.count_nonzero(Sum0 == 2)
            S1 = np.count_nonzero(Sum1 == 2)
            S2 = np.count_nonzero(Sum2 == 2)
            S3 = np.count_nonzero(Sum3 == 2)
            
            Match[0,2] = S0/len(C2)
            Match[1,2] = S1/len(C2)
            Match[2,2] = S2/len(C2)
            Match[3,2] = S3/len(C2)
        
            if Match[0,2] >= overlap:
                C2 = (props[index_area]['coords'])
            elif Match[1,2] >= overlap:
                C2 = (props[index_area_1]['coords'])    
            elif Match[2,2] >= overlap:
                C2 = (props[index_area_2]['coords'])
            elif Match[3,2] >= overlap:
                C2 = (props[index_area_3]['coords'])
        
            Sum0 = np.add(Testmap0, Tw_region3[j,:,:])
            Sum1 = np.add(Testmap1, Tw_region3[j,:,:])
            Sum2 = np.add(Testmap2, Tw_region3[j,:,:])
            Sum3 = np.add(Testmap3, Tw_region3[j,:,:])
            
            S0 = np.count_nonzero(Sum0 == 2)
            S1 = np.count_nonzero(Sum1 == 2)
            S2 = np.count_nonzero(Sum2 == 2)
            S3 = np.count_nonzero(Sum3 == 2)
            
            Match[0,3] = S0/len(C3)
            Match[1,3] = S1/len(C3)
            Match[2,3] = S2/len(C3)
            Match[3,3] = S3/len(C3)
        
            if Match[0,3] >= overlap:
                C3 = (props[index_area]['coords'])
            elif Match[1,3] >= overlap:
                C3 = (props[index_area_1]['coords'])    
            elif Match[2,3] >= overlap:
                C3 = (props[index_area_2]['coords'])   
            elif Match[3,3] >= overlap:
                C3 = (props[index_area_3]['coords'])
            
            Tw_region0[j-1,C0[0:-1,0],C0[0:-1,1]] = 1
            Tw_region1[j-1,C1[0:-1,0],C1[0:-1,1]] = 1
            Tw_region2[j-1,C2[0:-1,0],C2[0:-1,1]] = 1
            Tw_region3[j-1,C3[0:-1,0],C3[0:-1,1]] = 1
            
            Testmap0 = np.zeros(np.shape(Tw_region0[0,:,:]))
            Testmap1 = np.zeros(np.shape(Tw_region0[0,:,:]))
            Testmap2 = np.zeros(np.shape(Tw_region0[0,:,:]))
            Testmap3 = np.zeros(np.shape(Tw_region0[0,:,:]))
            
        global tracked
        tracked = LastFrame[num2]
        global processed
        processed = tracked.copy()
        
        if contr3 == 0:
            track_lbl = Label(ws, text = 'Tracking completed!', foreground = 'green')
            track_lbl.place(x = 640, y = 580)
            ws.after(2000, destroy_widget, track_lbl)   
        elif contr3 == 1:
            track_lbl = Label(ws, text = 'Done!', foreground = 'green')
            track_lbl.place(x = 1050, y = 160)
            ws.after(2000, destroy_widget, track_lbl)   
        elif contr3 == 2: 
            track_lbl = Label(ws, text = 'Done!', foreground = 'green')
            track_lbl.place(x = 1050, y = 190)
            ws.after(2000, destroy_widget, track_lbl)
        elif contr3 == 3:
            track_lbl = Label(ws, text = 'Done!', foreground = 'green')
            track_lbl.place(x = 1050, y = 220)
            ws.after(2000, destroy_widget, track_lbl)
            
        contr3 = 0
        
        if c == 0:

            vis5_btn = Button(ws, text = 'Visualize Tracked Shape', command = lambda:Vis_track(spin_val.get(), canvas, c15))
            vis5_btn.place(x = col2_px, y = 610)
        
        global c14
        c14 = 1
            
    def Vis_track(num, canvas, c):
        plt.close()
        canvas.get_tk_widget().destroy()
        num = int(num)
        fig5 = plt.figure(figsize = (4.5,3.5))
        plot5 = fig5.add_subplot(111)
        Plotstr = 'track'
        if contr == 'X': 
            plot5.imshow(tracked[num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinZ, MaxZ])
            plot5.set_title("Tracked Shape, Frame "+str(num), fontsize = 8)
            plot5.set_ylabel("y", fontsize = 9)
            plot5.set_xlabel("x", fontsize = 9)
            plot5.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Y': 
            plot5.imshow(tracked[num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinY, MaxY, MinZ, MaxZ])
            plot5.set_title("Tracked Shape, Frame "+str(num), fontsize = 8)
            plot5.set_ylabel("y", fontsize = 9)
            plot5.set_xlabel("x", fontsize = 9)
            plot5.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Z': 
            plot5.imshow(tracked[num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinY, MaxY])
            plot5.set_title("Tracked Shape, Frame "+str(num), fontsize = 8)
            plot5.set_ylabel("y", fontsize = 9)
            plot5.set_xlabel("x", fontsize = 9)
            plot5.tick_params(axis='both', which='major', labelsize=7)
            
        canvas = FigureCanvasTkAgg(fig5, master=ws)
        canvas.draw()
        canvas.get_tk_widget().place(x = 20, y = 100)
        
        #base_name4 = Text(ws, height = 1, width = 30)
        #base_name4.place(x = 180, y = 620)
        #save_frames3 = Button(ws, text = 'Save Tracking Frames', command = lambda:savefunc(Plotstr, contr, tracked, base_name4.get('1.0','end-1c')))
        #save_frames3.place(x = 20, y = 620)
        
        #base_name5 = Text(ws, height = 1, width = 30)
        #base_name5.place(x = 180, y = 650)
        #save_array3 = Button(ws, text = 'Save Arrays', command = lambda:savearr(tracked, base_name5.get('1.0','end-1c')))
        #save_array3.place(x = 20, y = 650)
        
        if c == 0:
            Sep3 = Separator(ws, takefocus=0, orient='horizontal', style = "gray.TSeparator")
            Sep3.place(x = col3_px, y = 8, relwidth = 0.3)
            Label(ws, text = 'Post-Processing (optional)').place(x = col3_px, y = 10)
            
            global Undo2_btn
            er_lbl = Label(ws, text = 'Erosion Size')
            er_lbl.place(x = col3_px, y = 40)
            Enter_ope2 = Entry(ws, textvariable = ope2, width = wi)
            Enter_ope2.place(in_ = er_lbl, y = 0, relx = spacing)
            
            global erspin_lbl
            erspin_lbl = Label(ws, text = 'Frame no.:')
            erspin_lbl.place(x = col3_px, y = 70)
            global spin8
            spin8 = Spinbox(ws, from_ = 0, to = len(tracked)-1, textvariable = spin8_val, wrap = True, width = wi)
            spin8.place(in_ = erspin_lbl, y = 0, relx = spacing)
            
            subim_lbl2 = Label(ws, text = 'Sub-image')
            subim_lbl2.place(x = col3_px, y = 100)
            xlbl2 = Label(ws, text = 'x =')
            xlbl2.place(in_ = subim_lbl2, y = 0, relx = spacing)
            Enter_opeX11 = Entry(ws, textvariable = x11_in, width = wi)
            Enter_opeX11.place(in_ = xlbl2, y = 0, relx = spacing)
            to3 = Label(ws, text = 'to')
            to3.place(in_ = Enter_opeX11, y = 0, relx = spacing)
            Enter_opeX22 = Entry(ws, textvariable = x22_in, width = wi)
            Enter_opeX22.place(in_ = to3, y = 0, relx = spacing)
            
            ylbl2 = Label(ws, text = 'y =')
            ylbl2.place(in_ = subim_lbl2, y = 30, relx = spacing)
            Enter_opeY11 = Entry(ws, textvariable = y11_in, width = wi)
            Enter_opeY11.place(in_ = ylbl2, y = 0, relx = spacing)
            to4 = Label(ws, text = 'to')
            to4.place(in_ = Enter_opeY11, y = 0, relx = spacing)
            Enter_opeY22 = Entry(ws, textvariable = y22_in, width = wi)
            Enter_opeY22.place(in_ = to4, y = 0, relx = spacing)
            
            fill_btn = Button(ws, text = 'Fill Holes', command = lambda:Fill(processed, Plotstr, c18))
            fill_btn.place(x = col3_px, y = 160)
            
            open2_btn = Button(ws, text = 'Apply Erosion', command = lambda:ErosionStep(processed, ope2.get(), spin8_val.get(), Plotstr, x11_in.get(), x22_in.get(), y11_in.get(), y22_in.get(), c16))
            open2_btn.place(x = col3_px, y = 190)
            
            openall2_btn = Button(ws, text = 'Erosion All Frames', command = lambda:ErosionAll(processed, ope2.get(), Plotstr, x11_in.get(), x22_in.get(), y11_in.get(), y22_in.get(), c17))
            openall2_btn.place(x = col3_px, y = 220)
        
            Sep4 = Separator(ws, takefocus=0, orient='horizontal', style = "gray.TSeparator")
            Sep4.place(x = col3_px, y = 247, relwidth = 0.3)
            
            #global spin9
            #spin9 = Spinbox(ws, from_ = 0, to = len(tracked)-1, textvariable = spin9_val, wrap = True)
            #spin9.place(x = 930, y = 250)
            #Label(ws, text = 'Frame no.:').place(x = 850, y = 250)
            vis6_btn = Button(ws, text = 'Visualize Final Mask', command = lambda:Vis_opefill(processed, spin_val.get(), Plotstr, canvas, c19))
            vis6_btn.place(x = col3_px, y = 250)
        else:
            spin8.destroy()
            spin8 = Spinbox(ws, from_ = 0, to = len(tracked)-1, textvariable = spin8_val, wrap = True)
            spin8.place(in_ = erspin_lbl, y = 0, relx = spacing)
            
            #spin9.destroy()
            #spin9 = Spinbox(ws, from_ = 0, to = len(tracked)-1, textvariable = spin9_val, wrap = True)
            #spin9.place(x = 930, y = 250)
        
        global c15
        c15 = 1
        
    def ErosionStep(arr, er_size, num, Plotstr, x1_in, x2_in, y1_in, y2_in, c):
        global arr_before_er
        arr_before_er = arr.copy()
        #global undo_str
        #undo_str = 'Erosion'
        
        num = int(num)
        er_size = float(er_size)
        
        x1_in = float(x1_in)
        x2_in = float(x2_in)
        y1_in = float(y1_in)
        y2_in = float(y2_in)
        
        if (x1_in >= x2_in) or (y1_in >= y2_in):
            processed[num] = dip.Erosion(arr[num], er_size)
        else:
            if contr == 'X': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Y': 
                x1_conv = int(np.floor((x1_in-MinY)/dy))
                x2_conv = int(np.floor((x2_in-MinY)/dy))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Z': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinY)/dy))
                y2_conv = int(np.floor((y2_in-MinY)/dy))
            
            Corr = np.zeros(np.shape(arr[num, y1_conv:y2_conv, x1_conv:x2_conv]))
            Corr[arr[num, y1_conv:y2_conv, x1_conv:x2_conv] > 0.8] = 1
            Corr_op = dip.Erosion(Corr, er_size)
            processed[num, y1_conv:y2_conv, x1_conv:x2_conv] = Corr_op
        
        Plotstr = 'Open'
        contr3 = 1
    

        Er_lbl = Label(ws, text = 'Done!', foreground = 'green')
        Er_lbl.place(x = 930, y = 190)
        ws.after(2000, destroy_widget, Er_lbl) 
        
        if c == 0:
            global Undo2_btn
            try:
                Undo2_btn.destroy()
                Undo2_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo2(arr_before_er, Undo2_btn))
                Undo2_btn.place(x = 930, y = 220)
            except:
                Undo2_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo2(arr_before_er, Undo2_btn))
                Undo2_btn.place(x = 930, y = 220)
        
        Undo2_btn.config(state = "normal")   
        
        global c16
        c16 = 1
        
    def ErosionAll(arr, er_size, Plotstr, x1_in, x2_in, y1_in, y2_in, c):
        er_size = float(er_size)
        
        global arr_before_er2
        arr_before_er2 = arr.copy()
        #global undo_str
        #undo_str = 'ErosionAll'
        
        x1_in = float(x1_in)
        x2_in = float(x2_in)
        y1_in = float(y1_in)
        y2_in = float(y2_in)
        
        #global opened
        #opened = arr.copy()
        
        if (x1_in >= x2_in) or (y1_in >= y2_in):
            for j in range(len(arr)):
                processed[j] = dip.Erosion(arr[j], er_size)
        else:
            if contr == 'X': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Y': 
                x1_conv = int(np.floor((x1_in-MinY)/dy))
                x2_conv = int(np.floor((x2_in-MinY)/dy))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Z': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinY)/dy))
                y2_conv = int(np.floor((y2_in-MinY)/dy))
            
            for j in range(len(arr)):
                Corr = np.zeros(np.shape(arr[j, y1_conv:y2_conv, x1_conv:x2_conv]))
                Corr[arr[j, y1_conv:y2_conv, x1_conv:x2_conv] > 0.8] = 1
                Corr_op = dip.Erosion(Corr, er_size)
                processed[j, y1_conv:y2_conv, x1_conv:x2_conv] = Corr_op
        
        Er_lbl = Label(ws, text = 'Done!', foreground = 'green')
        Er_lbl.place(x = 930, y = 220)
        ws.after(2000, destroy_widget, Er_lbl) 
        
        Plotstr = 'Open'
        contr3 = 2
    
        if c == 0:
            global Undo2_btn
            try:
                Undo2_btn.destroy()
                Undo2_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo2(arr_before_er2, Undo2_btn))
                Undo2_btn.place(x = 930, y = 220)
            except:
                Undo2_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo2(arr_before_er2, Undo2_btn))
                Undo2_btn.place(x = 930, y = 220)

        Undo2_btn.config(state = "normal")  
        
        global c17
        c17 = 1
        
    def Fill(arr, Plotstr, c):
        N = len(arr)
        global arr_before_fill
        arr_before_fill = arr.copy()
        
        global undo_str
        undo_str = 'Fill'
        
        #global filled
        #filled = arr.copy()
        for j in range(N):
            if Plotstr == 'Open':
                processed[j] = dip.FillHoles(dip.FixedThreshold(processed[j],0.5))
            else:
                processed[j] = dip.FillHoles(dip.FixedThreshold(arr[j],0.5))   
                
        Plotstr = 'Fill'
        
        Fill_lbl = Label(ws, text = 'Done!', foreground = 'green')
        Fill_lbl.place(x = 930, y = 160)
        ws.after(2000, destroy_widget, Fill_lbl)   
        
        contr3 = 3
        
        if c == 0:
            global Undo2_btn
            try:
                Undo2_btn.destroy()
                Undo2_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo2(arr_before_fill, Undo2_btn))
                Undo2_btn.place(x = 930, y = 220)
            except:
                Undo2_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo2(arr_before_fill, Undo2_btn))
                Undo2_btn.place(x = 930, y = 220)

        Undo2_btn.config(state = "normal")  
            
        global c18 
        c18 = 1
    
    def Undo2(arr_before, Undo2_btn):
        global processed
        processed = arr_before.copy()
        
        #if undo_str == 'Erosion':
        #    calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        #    calc_lbl.place(x = 1050, y = 190)
        #elif undo_str == 'ErosionAll':
        #    calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        #    calc_lbl.place(x = 1050, y = 220)
        #elif undo_str == 'Fill':  
        #    calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        #    calc_lbl.place(x = 1050, y = 160)
        
        calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        calc_lbl.place(x = 1050, y = 220)   
        
        ws.after(2000, destroy_widget, calc_lbl)
    
        Undo2_btn.config(state = "disabled")
        
        
    def Vis_opefill(fill, num, Plotstr, canvas, c):
        plt.close()
        canvas.get_tk_widget().destroy()
        Plotstr = 'processed'
        num = int(num)
        fig6 = plt.figure(figsize = (4.5,3.5))
        plot6 = fig6.add_subplot(111)
        if contr == 'X': 
            plot6.imshow(processed[num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinZ, MaxZ])
            plot6.set_title("Tracked Shape, Frame "+str(num), fontsize = 8)
            plot6.set_ylabel("y", fontsize = 9)
            plot6.set_xlabel("x", fontsize = 9)
            plot6.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Y': 
            plot6.imshow(processed[num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinY, MaxY, MinZ, MaxZ])
            plot6.set_title("Tracked Shape, Frame "+str(num), fontsize = 8)
            plot6.set_ylabel("y", fontsize = 9)
            plot6.set_xlabel("x", fontsize = 9)
            plot6.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Z': 
            plot6.imshow(processed[num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinY, MaxY])
            plot6.set_title("Tracked Shape, Frame "+str(num), fontsize = 8)
            plot6.set_ylabel("y", fontsize = 9)
            plot6.set_xlabel("x", fontsize = 9)
            plot6.tick_params(axis='both', which='major', labelsize=7)
            
        canvas = FigureCanvasTkAgg(fig6, master=ws)
        canvas.draw()
        canvas.get_tk_widget().place(x = 20, y = 100)
        
        if c == 0:        
            base_name6 = Text(ws, height = 1, width = 30)
            base_name6.place(x = basecol2_px, y = 280)
            save_frames_processed = Button(ws, text = 'Save Final Frames', command = lambda:savefunc(Plotstr, contr, processed, base_name6.get('1.0','end-1c')))
            save_frames_processed.place(x = col3_px, y = 280)
            
            base_name8 = Text(ws, height = 1, width = 30)
            base_name8.place(x = basecol2_px, y = 310)
            save_array_processed = Button(ws, text = 'Save Final Arrays', command = lambda:savearr(processed, base_name8.get('1.0','end-1c'), Plotstr))
            save_array_processed.place(x = col3_px, y = 310)
            
            base_name9 = Text(ws, height = 1, width = 30)
            base_name9.place(x = basecol2_px, y = 340)
            save_anim_processed = Button(ws, text = 'Save Final Animation', command = lambda:saveanim_final(processed, base_name9.get('1.0','end-1c'), contr))
            save_anim_processed.place(x = col3_px, y = 340)            
            
            sample_lbl = Label(ws, text = 'Enter sample size (in image x):')
            sample_lbl.place(x = col3_px, y = 375)
            Enter_xsteps = Entry(ws, textvariable = xsteps, width = wi)
            Enter_xsteps.place(in_ = sample_lbl, y = 0, relx = spacing)
        
            Label(ws, text = 'Uniform sampling:').place(x = col3_px, y = 430)
            Grid_Button = Button(ws, text = 'Create Grid', command = lambda:create_grid(processed, xsteps.get(), contr, c20))
            Grid_Button.place(x = col3_px, y = 460)
    
            Label(ws, text = 'Random sampling:').place(x = col3_px, y = 550)
            Random_Button = Button(ws, text = 'Create Points', command = lambda:create_random(processed, xsteps.get(), contr, c21))
            Random_Button.place(x = col3_px, y = 580)
    
    def saveanim_final(arr, filename, contr):

        plotws = tki.Toplevel(ws)
        plotws.title("Plot Specifications")
        plotws.geometry(str(horsz_plotws)+'x640')
        plotws.grab_set()
        
        default_font = tki.font.nametofont("TkDefaultFont")
        default_font2 = tki.font.nametofont("TkTextFont")
        default_font3 = tki.font.nametofont("TkFixedFont")
        default_font.configure(size=9)
        default_font2.configure(size=9)
        default_font3.configure(size=9)
        
        #Set colormap:
        global cmap_to_use
        cmap_to_use = "RdBu_r"
        
        def set_colormap(boxon):
            if boxon % 2 == 1:
                listbox3.config(state = "normal")
            else:
                listbox3.config(state = "disabled")

        def_colormap = tki.IntVar(value = 0)
        check_default_colormap = Checkbutton(plotws, text = "Customize", variable = def_colormap, command = lambda:set_colormap(def_colormap.get()))        
        check_default_colormap.place(x = 10, y = 90)
        
        #cmap_to_use = tki.StringVar(value = '')
        listbox3 = tki.Listbox(plotws, height=7, width = 25, selectmode=tki.SINGLE, exportselection=False)
        
        for j in range(len(cmaps)):
            listbox3.insert(tki.END, cmaps[j])
        listbox3.place(x = 120, y = 35)
        listbox3.config(state = "disabled")
        
        colormap_lbl = Label(plotws, text = 'Choose Colormap:')    
        colormap_lbl.place(x = 120, y = 10)   
        
        def color_selected(event):
            global cmap_to_use
            cmap_to_use = cmaps[int(listbox3.curselection()[0])]
    
        listbox3.bind('<<ListboxSelect>>', color_selected)
        
        #Set figure size:
        def_figsize = tki.IntVar(value = 0)
        check_default_figsize = Checkbutton(plotws, text = "Customize", variable = def_figsize, command = lambda:set_figsize(def_figsize.get()))        
        check_default_figsize.place(x = 10, y = 180)   
        
        Label(plotws, text='Choose Figure Size:').place(x = 120, y = 180)
        
        figure_x = tki.StringVar(value = "12")
        figure_y = tki.StringVar(value = "12")
        
        xfig = Label(plotws, text = 'x =')
        xfig.place(x = 120, y = 210)
        Enter_figx = Entry(plotws, textvariable = figure_x, width = 4)
        Enter_figx.place(in_ = xfig, y = 0, relx = spacing)
        yfig = Label(plotws, text = 'y =')
        yfig.place(in_ = Enter_figx, y = 0, relx = spacing)
        Enter_figy = Entry(plotws, textvariable = figure_y, width = 4)
        Enter_figy.place(in_ = yfig, y = 0, relx = spacing)
        
        Enter_figx.config(state = "disabled")
        Enter_figy.config(state = "disabled")
        
        def set_figsize(boxon):
            if boxon % 2 == 1:
                Enter_figx.config(state = "normal")
                Enter_figy.config(state = "normal")
            else:
                Enter_figx.config(state = "disabled")
                Enter_figy.config(state = "disabled")  
        
        #Set title:
        def_title = tki.IntVar(value = 0)
        check_default_title = Checkbutton(plotws, text = "Customize", variable = def_title, command = lambda:set_plottitle(def_title.get()))        
        check_default_title.place(x = 10, y = 240)   
        
        Label(plotws, text='Choose Figure Title:').place(x = 120, y = 240)
        
        figure_title = tki.StringVar(value = "")
        text_title = Text(plotws, height = 1, width = 20)
        text_title.place(x = 120, y = 270)        
        text_title.config(state = "disabled")
        
        def set_plottitle(boxon):
            if boxon % 2 == 1:
                text_title.config(state = "normal")
            else:
                text_title.config(state = "disabled")
        
        #Set titlesize 
        def_titlesize = tki.IntVar(value = 0)
        check_default_titlesize = Checkbutton(plotws, text = "Customize", variable = def_titlesize, command = lambda:set_titlesize(def_titlesize.get()))        
        check_default_titlesize.place(x = 10, y = 300)   
        
        Label(plotws, text='Choose Title Size:').place(x = 120, y = 300)
        
        titlesize = tki.StringVar(value = "14")
        Enter_titlesize = Entry(plotws, textvariable = titlesize, width = 6)
        Enter_titlesize.place(x = 120, y = 330)       
        Enter_titlesize.config(state = "disabled")
        
        def set_titlesize(boxon):
            if boxon % 2 == 1:
                Enter_titlesize.config(state = "normal")
            else:
                Enter_titlesize.config(state = "disabled")
        
        #Set ticksize 
        def_ticksize = tki.IntVar(value = 0)
        check_default_ticksize = Checkbutton(plotws, text = "Customize", variable = def_ticksize, command = lambda:set_ticksize(def_ticksize.get()))        
        check_default_ticksize.place(x = 10, y = 360)   
        
        Label(plotws, text='Choose Ticksize:').place(x = 120, y = 360)
        
        ticksize = tki.StringVar(value = "14")
        Enter_ticksize = Entry(plotws, textvariable = ticksize, width = 6)
        Enter_ticksize.place(x = 120, y = 390)       
        Enter_ticksize.config(state = "disabled")
        
        def set_ticksize(boxon):
            if boxon % 2 == 1:
                Enter_ticksize.config(state = "normal")
            else:
                Enter_ticksize.config(state = "disabled")

        #Set label
        def_label = tki.IntVar(value = 0)
        check_default_label = Checkbutton(plotws, text = "Customize", variable = def_label, command = lambda:set_label(def_label.get()))        
        check_default_label.place(x = 10, y = 420)   
        
        Label(plotws, text='Choose Labels:').place(x = 120, y = 420)
        
        label_x = tki.StringVar(value = "")
        label_y = tki.StringVar(value = "")
        
        axx_lbl = Label(plotws, text = 'x =')
        axx_lbl.place(x = 120, y = 450)
        Enter_labelx = Entry(plotws, textvariable = label_x, width = 6)
        Enter_labelx.place(in_ = axx_lbl, y = 0, relx = spacing)
        axy_lbl = Label(plotws, text = 'y =')
        axy_lbl.place(in_ = Enter_labelx, y = 0, relx = spacing)
        Enter_labely = Entry(plotws, textvariable = label_y, width = 6)
        Enter_labely.place(in_ = axy_lbl, y = 0, relx = spacing)
        
        Enter_labelx.config(state = "disabled")
        Enter_labely.config(state = "disabled")
        
        def set_label(boxon):
            if boxon % 2 == 1:
                Enter_labelx.config(state = "normal")
                Enter_labely.config(state = "normal")
            else:
                Enter_labelx.config(state = "disabled")
                Enter_labely.config(state = "disabled")
                
        #Set labelsize      
        def_labelsize = tki.IntVar(value = 0)
        check_default_labelsize = Checkbutton(plotws, text = "Customize", variable = def_labelsize, command = lambda:set_labelsize(def_labelsize.get()))        
        check_default_labelsize.place(x = 10, y = 480)   
        
        Label(plotws, text='Choose Labelsize:').place(x = 120, y = 480)
        
        labelsize = tki.StringVar(value = "14")
        Enter_labelsize = Entry(plotws, textvariable = labelsize, width = 6)
        Enter_labelsize.place(x = 120, y = 510)       
        Enter_labelsize.config(state = "disabled")
        
        def set_labelsize(boxon):
            if boxon % 2 == 1:
                Enter_labelsize.config(state = "normal")
            else:
                Enter_labelsize.config(state = "disabled")
        
        #Set vmin/vmax
        def_minmax = tki.IntVar(value = 0)
        check_default_minmax = Checkbutton(plotws, text = "Customize", variable = def_minmax, command = lambda:set_minmax(def_minmax.get()))        
        check_default_minmax.place(x = 10, y = 540)   
        
        Label(plotws, text='Choose Colormap Limits:').place(x = 120, y = 540)
        
        vmin = tki.IntVar(value = -5)
        vmax = tki.IntVar(value = 5)
        
        vmin_lbl = Label(plotws, text = 'vmin =')
        vmin_lbl.place(x = 120, y = 570)
        Enter_vmin = Entry(plotws, textvariable = vmin, width = 4)
        Enter_vmin.place(in_ = vmin_lbl, y = 0, relx = spacing)
        vmax_lbl = Label(plotws, text = 'vmax =')
        vmax_lbl.place(in_ = Enter_vmin, y = 0, relx = spacing)
        Enter_vmax = Entry(plotws, textvariable = vmax, width = 4)
        Enter_vmax.place(in_ = vmax_lbl, y = 0, relx = spacing)
        
        Enter_vmin.config(state = "disabled")
        Enter_vmax.config(state = "disabled")
        
        def set_minmax(boxon):
            if boxon % 2 == 1:
                Enter_vmin.config(state = "normal")
                Enter_vmax.config(state = "normal")
            else:
                Enter_vmin.config(state = "disabled")
                Enter_vmax.config(state = "disabled")
        
        conf_btn3 = Button(plotws, text='Confirm', command = lambda:destroy_widget_5(plotws, def_colormap.get(), def_figsize.get(), def_title.get(), \
        def_titlesize.get(), def_ticksize.get(), def_label.get(), def_labelsize.get(), def_minmax.get(), figure_x.get(), figure_y.get(), text_title.get('1.0','end-1c'), titlesize.get(), \
        ticksize.get(), label_x.get(), label_y.get(), labelsize.get(), vmin.get(), vmax.get(), cmap_to_use))
        
        conf_btn3.place(x = 120, y = 605)
        
        def destroy_widget_5(widget, boxon1, boxon2, boxon3, boxon4, boxon5, boxon6, boxon7, boxon8, figx, figy, title_name, titlesize, ticksize, labelx, labely,\
        labelsize, vmin, vmax, cmap_to_use):

            L = len(arr)
            if boxon1 % 2 == 0:
                cmap_to_use = "gray"
                
            if boxon2 % 2 == 0:
                figx = dim[1]/50
                figy = dim[0]/50
            else:
                figx = int(figx)
                figy = int(figy)
            
            if boxon4 % 2 == 0:
                titlesize = 14
            else:
                titlesize = int(titlesize)

            if boxon5 % 2 == 0:
                ticksize = 14
            else:
                ticksize = int(ticksize)

            if boxon7 % 2 == 0:
                labelsize = 14
            else:
                labelsize = int(labelsize)
            
            if boxon8 % 2 == 0:
                vmin = 0
                vmax = 1.5
            else:
                vmin = float(vmin)
                vmax = float(vmax)
        
            fig_anim = plt.figure(figsize=(figx, figy))
            if contr == 'X':
                ax_anim = plt.axes(xlim=(MinX, MaxX), ylim=(MinZ, MaxZ))
                nanarray = np.empty((dim[1], dim[0]))
                nanarray[:] = np.nan
                im = plt.imshow(nanarray, origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinZ, MaxZ])
                if boxon3 % 2 == 0:
                    ax_anim.set_title("Proxy map", fontsize = titlesize)
                else: 
                    ax_anim.set_title(title_name, fontsize = titlesize)
                if boxon6 % 2 == 0:
                    ax_anim.set_ylabel("y", fontsize = labelsize)
                    ax_anim.set_xlabel("x", fontsize = labelsize)
                else: 
                    ax_anim.set_ylabel(labely, fontsize = labelsize)
                    ax_anim.set_xlabel(labelx, fontsize = labelsize) 
                ax_anim.tick_params(labelsize = ticksize)
            elif contr == 'Y': 
                ax_anim = plt.axes(xlim=(MinY, MaxY), ylim=(MinZ, MaxZ))
                nanarray = np.empty((dim[1], dim[0]))
                nanarray[:] = np.nan
                im = plt.imshow(nanarray, origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinY, MaxY, MinZ, MaxZ])
                if boxon6 % 2 == 0:
                    ax_anim.set_ylabel("y", fontsize = labelsize)
                    ax_anim.set_xlabel("x", fontsize = labelsize)
                else: 
                    ax_anim.set_ylabel(labely, fontsize = labelsize)
                    ax_anim.set_xlabel(labelx, fontsize = labelsize)
                if boxon3 % 2 == 0:
                    ax_anim.set_title("Proxy map", fontsize = titlesize)
                else: 
                    ax_anim.set_title(title_name, fontsize = titlesize) 
                ax_anim.tick_params(labelsize = ticksize)
            elif contr == 'Z':
                ax_anim = plt.axes(xlim=(MinX, MaxX), ylim=(MinY, MaxY))
                nanarray = np.empty((dim[1], dim[0]))
                nanarray[:] = np.nan
                im = plt.imshow(nanarray, origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinY, MaxY])
                if boxon6 % 2 == 0:
                    ax_anim.set_ylabel("y", fontsize = labelsize)
                    ax_anim.set_xlabel("x", fontsize = labelsize)
                else:
                    ax_anim.set_ylabel(labely, fontsize = labelsize)
                    ax_anim.set_xlabel(labelx, fontsize = labelsize)
                if boxon3 % 2 == 0:
                    ax_anim.set_title("Proxy map", fontsize = titlesize)
                else:
                    ax_anim.set_title(title_name, fontsize = titlesize) 
                ax_anim.tick_params(labelsize = ticksize)
                
            def init():
                im.set_data(nanarray)
                #plt.axis('off')
                return [im]
        
            def animate(j):
                im.set_array(arr[j])
                #plt.axis('off')
                return [im]
        
            anim = FuncAnimation(fig_anim, animate, init_func=init,
                                    frames=L, interval=120, blit=True)
        
            anim.save(filename+'.gif', writer='imagemagick')
            
            plt.close()
            
            save_lbl = Label(ws, text = 'Saved!', foreground = 'green')    
            save_lbl.place(x = saved_px, y = 340)
            
            ws.after(2000, destroy_widget, save_lbl)
            plotws.destroy()

    def create_grid(arr, steps, contr, c):
        Nsteps_x = int(steps)
        
        if contr == "X":
            dx_new = (MaxX-MinX)/Nsteps_x
            Nsteps_y = (MaxZ-MinZ)/dx_new  
            x_axis = np.linspace(0, dim[1], Nsteps_x)
            y_axis = np.linspace(0, dim[0], int(Nsteps_y))        
        elif contr == 'Y':
            dx_new = (MaxY-MinY)/Nsteps_x
            Nsteps_y = (MaxZ-MinZ)/dx_new    
            x_axis = np.linspace(0, dim[1], Nsteps_x)
            y_axis = np.linspace(0, dim[0], int(Nsteps_y))
        elif contr == 'Z':
            dx_new = (MaxX-MinX)/Nsteps_x
            Nsteps_y = (MaxY-MinY)/dx_new    
            x_axis = np.linspace(0, dim[1], Nsteps_x)
            y_axis = np.linspace(0, dim[0], int(Nsteps_y))            
        Grid = np.meshgrid(x_axis, y_axis)
        
        global full_coords
        full_coords = []
        
        for n_ind in range(len(arr)):    
            Tw10 = arr[n_ind,:,:].astype(np.uint8)
            ret, bin_10 = cv2.threshold(Tw10, 0.5, 255, cv2.THRESH_BINARY)
            
            cont_10, hierachy = cv2.findContours(bin_10, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            #print("Total Number of Contours found =", len(cont_10))
            #print("contours are: \n",cont_10)
                    
            img_contours = np.zeros(bin_10.shape)
            cv2.drawContours(img_contours, cont_10, -1, (255,0,0), 2)
            
            lencont = []
            new_coords = []
            for j in range(len(Grid[0][0])):
                    for k in range(len(Grid[1])):
                        dist2 = []
                        for m in range(len(cont_10)):
                            lencont.append(len(cont_10[m]))
                        maxlen = max(lencont)
                        for m in range(len(cont_10)):
                            if lencont[m] == maxlen:
                                dist = cv2.pointPolygonTest(cont_10[m], tuple([Grid[0][0][j], Grid[1][k][0]]), False)
                            else:
                                dist2.append(cv2.pointPolygonTest(cont_10[m], tuple([Grid[0][0][j], Grid[1][k][0]]), False))                                
                        if dist > 0:
                            fail = 0
                            for l in range(len(dist2)):
                                if dist2[l] > 0:
                                    fail = 1
                            if fail == 0:
                                new_coords.append([Grid[0][0][j], Grid[1][k][0]])
            
            full_coords.append(new_coords)
        
        grid_lbl = Label(ws, text = 'Grid created!', foreground = 'green')    
        grid_lbl.place(x = 930, y = 460)
        
        ws.after(2000, destroy_widget, grid_lbl)
        
        if c == 0:
            base_name7 = Text(ws, height = 1, width = 30)
            base_name7.place(x = 920, y = 490)
            PhysCoord_btn = Button(ws, text = 'Get Coordinates', command = lambda:get_phys_coords(full_coords, contr, base_name7.get('1.0','end-1c')))
            PhysCoord_btn.place(x = col3_px, y = 490)
            
        global c20
        c20 = 1
        
    def get_phys_coords(full_coords, contr, name):
        global phys_coords
        phys_coords = full_coords.copy()
        if contr == 'X':
            for j in range(len(full_coords)):
                savedcoords = []
                for k in range(len(full_coords[j])):
                    phys_coords[j][k][0] = MinX+dx*full_coords[j][k][0]
                    phys_coords[j][k][1] = MinZ+dz*full_coords[j][k][1]
                    savedcoords.append((float(phys_coords[j][k][0]),float(yy),float(phys_coords[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords)
        elif contr == 'Y':
            for j in range(len(full_coords)):
                savedcoords = []
                for k in range(len(full_coords[j])):           
                    phys_coords[j][k][0] = MinY+dy*full_coords[j][k][0]
                    phys_coords[j][k][1] = MinZ+dz*full_coords[j][k][1]
                    savedcoords.append((float(xx),float(phys_coords[j][k][0]),float(phys_coords[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords)
        elif contr == 'Z':
            for j in range(len(full_coords)):
                savedcoords = []
                for k in range(len(full_coords[j])):           
                    phys_coords[j][k][0] = MinX+dx*full_coords[j][k][0]
                    phys_coords[j][k][1] = MinY+dy*full_coords[j][k][1]
                    savedcoords.append((float(phys_coords[j][k][0]),float(phys_coords[j][k][1]), float(zz)))
                np.savetxt(name+str(j)+".txt", savedcoords)        
        coord_lbl = Label(ws, text = 'Coordinates saved!', foreground = 'green')    
        coord_lbl.place(x = col3_px, y = 520)
        
        ws.after(2000, destroy_widget, coord_lbl)

    def create_random(arr, steps, contr, c): 
        num_points = int(steps)**2
        
        random_x = np.random.randint(dim[1], size = (len(arr), num_points))
        random_y = np.random.randint(dim[0], size = (len(arr), num_points))        

        global full_coords2
        full_coords2 = []
        
        for n_ind in range(len(arr)):    
            Tw10 = arr[n_ind,:,:].astype(np.uint8)
            ret, bin_10 = cv2.threshold(Tw10, 0.5, 255, cv2.THRESH_BINARY)
            
            cont_10, hierachy = cv2.findContours(bin_10, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    
            img_contours = np.zeros(bin_10.shape)
            cv2.drawContours(img_contours, cont_10, -1, (255,0,0), 2)
            
            lencont = []
            new_coords2 = []
            for j in range(num_points):
                dist2 = []
                for m in range(len(cont_10)):
                    lencont.append(len(cont_10[m]))
                maxlen = max(lencont)
                for m in range(len(cont_10)):
                    if lencont[m] == maxlen:
                        dist = cv2.pointPolygonTest(cont_10[m], tuple([float(random_x[n_ind, j]), float(random_y[n_ind, j])]), False)
                    else:
                        dist2.append(cv2.pointPolygonTest(cont_10[m], tuple([float(random_x[n_ind, j]), float(random_y[n_ind, j])]), False))
                if dist > 0:
                    fail = 0
                    for l in range(len(dist2)):
                        if dist2[l] > 0:
                            fail = 1
                    if fail == 0:
                        new_coords2.append([float(random_x[n_ind,j]), float(random_y[n_ind,j])])                
            
            full_coords2.append(new_coords2)
        
        grid_lbl = Label(ws, text = 'Points created!', foreground = 'green')    
        grid_lbl.place(x = 930, y = 580)
        
        ws.after(2000, destroy_widget, grid_lbl)
        
        if c == 0:
            base_name10 = Text(ws, height = 1, width = 30)
            base_name10.place(x = 920, y = 610)
            PhysCoord_randbtn = Button(ws, text = 'Get Coordinates', command = lambda:get_phys_randcoords(full_coords2, contr, base_name10.get('1.0','end-1c')))
            PhysCoord_randbtn.place(x = col3_px, y = 610)
        
        global c21
        c21 = 1
        
    def get_phys_randcoords(full_coords2, contr, name):
        global phys_coords2
        phys_coords2 = full_coords2.copy()
        if contr == 'X':
            for j in range(len(full_coords2)):
                savedcoords2 = []
                for k in range(len(full_coords[j])):
                    phys_coords2[j][k][0] = MinX+dx*full_coords2[j][k][0]
                    phys_coords2[j][k][1] = MinZ+dz*full_coords2[j][k][1]
                    savedcoords2.append((float(phys_coords2[j][k][0]),float(yy),float(phys_coords2[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords2)
        elif contr == 'Y':
            for j in range(len(full_coords2)):
                savedcoords2 = []
                for k in range(len(full_coords2[j])):           
                    phys_coords2[j][k][0] = MinY+dy*full_coords2[j][k][0]
                    phys_coords2[j][k][1] = MinZ+dz*full_coords2[j][k][1]
                    savedcoords2.append((float(xx),float(phys_coords2[j][k][0]),float(phys_coords2[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords2)
        elif contr == 'Z':
            for j in range(len(full_coords2)):
                savedcoords2 = []
                for k in range(len(full_coords2[j])):           
                    phys_coords2[j][k][0] = MinX+dx*full_coords2[j][k][0]
                    phys_coords2[j][k][1] = MinY+dy*full_coords2[j][k][1]
                    savedcoords2.append((float(phys_coords2[j][k][0]),float(phys_coords2[j][k][1]), float(zz)))
                np.savetxt(name+str(j)+".txt", savedcoords2)
                
        coord_lbl = Label(ws, text = 'Coordinates saved!', foreground = 'green')    
        coord_lbl.place(x = col3_px, y = 640)
        
        ws.after(2000, destroy_widget, coord_lbl)

    ws.protocol("WM_DELETE_WINDOW", ws.quit)
    ws.mainloop()
    ws.destroy()

elif selected_index == 1:
    ws = Tk()
    ws.title(Name+" <Post-Processing Mode>")
    ws.geometry(str(horsz)+'x610')
    
    default_font = tki.font.nametofont("TkDefaultFont")
    default_font2 = tki.font.nametofont("TkTextFont")
    default_font3 = tki.font.nametofont("TkFixedFont")
    default_font.configure(size=9)
    default_font2.configure(size=9)
    default_font3.configure(size=9)
    
    Style().configure("TButton", padding=1)
    
    canv_num = 0
    spin_val = tki.StringVar(value=0)
    ope = tki.StringVar(value = 0)
    spin4_val = tki.StringVar(value=0)
    spin5_val = tki.StringVar(value=0)
    spin6_val = tki.StringVar(value=0)
    x1_in = tki.StringVar(value = 0)
    x2_in = tki.StringVar(value = 0)
    y1_in = tki.StringVar(value = 0)
    y2_in = tki.StringVar(value = 0)
    x11_in = tki.StringVar(value = 0)
    x22_in = tki.StringVar(value = 0)
    y11_in = tki.StringVar(value = 0)
    y22_in = tki.StringVar(value = 0)
    xsteps = tki.StringVar(value = 0)
    overlap = tki.StringVar(value = 0.1)
    ope2 = tki.StringVar(value = 0)
    contr4 = 0
    
    #control parameters for avoiding creating widgets multiple times
    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    
    #controls the creation of vis8_btn-Button
    contr_vis = 0
    
    addat = Label(ws, text='Load current FR Mask:')
    addat.place(x = 20, y = 10)
    
    addatbtn = Button(ws, text ='Choose Files', command = lambda:open_file_npz())
    addatbtn.place(in_ = addat, y = 0, relx = spacing)
    
    upld = Button(ws, text='Load Files', command = lambda:uploadFiles_npz_only(file_path_npz, c1))
    upld.place(in_ = addatbtn, y = 0, relx = spacing)
    
    def open_file_npz():
        global file_path_npz
        file_path_npz = askopenfilenames(initialdir='./', filetypes=[('NPZ Files', '*npz')])
        
    def uploadFiles_npz_only(file_path_npz, c):
        global original
        original = []
        global tracked
        Test = np.load(file_path_npz[0], allow_pickle = True)
        for j in range(0, len(Test['data'])):
            original.append(Test['data'][int(j)])
        
        original = np.array(original)
        tracked = original.copy()
        global dim, MinX, MaxX, MinY, MaxY, MinZ, MaxZ, dx, dy, dz, contr
        
        
        if (len(Test['x']) > 1) & (len(Test['y']) > 1):
            global zz
            zz = Test['z']
            #print(np.shape(Test['x']))
            dim = [len(Test['y']), len(Test['x'])]
            MinX = min(Test['x'])
            MaxX = max(Test['x'])
            MX = (MaxX-MinX)
            dx = MX/(dim[1]-1)
            MinY = min(Test['y'])
            MaxY = max(Test['y'])
            MY = (MaxY-MinY)
            dy = MY/(dim[0]-1)
            contr = 'Y'            
        elif (len(Test['x']) > 1):
            global yy
            yy = Test['y']
            #print(np.shape(Test['x']))
            dim = [len(Test['z']), len(Test['x'])]
            MinX = min(Test['x'])
            MaxX = max(Test['x'])
            MX = (MaxX-MinX)
            dx = MX/(dim[1]-1)
            MinZ = min(Test['z'])
            MaxZ = max(Test['z'])
            MZ = (MaxZ-MinZ)
            dz = MZ/(dim[0]-1)
            contr = 'X'   
        else:
            global xx
            xx = Test['x']
            dim = [len(Test['z']), len(Test['y'])]
            MinY = min(Test['y'])
            MaxY = max(Test['y'])
            MY = (MaxY-MinY)
            dy = MY/(dim[1]-1)
            MinZ = min(Test['z'])
            MaxZ = max(Test['z'])
            MZ = (MaxZ-MinZ)
            dz = MZ/(dim[0]-1)
            contr = 'Y'
        
        Uploadnpz_lbl = Label(ws, text='Files Loaded Successfully!', foreground='green')
        Uploadnpz_lbl.place(x = 165, y = 40)
            
        ws.after(2000, destroy_widget, Uploadnpz_lbl)
        
        if c == 0:
            global spin
            global vis_lbl
            vis_lbl = Label(ws, text = 'Choose Image Frame no.:')
            vis_lbl.place(x = 20, y = 70)
            spin = Spinbox(ws, from_ = 0, to = len(original)-1, textvariable = spin_val, wrap = True, width = wi)
            spin.place(in_ = vis_lbl, y = 0, relx = spacing)
            global vis_btn
            vis_btn = Button(ws, text='Visualize Original Mask', command = lambda:Vis_track1(original, spin_val.get(), contr4, canv_num, c2))
            vis_btn.place(in_ = spin, y = 0, relx = spacing)
        else:
            spin.destroy()
            spin = Spinbox(ws, from_ = 0, to = len(original)-1, textvariable = spin_val, wrap = True, width = wi)
            spin.place(in_ = vis_lbl, y = 0, relx = spacing)
            vis_btn.destroy()
            vis_btn = Button(ws, text='Visualize Original Mask', command = lambda:Vis_track1(original, spin_val.get(), contr4, canv_num, c2))
            vis_btn.place(in_ = spin, y = 0, relx = spacing)
        
        global c1
        c1 = 1
        
    def Vis_track1(arr, num, contr4, num2, c):
        plt.close()
        num = int(num)
        fig5 = plt.figure(figsize = (4.5,3.5))
        plot5 = fig5.add_subplot(111)
        
        if contr == 'X': 
            plot5.imshow(arr[num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinZ, MaxZ])
            plot5.set_title("Input Shape, Frame "+str(num), fontsize = 8)
            plot5.set_ylabel("y", fontsize = 9)
            plot5.set_xlabel("x", fontsize = 9)
            plot5.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Y': 
            plot5.imshow(arr[num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinY, MaxY, MinZ, MaxZ])
            plot5.set_title("Input Shape, Frame "+str(num), fontsize = 8)
            plot5.set_ylabel("y", fontsize = 9)
            plot5.set_xlabel("x", fontsize = 9)
            plot5.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Z': 
            plot5.imshow(arr[num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinY, MaxY])
            plot5.set_title("Input Shape, Frame "+str(num), fontsize = 8)
            plot5.set_ylabel("y", fontsize = 9)
            plot5.set_xlabel("x", fontsize = 9)
            plot5.tick_params(axis='both', which='major', labelsize=7)            
        
        if num2 == 0:
            global canvas
            canvas = FigureCanvasTkAgg(fig5, master=ws)
            canvas.draw()
            canvas.get_tk_widget().place(x = 20, y = 100)
        else:     
            canvas.get_tk_widget().destroy()
            canvas = FigureCanvasTkAgg(fig5, master=ws)
            canvas.draw()
            canvas.get_tk_widget().place(x = 20, y = 100)
        
        global canv_num
        canv_num = 1        
                
        if c == 0: 
            global proc_btn
            proc_btn = Button(ws, text = 'Proceed', command = lambda:Proceed(contr4, c10))
            proc_btn.place(x = col3_px, y = 190)
            
            Style().configure("gray.TSeparator", background="gray")
            
            Sep = Separator(ws, takefocus=0, orient='horizontal', style = "gray.TSeparator")
            Sep.place(x = col2_px, y = 7, relwidth = 0.22)
            
            Label(ws, text = 'Specify Processing Region:').place(x = col2_px, y = 10) 
            
            global Undo_btn
            
            global frame_lbl
            frame_lbl = Label(ws, text = 'Frame no.:')
            frame_lbl.place(x = col2_px, y = 40)                
            global spin4
            spin4 = Spinbox(ws, from_ = 0, to = len(arr)-1, textvariable = spin4_val, wrap = True, width = wi)
            spin4.place(in_ = frame_lbl, y = 0, relx = spacing)

            subim_lbl3 = Label(ws, text = 'Sub-image')
            subim_lbl3.place(x = col2_px, y = 70)
            xlbl3 = Label(ws, text = 'x =')
            xlbl3.place(in_ = subim_lbl3, y = 0, relx = spacing)
            Enter_opeX1 = Entry(ws, textvariable = x1_in, width = wi)
            Enter_opeX1.place(in_ = xlbl3, y = 0, relx = spacing)
            to5 = Label(ws, text = 'to')
            to5.place(in_ = Enter_opeX1, y = 0, relx = spacing)
            Enter_opeX2 = Entry(ws, textvariable = x2_in, width = wi)
            Enter_opeX2.place(in_ = to5, y = 0, relx = spacing)
            
            ylbl3 = Label(ws, text = 'y =')
            ylbl3.place(in_ = subim_lbl3, y = 30, relx = spacing)
            Enter_opeY1 = Entry(ws, textvariable = y1_in, width = wi)
            Enter_opeY1.place(in_ = ylbl3, y = 0, relx = spacing)
            to6 = Label(ws, text = 'to')
            to6.place(in_ = Enter_opeY1, y = 0, relx = spacing)
            Enter_opeY2 = Entry(ws, textvariable = y2_in, width = wi)
            Enter_opeY2.place(in_ = to6, y = 0, relx = spacing)
                        
            Label(ws, text = 'Post-processing (Opening):').place(x = col2_px, y = 130)   
            Op_lbl = Label(ws, text = 'Opening Size')
            Op_lbl.place(x = col2_px, y = 160)
            Enter_ope = Entry(ws, textvariable = ope, width = wi)
            Enter_ope.place(in_ = Op_lbl, y = 0, relx = spacing)
            
            open_btn = Button(ws, text = 'Apply Opening', command = lambda:OpeningStep(tracked, ope.get(), spin4_val.get(), x1_in.get(), x2_in.get(), y1_in.get(), y2_in.get(), c3, contr_vis))
            open_btn.place(x = col2_px, y = 190)
            
            openall_btn = Button(ws, text = 'Opening All Frames', command = lambda:OpeningAll(tracked, ope.get(), x1_in.get(), x2_in.get(), y1_in.get(), y2_in.get(), c4, contr_vis))
            openall_btn.place(x = col2_px, y = 220)
            
            Label(ws, text = 'Post-processing (Erosion):').place(x = col2_px, y = 250)
            Er_lbl = Label(ws, text = 'Erosion Size')
            Er_lbl.place(x = col2_px, y = 280)
            Enter_ope2 = Entry(ws, textvariable = ope2, width = wi)
            Enter_ope2.place(in_ = Er_lbl, y = 0, relx = spacing)
            
            open2_btn = Button(ws, text = 'Apply Erosion', command = lambda:ErosionStep(tracked, ope2.get(), spin4_val.get(), x1_in.get(), x2_in.get(), y1_in.get(), y2_in.get(), c5, contr_vis))
            open2_btn.place(x = col2_px, y = 310)
            
            openall2_btn = Button(ws, text = 'Erosion All Frames', command = lambda:ErosionAll(tracked, ope2.get(), x1_in.get(), x2_in.get(), y1_in.get(), y2_in.get(), c6, contr_vis))
            openall2_btn.place(x = col2_px, y = 340)
            
            Label(ws, text = "Post-processing (Filling):").place(x = col2_px, y = 370)
            fill_btn = Button(ws, text = 'Fill Holes', command = lambda:Fill(tracked, c7, contr_vis))
            fill_btn.place(x = col2_px, y = 400)        
        
            Sep2 = Separator(ws, takefocus=0, orient='horizontal', style = "gray.TSeparator")
            Sep2.place(x = col2_px, y = 427, relwidth = 0.22)
            
            Label(text = "Re-tracking (if needed):").place(x = col3_px, y = 10)
            
            init_track_btn = Button(ws, text = 'Initialize Re-Tracking', command = lambda:init_tracking(tracked, spin5_val.get(), c8))
            init_track_btn.place(x = col3_px, y = 70)
            
            global retrack_lbl
            retrack_lbl = Label(ws, text = 'Start re-tracking from frame: ')
            retrack_lbl.place(x = col3_px, y = 40)
            global spin5
            spin5 = Spinbox(ws, from_ = 0, to = len(arr)-1, textvariable = spin5_val, wrap = True, width = wi)
            spin5.place(in_ = retrack_lbl, y = 0, relx = spacing)
              
        else:
            proc_btn.destroy()
            proc_btn = Button(ws, text = 'Proceed', command = lambda:Proceed(contr4, c10))
            proc_btn.place(x = col3_px, y = 190)
            
            spin4.destroy()
            spin4 = Spinbox(ws, from_ = 0, to = len(arr)-1, textvariable = spin4_val, wrap = True, width = wi)
            spin4.place(in_ = frame_lbl, y = 0, relx = spacing)
            
            spin5.destroy()
            spin5 = Spinbox(ws, from_ = 0, to = len(arr)-1, textvariable = spin5_val, wrap = True, width = wi)
            spin5.place(in_ = retrack_lbl, y = 0, relx = spacing)
     
        
        global c2
        c2 = 1

    def Proceed(contr4, c):      
        
        if c == 0:
            global base_name6
            base_name6 = Text(ws, height = 1, width = 30)
            base_name6.place(x = basecol2_px, y = 220)
            
            global base_name8
            base_name8 = Text(ws, height = 1, width = 30)
            base_name8.place(x = basecol2_px, y = 250)
            
            global base_name9         
            base_name9 = Text(ws, height = 1, width = 30)
            base_name9.place(x = basecol2_px, y = 280)
            
            lbl1 = Label(ws, text = 'Enter sampling (in x):')
            lbl1.place(x = col3_px, y = 315)
            
            Enter_xsteps = Entry(ws, textvariable = xsteps, width = wi)
            Enter_xsteps.place(x = col3_px, y = 345)
            
            lbl2 = Label(ws, text = 'Uniform sampling:')
            lbl2.place(x = col3_px, y = 370)

            lbl3 = Label(ws, text = 'Random sampling:')
            lbl3.place(x = col3_px, y = 490)
            
            global save_frames_processed
            global save_array_processed
            global save_anim_processed
            global Random_Button
            global Grid_Button
            
                
            if contr4 == 2:
                
                save_frames_processed = Button(ws, text = 'Save Final Frames', command = lambda:savefunc(contr, retracked, base_name6.get('1.0','end-1c')))
                save_frames_processed.place(x = col3_px, y = 220)
                
                save_array_processed = Button(ws, text = 'Save Final Arrays', command = lambda:savearr(retracked, base_name8.get('1.0','end-1c')))
                save_array_processed.place(x = col3_px, y = 250) 

                save_anim_processed = Button(ws, text = 'Save Final Animation', command = lambda:saveanim_final(retracked, base_name9.get('1.0','end-1c'), contr))
                save_anim_processed.place(x = col3_px, y = 280)
                
                Random_Button = Button(ws, text = 'Create Points', command = lambda:create_random(retracked, xsteps.get(), contr, c12))
                Random_Button.place(x = col3_px, y = 520)
                
                Grid_Button = Button(ws, text = 'Create Grid', command = lambda:create_grid(retracked, xsteps.get(), contr, c11))
                Grid_Button.place(x = col3_px, y = 400)
  
            else: 
                save_frames_processed = Button(ws, text = 'Save Final Frames', command = lambda:savefunc(contr, tracked, base_name6.get('1.0','end-1c')))
                save_frames_processed.place(x = col3_px, y = 220)

                save_array_processed = Button(ws, text = 'Save Final Arrays', command = lambda:savearr(tracked, base_name8.get('1.0','end-1c')))
                save_array_processed.place(x = col3_px, y = 250)
                
                save_anim_processed = Button(ws, text = 'Save Final Animation', command = lambda:saveanim_final(tracked, base_name9.get('1.0','end-1c'), contr))
                save_anim_processed.place(x = col3_px, y = 280)
                
                Random_Button = Button(ws, text = 'Create Points', command = lambda:create_random(tracked, xsteps.get(), contr, c12))
                Random_Button.place(x = col3_px, y = 520)
                
                Grid_Button = Button(ws, text = 'Create Grid', command = lambda:create_grid(tracked, xsteps.get(), contr, c11))
                Grid_Button.place(x = col3_px, y = 400)
 

            
        else:
            base_name6.destroy()
            base_name6 = Text(ws, height = 1, width = 30)
            base_name6.place(x = basecol2_px, y = 220)
            
            base_name8.destroy()
            base_name8 = Text(ws, height = 1, width = 30)
            base_name8.place(x = basecol2_px, y = 250)
            
            base_name9.destroy()        
            base_name9 = Text(ws, height = 1, width = 30)
            base_name9.place(x = basecol2_px, y = 280)

            if contr4 == 2:
                save_frames_processed.destroy()
                save_frames_processed = Button(ws, text = 'Save Final Frames', command = lambda:savefunc(contr, retracked, base_name6.get('1.0','end-1c')))
                save_frames_processed.place(x = col3_px, y = 220)
                
                save_array_processed.destroy()
                save_array_processed = Button(ws, text = 'Save Final Arrays', command = lambda:savearr(retracked, base_name8.get('1.0','end-1c')))
                save_array_processed.place(x = col3_px, y = 250) 

                save_anim_processed.destroy()
                save_anim_processed = Button(ws, text = 'Save Final Animation', command = lambda:saveanim_final(retracked, base_name9.get('1.0','end-1c'), contr))
                save_anim_processed.place(x = col3_px, y = 280)

                Random_Button.destroy()
                Random_Button = Button(ws, text = 'Create Points', command = lambda:create_random(retracked, xsteps.get(), contr, c12))
                Random_Button.place(x = col3_px, y = 520)
                
                Grid_Button.destroy()
                Grid_Button = Button(ws, text = 'Create Grid', command = lambda:create_grid(retracked, xsteps.get(), contr, c11))
                Grid_Button.place(x = col3_px, y = 400)
  
            else:
                save_frames_processed.destroy()
                save_frames_processed = Button(ws, text = 'Save Final Frames', command = lambda:savefunc(contr, tracked, base_name6.get('1.0','end-1c')))
                save_frames_processed.place(x = col3_px, y = 220)

                save_array_processed.destroy()
                save_array_processed = Button(ws, text = 'Save Final Arrays', command = lambda:savearr(tracked, base_name8.get('1.0','end-1c')))
                save_array_processed.place(x = col3_px, y = 250)
                
                save_anim_processed.destroy()
                save_anim_processed = Button(ws, text = 'Save Final Animation', command = lambda:saveanim_final(tracked, base_name9.get('1.0','end-1c'), contr))
                save_anim_processed.place(x = col3_px, y = 280)
                
                Random_Button.destroy()
                Random_Button = Button(ws, text = 'Create Points', command = lambda:create_random(tracked, xsteps.get(), contr, c12))
                Random_Button.place(x = col3_px, y = 520)
                
                Grid_Button.destroy()
                Grid_Button = Button(ws, text = 'Create Grid', command = lambda:create_grid(tracked, xsteps.get(), contr, c11))
                Grid_Button.place(x = col3_px, y = 400)
                
        global c10
        c10 = 1

    def OpeningStep(arr, ope_size, num, x1_in, x2_in, y1_in, y2_in, c, c_v):
        #global undo_str
        #undo_str = 'Open'
        
        global arr_before
        arr_before = tracked.copy()
        
        global contr4
        contr4 = 1
        
        num = int(num)
        ope_size = float(ope_size)
        x1_in = float(x1_in)
        x2_in = float(x2_in)
        y1_in = float(y1_in)
        y2_in = float(y2_in)
        
        if (x1_in >= x2_in) or (y1_in >= y2_in):
            arr[num] = dip.Opening(arr[num], ope_size)
        else:
            if contr == 'X': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Y': 
                x1_conv = int(np.floor((x1_in-MinY)/dy))
                x2_conv = int(np.floor((x2_in-MinY)/dy))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Z': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinY)/dy))
                y2_conv = int(np.floor((y2_in-MinY)/dy))
                        
            Corr = np.zeros(np.shape(arr[num, y1_conv:y2_conv, x1_conv:x2_conv]))
            Corr[arr[num, y1_conv:y2_conv, x1_conv:x2_conv] > 0.8] = 1
            Corr_op = dip.Opening(Corr, ope_size)
            arr[num, y1_conv:y2_conv, x1_conv:x2_conv] = Corr_op
    
        calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        calc_lbl.place(x = 630, y = 190)
        
        ws.after(2000, destroy_widget, calc_lbl)
        
        if c == 0:
            global Undo_btn
            try:
                Undo_btn.destroy()
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo(arr_before_er, Undo_btn))
                Undo_btn.place(x = 630, y = 400)
            except:
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo(arr_before_er, Undo_btn))
                Undo_btn.place(x = 630, y = 400)
                
        Undo_btn.config(state = "normal")

        if c_v == 0:
            vis8_btn = Button(ws, text='Visualize Processing', command = lambda:Vis_track1(tracked, spin_val.get(), contr4, canv_num, c2))
            vis8_btn.place(x = col2_px, y = 430)
            
            global contr_vis
            contr_vis = 1

        global c3
        c3 = 1
    
    def Undo(arr_2, Undo_btn):
        global tracked
        tracked = arr_2.copy()
        
        #if undo_str == 'Open':
        #    calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        #    calc_lbl.place(x = 740, y = 190)
        #elif undo_str == 'OpenAll':
        #    calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        #    calc_lbl.place(x = 740, y = 220)
        
        Undo_btn.config(state = "disabled")
        
        calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        calc_lbl.place(x = 740, y = 400)
 
        ws.after(2000, destroy_widget, calc_lbl)
    
    def OpeningAll(arr, ope_size, x1_in, x2_in, y1_in, y2_in, c, c_v):
        #global undo_str
        #undo_str = 'OpenAll'
        
        global arr_before2
        arr_before2 = arr.copy()
        
        global contr4
        contr4 = 1
        
        ope_size = float(ope_size)
        x1_in = float(x1_in)
        x2_in = float(x2_in)
        y1_in = float(y1_in)
        y2_in = float(y2_in)
        
        if (x1_in >= x2_in) or (y1_in >= y2_in):
            for j in range(len(arr)):
                arr[j] = dip.Opening(arr[j], ope_size)
        else:
            if contr == 'X': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Y': 
                x1_conv = int(np.floor((x1_in-MinY)/dy))
                x2_conv = int(np.floor((x2_in-MinY)/dy))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Z': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinY)/dy))
                y2_conv = int(np.floor((y2_in-MinY)/dy))
                        
            for j in range(len(arr)):
                Corr = np.zeros(np.shape(arr[j, y1_conv:y2_conv, x1_conv:x2_conv]))
                Corr[arr[j, y1_conv:y2_conv, x1_conv:x2_conv] > 0.8] = 1
                Corr_op = dip.Opening(Corr, ope_size)
                arr[j, y1_conv:y2_conv, x1_conv:x2_conv] = Corr_op
    
        calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
        calc_lbl.place(x = 630, y = 220)
    
        ws.after(2000, destroy_widget, calc_lbl)   
        
        if c == 0:
            global Undo_btn
            try:
                Undo_btn.destroy()
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo(arr_before_er, Undo_btn))
                Undo_btn.place(x = 630, y = 400)
            except:
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo(arr_before_er, Undo_btn))
                Undo_btn.place(x = 630, y = 400)
                
        Undo_btn.config(state = "normal")
            
        if c_v == 0:
            vis8_btn = Button(ws, text='Visualize Processing', command = lambda:Vis_track1(tracked, spin_val.get(), contr4, canv_num, c2))
            vis8_btn.place(x = col2_px, y = 430)
            
            global contr_vis
            contr_vis = 1
        
        global c4
        c4 = 1

    def ErosionStep(arr, er_size, num, x1_in, x2_in, y1_in, y2_in, c, c_v):
        global arr_before_er
        arr_before_er = arr.copy()
        global undo_str
        undo_str = 'Erosion'
        
        global contr4
        contr4 = 1
        
        num = int(num)
        er_size = float(er_size)
        
        x1_in = float(x1_in)
        x2_in = float(x2_in)
        y1_in = float(y1_in)
        y2_in = float(y2_in)
        
        if (x1_in >= x2_in) or (y1_in >= y2_in):
            arr[num] = dip.Erosion(arr[num], er_size)
        else:
            if contr == 'X': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Y': 
                x1_conv = int(np.floor((x1_in-MinY)/dy))
                x2_conv = int(np.floor((x2_in-MinY)/dy))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Z': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinY)/dy))
                y2_conv = int(np.floor((y2_in-MinY)/dy))
                
            Corr = np.zeros(np.shape(arr[num, y1_conv:y2_conv, x1_conv:x2_conv]))
            Corr[arr[num, y1_conv:y2_conv, x1_conv:x2_conv] > 0.8] = 1
            Corr_op = dip.Erosion(Corr, er_size)
            arr[num, y1_conv:y2_conv, x1_conv:x2_conv] = Corr_op
    
        Er_lbl = Label(ws, text = 'Done!', foreground = 'green')
        Er_lbl.place(x = 630, y = 310)
        ws.after(2000, destroy_widget, Er_lbl) 
       
        if c == 0:
            global Undo_btn
            try:
                Undo_btn.destroy()
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo(arr_before_er, Undo_btn))
                Undo_btn.place(x = 630, y = 400)
            except:
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo(arr_before_er, Undo_btn))
                Undo_btn.place(x = 630, y = 400)

        Undo_btn.config(state = "normal")               
            
        if c_v == 0:
            vis8_btn = Button(ws, text='Visualize Processing', command = lambda:Vis_track1(tracked, spin_val.get(), contr4, canv_num, c2))
            vis8_btn.place(x = col2_px, y = 430)
            
            global contr_vis
            contr_vis = 1
        
        global c5 
        c5 = 1
        
    def ErosionAll(arr, er_size, x1_in, x2_in, y1_in, y2_in, c, c_v):
        er_size = float(er_size)
        
        global arr_before_er2
        arr_before_er2 = arr.copy()
        global undo_str
        undo_str = 'ErosionAll'
        
        global contr4
        contr4 = 1
        
        x1_in = float(x1_in)
        x2_in = float(x2_in)
        y1_in = float(y1_in)
        y2_in = float(y2_in)
        
        if (x1_in >= x2_in) or (y1_in >= y2_in):
            for j in range(len(arr)):
                arr[j] = dip.Erosion(arr[j], er_size)
        else:
            if contr == 'X': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Y': 
                x1_conv = int(np.floor((x1_in-MinY)/dy))
                x2_conv = int(np.floor((x2_in-MinY)/dy))
                y1_conv = int(np.floor((y1_in-MinZ)/dz))
                y2_conv = int(np.floor((y2_in-MinZ)/dz))
            elif contr == 'Z': 
                x1_conv = int(np.floor((x1_in-MinX)/dx))
                x2_conv = int(np.floor((x2_in-MinX)/dx))
                y1_conv = int(np.floor((y1_in-MinY)/dy))
                y2_conv = int(np.floor((y2_in-MinY)/dy))
            
            for j in range(len(arr)):
                Corr = np.zeros(np.shape(arr[j, y1_conv:y2_conv, x1_conv:x2_conv]))
                Corr[arr[j, y1_conv:y2_conv, x1_conv:x2_conv] > 0.8] = 1
                Corr_op = dip.Erosion(Corr, er_size)
                arr[j, y1_conv:y2_conv, x1_conv:x2_conv] = Corr_op
        
        Er_lbl = Label(ws, text = 'Done!', foreground = 'green')
        Er_lbl.place(x = 630, y = 340)
        ws.after(2000, destroy_widget, Er_lbl) 
    
        if c == 0:
            global Undo_btn
            try:
                Undo_btn.destroy()
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo(arr_before_er, Undo_btn))
                Undo_btn.place(x = 630, y = 400)
            except:
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo(arr_before_er, Undo_btn))
                Undo_btn.place(x = 630, y = 400)

        Undo_btn.config(state = "normal")      
            
        if c_v == 0:
            vis8_btn = Button(ws, text='Visualize Processing', command = lambda:Vis_track1(tracked, spin_val.get(), contr4, canv_num, c2))
            vis8_btn.place(x = col2_px, y = 430)
            
            global contr_vis
            contr_vis = 1
    
        global c6
        c6 = 1
    
    def Fill(arr, c, c_v):
        N = len(arr)
        global arr_before_fill
        arr_before_fill = arr.copy()
        
        global undo_str
        undo_str = 'Fill'
        
        global contr4
        contr4 = 1
 
        for j in range(len(arr)):
            tracked[j] = dip.FillHoles(dip.FixedThreshold(arr[j],0.5))
        
        Fill_lbl = Label(ws, text = 'Done!', foreground = 'green')
        Fill_lbl.place(x = 740, y = 400)
        
        ws.after(2000, destroy_widget, Fill_lbl)    
                
        if c == 0:
            global Undo_btn
            try:
                Undo_btn.destroy()
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo(arr_before_er, Undo_btn))
                Undo_btn.place(x = 630, y = 400)
            except:
                Undo_btn = Button(ws, text = 'Undo Processing', command = lambda:Undo(arr_before_er, Undo_btn))
                Undo_btn.place(x = 630, y = 400)

        Undo_btn.config(state = "normal")
            
        if c_v == 0:
            vis8_btn = Button(ws, text='Visualize Processing', command = lambda:Vis_track1(tracked, spin_val.get(), contr4, canv_num, c2))
            vis8_btn.place(x = col2_px, y = 430)

            global contr_vis
            contr_vis = 1
    
        global c7
        c7 = 1
        
#    def Undo2(arr_before, undo_str):
#        global tracked
#        tracked = arr_before.copy()
#        
#        if undo_str == 'Erosion':
#            calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
#            calc_lbl.place(x = 740, y = 310)
#        elif undo_str == 'ErosionAll':
#            calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
#            calc_lbl.place(x = 740, y = 340)
#        elif undo_str == 'Fill':  
#            calc_lbl = Label(ws, text = 'Done!', foreground = 'green')
#            calc_lbl.place(x = 740, y = 400) 
#        
#        ws.after(2000, destroy_widget, calc_lbl)    
        
    def init_tracking(arr, num, c):
        arr = np.array(arr)
        arr[:,0,0] = 1
        arr[:,-1,0] = 1
        arr[:,0,-1] = 1
        arr[:,-1,-1] = 1
        
        #track backwards in time from this frame on (N-1 = last)
        num = int(num)
        
        labels0, num0 = measure.label(arr[num,:,:], connectivity = 1, return_num = True)
        props0 = measure.regionprops(labels0)
        l0 = len(props0)
        
        global C0, C1, C2, C3
        
        #calculate size of extracted areas
        areas0 = np.zeros(l0)
        for k in range(0,l0):
            areas0[k] = props0[k]["area"]
        
        #calculate index of largest area and track it as feature 0, then do the same after removing area 0, etc.
        index_area0 = np.argmax(areas0)
        C0 = (props0[index_area0]['coords'])
        
        areas1 = areas0.copy()
        areas1[index_area0] = 0
        index_area1 = np.argmax(areas1)
        C1 = (props0[index_area1]['coords'])
        
        areas2 = areas1.copy()
        areas2[index_area1] = 0
        index_area2 = np.argmax(areas2)
        C2 = (props0[index_area2]['coords'])
        
        areas3 = areas2.copy()
        areas3[index_area2] = 0
        index_area3 = np.argmax(areas3)
        C3 = (props0[index_area3]['coords'])
        
        #set the found twist regions to 1 in new binary arrays
        
        global Tw_region0, Tw_region1, Tw_region2, Tw_region3
        Tw_region0 = np.zeros((num+1, np.shape(arr)[1], np.shape(arr)[2]))
        Tw_region1 = np.zeros((num+1, np.shape(arr)[1], np.shape(arr)[2]))
        Tw_region2 = np.zeros((num+1, np.shape(arr)[1], np.shape(arr)[2]))
        Tw_region3 = np.zeros((num+1, np.shape(arr)[1], np.shape(arr)[2]))
        
        Tw_region0[num,C0[0:-1,0],C0[0:-1,1]] = 1
        Tw_region1[num,C1[0:-1,0],C1[0:-1,1]] = 1
        Tw_region2[num,C2[0:-1,0],C2[0:-1,1]] = 1
        Tw_region3[num,C3[0:-1,0],C3[0:-1,1]] = 1
        
        global LastFrame
        LastFrame = [Tw_region0, Tw_region1, Tw_region2, Tw_region3]
        
        init_lbl = Label(ws, text = 'Tracking initialized!', foreground = 'green')
        init_lbl.place(x = 950, y = 70)
        ws.after(2000, destroy_widget, init_lbl)
        
        if c == 0:
            #buttons to visualize last frame
            global shape_lbl
            shape_lbl = Label(ws, text = 'Choose Shape')
            shape_lbl.place(x = col3_px, y = 100)
            global spin6
            spin6 = Spinbox(ws, from_ = 0, to = 3, textvariable = spin6_val, wrap = True, width = wi)
            spin6.place(in_ = shape_lbl, y = 0, relx = spacing)
            global vis4_btn
            vis4_btn = Button(ws, text='Visualize', command = lambda:Vis_Init(contr, LastFrame, spin5_val.get(), spin6_val.get(), canvas, c9))
            vis4_btn.place(in_ = spin6, y = 0, relx = spacing)
        else:
            spin6.destroy()
            spin6 = Spinbox(ws, from_ = 0, to = 3, textvariable = spin6_val, wrap = True, width = wi)
            spin6.place(in_ = shape_lbl, y = 0, relx = spacing)
            vis4_btn.destroy()
            vis4_btn = Button(ws, text='Visualize', command = lambda:Vis_Init(contr, LastFrame, spin5_val.get(), spin6_val.get(), canvas, c9))
            vis4_btn.place(in_ = spin6, y = 0, relx = spacing)
            
        global c8
        c8 = 1

    def Vis_Init(contr, arr, num, num2, canvas, c):
        plt.close()
        canvas.get_tk_widget().destroy()
        num = int(num) #initialization frame
        num2 = int(num2) #Twist region identifier
        fig4 = plt.figure(figsize = (4.5,3.5))
        plot4 = fig4.add_subplot(111)
        if contr == 'X': 
            plot4.imshow(arr[num2][num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinZ, MaxZ])
            plot4.set_title("Initial Shape "+str(num2), fontsize = 8)
            plot4.set_ylabel("Z", fontsize = 9)
            plot4.set_xlabel("X", fontsize = 9)
            plot4.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Y': 
            plot4.imshow(arr[num2][num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinY, MaxY, MinZ, MaxZ])
            plot4.set_title("Initial Shape "+str(num2), fontsize = 8)
            plot4.set_ylabel("Z", fontsize = 9)
            plot4.set_xlabel("Y", fontsize = 9)
            plot4.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Z': 
            plot4.imshow(arr[num2][num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinY, MaxY])
            plot4.set_title("Initial Shape "+str(num2), fontsize = 8)
            plot4.set_ylabel("Y", fontsize = 9)
            plot4.set_xlabel("X", fontsize = 9)
            plot4.tick_params(axis='both', which='major', labelsize=7)
            
        canvas = FigureCanvasTkAgg(fig4, master=ws)
        canvas.draw()
        canvas.get_tk_widget().place(x = 20, y = 100)
        
        if c == 0:
            over_lbl = Label(ws, text = 'Overlap fraction:')
            over_lbl.place(x = col3_px, y = 130)
            Enter_overl = Entry(ws, textvariable = overlap, width = wi)
            Enter_overl.place(in_ = over_lbl, y = 0, relx = spacing)
            global Track_btn
            Track_btn = Button(ws, text = 'Track', command = lambda:Track(tracked, C0, C1, C2, C3, spin5_val.get(), spin6_val.get(), overlap.get(), c13))
            Track_btn.place(x = col3_px, y = 160)
        else:
            Track_btn.destroy()
            Track_btn = Button(ws, text = 'Track', command = lambda:Track(tracked, C0, C1, C2, C3, spin5_val.get(), spin6_val.get(), overlap.get(), c13))
            Track_btn.place(x = col3_px, y = 160) 
            
        global c9 
        c9 = 1

    def Track(GrdTw_Thr, C0, C1, C2, C3, num, num2, overlap, c):
        GrdTw_Thr = np.array(GrdTw_Thr)

        GrdTw_Thr[:,0,0] = 1
        GrdTw_Thr[:,-1,0] = 1
        GrdTw_Thr[:,0,-1] = 1
        GrdTw_Thr[:,-1,-1] = 1
        
        num = int(num) #initialization frame
        num2 = int(num2) #twist region identifier
        overlap = float(overlap)
        Match = np.ones((4,4)) #overlap matrix
        
        #Testmaps for comparison
        Testmap0 = np.zeros(np.shape(Tw_region0[0,:,:]))
        Testmap1 = np.zeros(np.shape(Tw_region0[0,:,:]))
        Testmap2 = np.zeros(np.shape(Tw_region0[0,:,:]))
        Testmap3 = np.zeros(np.shape(Tw_region0[0,:,:]))
        
        for j in range(num, 0, -1):    
            all_labels = measure.label(GrdTw_Thr[j-1,:,:], connectivity = 1, return_num = False)
            props = measure.regionprops(all_labels)
            l1 = len(props)
            
            areas = np.zeros(l1)
            for k in range(0,l1):
                areas[k] = props[k]["area"]
                
            index_area = np.argmax(areas)
            areas[index_area] = 0
            index_area_1 = np.argmax(areas)
            areas[index_area_1] = 0
            index_area_2 = np.argmax(areas)                
            areas[index_area_2] = 0
            index_area_3 = np.argmax(areas)
            
            Testmap0[props[index_area]['coords'][0:-1,0],props[index_area]['coords'][0:-1,1]] = 1
            Testmap1[props[index_area_1]['coords'][0:-1,0],props[index_area_1]['coords'][0:-1,1]] = 1
            Testmap2[props[index_area_2]['coords'][0:-1,0],props[index_area_2]['coords'][0:-1,1]] = 1
            Testmap3[props[index_area_3]['coords'][0:-1,0],props[index_area_3]['coords'][0:-1,1]] = 1
            
            Sum0 = np.add(Testmap0, Tw_region0[j,:,:])
            Sum1 = np.add(Testmap1, Tw_region0[j,:,:])
            Sum2 = np.add(Testmap2, Tw_region0[j,:,:])
            Sum3 = np.add(Testmap3, Tw_region0[j,:,:])
            
            S0 = np.count_nonzero(Sum0 == 2)
            S1 = np.count_nonzero(Sum1 == 2)
            S2 = np.count_nonzero(Sum2 == 2)
            S3 = np.count_nonzero(Sum3 == 2)
            
            Match[0,0] = S0/len(C0)
            Match[1,0] = S1/len(C0)
            Match[2,0] = S2/len(C0)
            Match[3,0] = S3/len(C0)
            
            if Match[0,0] >= overlap:
                C0 = (props[index_area]['coords'])
            elif Match[1,0] >= overlap:
                C0 = (props[index_area_1]['coords'])
            elif Match[2,0] >= overlap:
                C0 = (props[index_area_2]['coords'])
            elif Match[3,0] >= overlap:
                C0 = (props[index_area_3]['coords'])
        
            
            Sum0 = np.add(Testmap0, Tw_region1[j,:,:])
            Sum1 = np.add(Testmap1, Tw_region1[j,:,:])
            Sum2 = np.add(Testmap2, Tw_region1[j,:,:])
            Sum3 = np.add(Testmap3, Tw_region1[j,:,:])
            
            S0 = np.count_nonzero(Sum0 == 2)
            S1 = np.count_nonzero(Sum1 == 2)
            S2 = np.count_nonzero(Sum2 == 2)
            S3 = np.count_nonzero(Sum3 == 2)
            
            Match[0,1] = S0/len(C1)
            Match[1,1] = S1/len(C1)
            Match[2,1] = S2/len(C1)
            Match[3,1] = S3/len(C1)
        
            if Match[0,1] >= overlap:
                C1 = (props[index_area]['coords'])  
            elif Match[1,1] >= overlap:
                C1 = (props[index_area_1]['coords'])   
            elif Match[2,1] >= overlap:
                C1 = (props[index_area_2]['coords'])   
            elif Match[3,1] >= overlap:
                C1 = (props[index_area_3]['coords'])
        
            Sum0 = np.add(Testmap0, Tw_region2[j,:,:])
            Sum1 = np.add(Testmap1, Tw_region2[j,:,:])
            Sum2 = np.add(Testmap2, Tw_region2[j,:,:])
            Sum3 = np.add(Testmap3, Tw_region2[j,:,:])
            
            S0 = np.count_nonzero(Sum0 == 2)
            S1 = np.count_nonzero(Sum1 == 2)
            S2 = np.count_nonzero(Sum2 == 2)
            S3 = np.count_nonzero(Sum3 == 2)
            
            Match[0,2] = S0/len(C2)
            Match[1,2] = S1/len(C2)
            Match[2,2] = S2/len(C2)
            Match[3,2] = S3/len(C2)
        
            if Match[0,2] >= overlap:
                C2 = (props[index_area]['coords'])
            elif Match[1,2] >= overlap:
                C2 = (props[index_area_1]['coords'])    
            elif Match[2,2] >= overlap:
                C2 = (props[index_area_2]['coords'])
            elif Match[3,2] >= overlap:
                C2 = (props[index_area_3]['coords'])
        
            Sum0 = np.add(Testmap0, Tw_region3[j,:,:])
            Sum1 = np.add(Testmap1, Tw_region3[j,:,:])
            Sum2 = np.add(Testmap2, Tw_region3[j,:,:])
            Sum3 = np.add(Testmap3, Tw_region3[j,:,:])
            
            S0 = np.count_nonzero(Sum0 == 2)
            S1 = np.count_nonzero(Sum1 == 2)
            S2 = np.count_nonzero(Sum2 == 2)
            S3 = np.count_nonzero(Sum3 == 2)
            
            Match[0,3] = S0/len(C3)
            Match[1,3] = S1/len(C3)
            Match[2,3] = S2/len(C3)
            Match[3,3] = S3/len(C3)
        
            if Match[0,3] >= overlap:
                C3 = (props[index_area]['coords'])
            elif Match[1,3] >= overlap:
                C3 = (props[index_area_1]['coords'])    
            elif Match[2,3] >= overlap:
                C3 = (props[index_area_2]['coords'])   
            elif Match[3,3] >= overlap:
                C3 = (props[index_area_3]['coords'])
            
            Tw_region0[j-1,C0[0:-1,0],C0[0:-1,1]] = 1
            Tw_region1[j-1,C1[0:-1,0],C1[0:-1,1]] = 1
            Tw_region2[j-1,C2[0:-1,0],C2[0:-1,1]] = 1
            Tw_region3[j-1,C3[0:-1,0],C3[0:-1,1]] = 1
            
            Testmap0 = np.zeros(np.shape(Tw_region0[0,:,:]))
            Testmap1 = np.zeros(np.shape(Tw_region0[0,:,:]))
            Testmap2 = np.zeros(np.shape(Tw_region0[0,:,:]))
            Testmap3 = np.zeros(np.shape(Tw_region0[0,:,:]))
            
        global retracked
        retracked = LastFrame[num2]
        
        global contr4
        contr4 = 2
        
        track_lbl = Label(ws, text = 'Tracking completed!', foreground = 'green')
        track_lbl.place(x = 1020, y = 160)
        ws.after(2000, destroy_widget, track_lbl) 

        if c == 0:
            global vis5_btn
            vis5_btn = Button(ws, text = 'Visualize Tracking', command = lambda:Vis_track1(retracked, spin_val.get(), contr4, canvas, c2))
            vis5_btn.place(in_ = Track_btn, y = 0, relx = spacing)
        else:
            vis5_btn.destroy()
            vis5_btn = Button(ws, text = 'Visualize Tracking', command = lambda:Vis_track1(retracked, spin_val.get(), contr4, canvas, c2))
            vis5_btn.place(in_ = Track_btn, y = 0, relx = spacing)
            
        global c13
        c13 = 1

    def savefunc(contr, arr, filenames):
        #add option that it creates a separate folder for the images
        plotws = tki.Toplevel(ws)
        plotws.title("Plot Specifications")
        plotws.geometry(str(horsz_plotws)+'x640')
        plotws.grab_set()
        
        #Set colormap:
        global cmap_to_use
        cmap_to_use = "gray"
        
        def set_colormap(boxon):
            if boxon % 2 == 1:
                listbox3.config(state = "normal")
            else:
                listbox3.config(state = "disabled")

        def_colormap = tki.IntVar(value = 0)
        check_default_colormap = Checkbutton(plotws, text = "Customize", variable = def_colormap, command = lambda:set_colormap(def_colormap.get()))        
        check_default_colormap.place(x = 10, y = 90)
        
        #cmap_to_use = tki.StringVar(value = '')
        listbox3 = tki.Listbox(plotws, height=7, width = 25, selectmode=tki.SINGLE, exportselection=False)
        
        for j in range(len(cmaps)):
            listbox3.insert(tki.END, cmaps[j])
        listbox3.place(x = 120, y = 35)
        listbox3.config(state = "disabled")
        
        colormap_lbl = Label(plotws, text = 'Choose Colormap:')    
        colormap_lbl.place(x = 120, y = 10)   
        
        def color_selected(event):
            global cmap_to_use
            cmap_to_use = cmaps[int(listbox3.curselection()[0])]
            #print("I was here")
    
        listbox3.bind('<<ListboxSelect>>', color_selected)
        
        #Set figure size:
        def_figsize = tki.IntVar(value = 0)
        check_default_figsize = Checkbutton(plotws, text = "Customize", variable = def_figsize, command = lambda:set_figsize(def_figsize.get()))        
        check_default_figsize.place(x = 10, y = 180)   
        
        Label(plotws, text='Choose Figure Size:').place(x = 120, y = 180)
        
        figure_x = tki.StringVar(value = "12")
        figure_y = tki.StringVar(value = "12")
        
        xfig = Label(plotws, text = 'x =')
        xfig.place(x = 120, y = 210)
        Enter_figx = Entry(plotws, textvariable = figure_x, width = 4)
        Enter_figx.place(in_ = xfig, y = 0, relx = spacing)
        yfig = Label(plotws, text = 'y =')
        yfig.place(in_ = Enter_figx, y = 0, relx = spacing)
        Enter_figy = Entry(plotws, textvariable = figure_y, width = 4)
        Enter_figy.place(in_ = yfig, y = 0, relx = spacing)
        
        Enter_figx.config(state = "disabled")
        Enter_figy.config(state = "disabled")
        
        def set_figsize(boxon):
            if boxon % 2 == 1:
                Enter_figx.config(state = "normal")
                Enter_figy.config(state = "normal")
            else:
                Enter_figx.config(state = "disabled")
                Enter_figy.config(state = "disabled")  
        
        #Set title:
        def_title = tki.IntVar(value = 0)
        check_default_title = Checkbutton(plotws, text = "Customize", variable = def_title, command = lambda:set_plottitle(def_title.get()))        
        check_default_title.place(x = 10, y = 240)   
        
        Label(plotws, text='Choose Figure Title:').place(x = 120, y = 240)
        
        figure_title = tki.StringVar(value = "")
        text_title = Text(plotws, height = 1, width = 20)
        text_title.place(x = 120, y = 270)        
        text_title.config(state = "disabled")
        
        def set_plottitle(boxon):
            if boxon % 2 == 1:
                text_title.config(state = "normal")
            else:
                text_title.config(state = "disabled")
        
        #Set titlesize 
        def_titlesize = tki.IntVar(value = 0)
        check_default_titlesize = Checkbutton(plotws, text = "Customize", variable = def_titlesize, command = lambda:set_titlesize(def_titlesize.get()))        
        check_default_titlesize.place(x = 10, y = 300)   
        
        Label(plotws, text='Choose Title Size:').place(x = 120, y = 300)
        
        titlesize = tki.StringVar(value = "14")
        Enter_titlesize = Entry(plotws, textvariable = titlesize, width = 6)
        Enter_titlesize.place(x = 120, y = 330)       
        Enter_titlesize.config(state = "disabled")
        
        def set_titlesize(boxon):
            if boxon % 2 == 1:
                Enter_titlesize.config(state = "normal")
            else:
                Enter_titlesize.config(state = "disabled")
        
        #Set ticksize 
        def_ticksize = tki.IntVar(value = 0)
        check_default_ticksize = Checkbutton(plotws, text = "Customize", variable = def_ticksize, command = lambda:set_ticksize(def_ticksize.get()))        
        check_default_ticksize.place(x = 10, y = 360)   
        
        Label(plotws, text='Choose Ticksize:').place(x = 120, y = 360)
        
        ticksize = tki.StringVar(value = "14")
        Enter_ticksize = Entry(plotws, textvariable = ticksize, width = 6)
        Enter_ticksize.place(x = 120, y = 390)       
        Enter_ticksize.config(state = "disabled")
        
        def set_ticksize(boxon):
            if boxon % 2 == 1:
                Enter_ticksize.config(state = "normal")
            else:
                Enter_ticksize.config(state = "disabled")

        #Set label
        def_label = tki.IntVar(value = 0)
        check_default_label = Checkbutton(plotws, text = "Customize", variable = def_label, command = lambda:set_label(def_label.get()))        
        check_default_label.place(x = 10, y = 420)   
        
        Label(plotws, text='Choose Labels:').place(x = 120, y = 420)
        
        label_x = tki.StringVar(value = "")
        label_y = tki.StringVar(value = "")
        
        axx_lbl = Label(plotws, text = 'x =')
        axx_lbl.place(x = 120, y = 450)
        Enter_labelx = Entry(plotws, textvariable = label_x, width = 6)
        Enter_labelx.place(in_ = axx_lbl, y = 0, relx = spacing)
        axy_lbl = Label(plotws, text = 'y =')
        axy_lbl.place(in_ = Enter_labelx, y = 0, relx = spacing)
        Enter_labely = Entry(plotws, textvariable = label_y, width = 6)
        Enter_labely.place(in_ = axy_lbl, y = 0, relx = spacing)
        
        Enter_labelx.config(state = "disabled")
        Enter_labely.config(state = "disabled")
        
        def set_label(boxon):
            if boxon % 2 == 1:
                Enter_labelx.config(state = "normal")
                Enter_labely.config(state = "normal")
            else:
                Enter_labelx.config(state = "disabled")
                Enter_labely.config(state = "disabled")
                
        #Set labelsize      
        def_labelsize = tki.IntVar(value = 0)
        check_default_labelsize = Checkbutton(plotws, text = "Customize", variable = def_labelsize, command = lambda:set_labelsize(def_labelsize.get()))        
        check_default_labelsize.place(x = 10, y = 480)   
        
        Label(plotws, text='Choose Labelsize:').place(x = 120, y = 480)
        
        labelsize = tki.StringVar(value = "14")
        Enter_labelsize = Entry(plotws, textvariable = labelsize, width = 6)
        Enter_labelsize.place(x = 120, y = 510)       
        Enter_labelsize.config(state = "disabled")
        
        def set_labelsize(boxon):
            if boxon % 2 == 1:
                Enter_labelsize.config(state = "normal")
            else:
                Enter_labelsize.config(state = "disabled")
        
        #Set vmin/vmax
        def_minmax = tki.IntVar(value = 0)
        check_default_minmax = Checkbutton(plotws, text = "Customize", variable = def_minmax, command = lambda:set_minmax(def_minmax.get()))        
        check_default_minmax.place(x = 10, y = 540)   
        
        Label(plotws, text='Choose Colormap Limits:').place(x = 120, y = 540)
        
        vmin = tki.IntVar(value = 0)
        vmax = tki.IntVar(value = 1.5)
        
        vmin_lbl = Label(plotws, text = 'vmin =')
        vmin_lbl.place(x = 120, y = 570)
        Enter_vmin = Entry(plotws, textvariable = vmin, width = 4)
        Enter_vmin.place(in_ = vmin_lbl, y = 0, relx = spacing)
        vmax_lbl = Label(plotws, text = 'vmax =')
        vmax_lbl.place(in_ = Enter_vmin, y = 0, relx = spacing)
        Enter_vmax = Entry(plotws, textvariable = vmax, width = 4)
        Enter_vmax.place(in_ = vmax_lbl, y = 0, relx = spacing)
        
        Enter_vmin.config(state = "disabled")
        Enter_vmax.config(state = "disabled")
        
        def set_minmax(boxon):
            if boxon % 2 == 1:
                Enter_vmin.config(state = "normal")
                Enter_vmax.config(state = "normal")
            else:
                Enter_vmin.config(state = "disabled")
                Enter_vmax.config(state = "disabled")
        
        conf_btn3 = Button(plotws, text='Confirm', command = lambda:destroy_widget_2(plotws, def_colormap.get(), def_figsize.get(), def_title.get(), \
        def_titlesize.get(), def_ticksize.get(), def_label.get(), def_labelsize.get(), def_minmax.get(), figure_x.get(), figure_y.get(), text_title.get('1.0','end-1c'), titlesize.get(), \
        ticksize.get(), label_x.get(), label_y.get(), labelsize.get(), vmin.get(), vmax.get(), cmap_to_use))
        
        conf_btn3.place(x = 120, y = 605)

        def destroy_widget_2(widget, boxon1, boxon2, boxon3, boxon4, boxon5, boxon6, boxon7, boxon8, figx, figy, title_name, titlesize, ticksize, labelx, labely,\
        labelsize, vmin, vmax, cmap_to_use):
            #add option that it creates a separate folder for the images
            #print(cmap_to_use)
            #if not customized, use default settings:
            
            if boxon1 % 2 == 0:
                cmap_to_use = "RdBu_r"
                
            if boxon2 % 2 == 0:
                figx = dim[1]/50
                figy = dim[0]/50
            else:
                figx = int(figx)
                figy = int(figy)
            
            if boxon4 % 2 == 0:
                titlesize = 14
            else:
                titlesize = int(titlesize)

            if boxon5 % 2 == 0:
                ticksize = 14
            else:
                ticksize = int(ticksize)

            if boxon7 % 2 == 0:
                labelsize = 14
            else:
                labelsize = int(labelsize)
                
            L = len(arr)
            for j in range(L):
                fig = Figure(figsize=(figx, figy))
                plot1 = fig.add_subplot(111)
                if contr == 'X': 
                    if boxon8 % 2 == 0:
                        plot1.imshow(arr[j], origin = "lower", cmap = cmap_to_use, vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinZ, MaxZ])
                    else:
                        plot1.imshow(arr[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinZ, MaxZ])
                    if boxon3 % 2 == 0:
                        plot1.set_title("Processed Shape, Frame "+str(j), fontsize = titlesize)
                    else: 
                        plot1.set_title(title_name, fontsize = titlesize)
                    if boxon6 % 2 == 0:                            
                        plot1.set_ylabel("y", fontsize = labelsize)
                        plot1.set_xlabel("x", fontsize = labelsize)
                    else: 
                        plot1.set_ylabel(labely, fontsize = labelsize)
                        plot1.set_xlabel(labelx, fontsize = labelsize)                             
                    plot1.tick_params(axis='both', which='major', labelsize = ticksize)
                    fig.savefig(filenames+str(j)+'.png')
                elif contr == 'Y': 
                    if boxon8 % 2 == 0:
                        plot1.imshow(arr[j], origin = "lower", cmap = cmap_to_use, vmin = 0, vmax = 1.5, extent = [MinY, MaxY, MinZ, MaxZ])
                    else:
                        plot1.imshow(arr[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinY, MaxY, MinZ, MaxZ])
                    if boxon3 % 2 == 0:
                        plot1.set_title("Processed Shape, Frame "+str(j), fontsize = titlesize)
                    else: 
                        plot1.set_title(title_name, fontsize = titlesize)
                    if boxon6 % 2 == 0:                            
                        plot1.set_ylabel("y", fontsize = labelsize)
                        plot1.set_xlabel("x", fontsize = labelsize)
                    else: 
                        plot1.set_ylabel(labely, fontsize = labelsize)
                        plot1.set_xlabel(labelx, fontsize = labelsize)                             
                    plot1.tick_params(axis='both', which='major', labelsize = ticksize)
                    fig.savefig(filenames+str(j)+'.png')
                elif contr == 'Z': 
                    if boxon8 % 2 == 0:
                        plot1.imshow(arr[j], origin = "lower", cmap = cmap_to_use, vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinY, MaxY])
                    else:
                        plot1.imshow(arr[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinY, MaxY])
                    if boxon3 % 2 == 0:
                        plot1.set_title("Processed Shape, Frame "+str(j), fontsize = titlesize)
                    else: 
                        plot1.set_title(title_name, fontsize = titlesize)
                    if boxon6 % 2 == 0:                            
                        plot1.set_ylabel("y", fontsize = labelsize)
                        plot1.set_xlabel("x", fontsize = labelsize)
                    else: 
                        plot1.set_ylabel(labely, fontsize = labelsize)
                        plot1.set_xlabel(labelx, fontsize = labelsize)                             
                    plot1.tick_params(axis='both', which='major', labelsize = ticksize)
                    fig.savefig(filenames+str(j)+'.png')
                    
            save_lbl = Label(ws, text = 'Saved!', foreground = 'green')
            save_lbl.place(x = saved_px, y = 220)
            
            ws.after(2000, destroy_widget, save_lbl)
            plotws.destroy()
                
    def savearr(arr, filename):
        L = len(arr)
        
        if contr == 'X':
            x_vec = np.linspace(MinX, MaxX, dim[1])
            z_vec = np.linspace(MinZ, MaxZ, dim[0])
            np.savez(filename+".npz", data = arr, x = x_vec, y = [yy], z = z_vec)
        elif contr == 'Y':
            y_vec = np.linspace(MinY, MaxY, dim[1])
            z_vec = np.linspace(MinZ, MaxZ, dim[0])
            np.savez(filename+".npz", data = arr, x = [xx], y = y_vec, z = z_vec)
        elif contr == 'Z':
            x_vec = np.linspace(MinX, MaxX, dim[1])
            y_vec = np.linspace(MinY, MaxY, dim[0])
            np.savez(filename+".npz", data = arr, x = x_vec, y = y_vec, z = [zz])
            
        save_lbl = Label(ws, text = 'Saved!', foreground = 'green')  
        save_lbl.place(x = saved_px, y = 250) 

        ws.after(2000, destroy_widget, save_lbl)

    def saveanim_final(arr, filename, contr):
        plotws = tki.Toplevel(ws)
        plotws.title("Plot Specifications")
        plotws.geometry(str(horsz_plotws)+'x640')
        plotws.grab_set()
        
        #Set colormap:
        global cmap_to_use
        cmap_to_use = "RdBu_r"
        
        def set_colormap(boxon):
            if boxon % 2 == 1:
                listbox3.config(state = "normal")
            else:
                listbox3.config(state = "disabled")

        def_colormap = tki.IntVar(value = 0)
        check_default_colormap = Checkbutton(plotws, text = "Customize", variable = def_colormap, command = lambda:set_colormap(def_colormap.get()))        
        check_default_colormap.place(x = 10, y = 90)
        
        #cmap_to_use = tki.StringVar(value = '')
        listbox3 = tki.Listbox(plotws, height=7, width = 25, selectmode=tki.SINGLE, exportselection=False)
        
        for j in range(len(cmaps)):
            listbox3.insert(tki.END, cmaps[j])
        listbox3.place(x = 120, y = 35)
        listbox3.config(state = "disabled")
        
        colormap_lbl = Label(plotws, text = 'Choose Colormap:')    
        colormap_lbl.place(x = 120, y = 10)   
        
        def color_selected(event):
            global cmap_to_use
            cmap_to_use = cmaps[int(listbox3.curselection()[0])]
    
        listbox3.bind('<<ListboxSelect>>', color_selected)
        
        #Set figure size:
        def_figsize = tki.IntVar(value = 0)
        check_default_figsize = Checkbutton(plotws, text = "Customize", variable = def_figsize, command = lambda:set_figsize(def_figsize.get()))        
        check_default_figsize.place(x = 10, y = 180)   
        
        Label(plotws, text='Choose Figure Size:').place(x = 120, y = 180)
        
        figure_x = tki.StringVar(value = "12")
        figure_y = tki.StringVar(value = "12")
        
        xfig = Label(plotws, text = 'x =')
        xfig.place(x = 120, y = 210)
        Enter_figx = Entry(plotws, textvariable = figure_x, width = 4)
        Enter_figx.place(in_ = xfig, y = 0, relx = spacing)
        yfig = Label(plotws, text = 'y =')
        yfig.place(in_ = Enter_figx, y = 0, relx = spacing)
        Enter_figy = Entry(plotws, textvariable = figure_y, width = 4)
        Enter_figy.place(in_ = yfig, y = 0, relx = spacing)
        
        Enter_figx.config(state = "disabled")
        Enter_figy.config(state = "disabled")
        
        def set_figsize(boxon):
            if boxon % 2 == 1:
                Enter_figx.config(state = "normal")
                Enter_figy.config(state = "normal")
            else:
                Enter_figx.config(state = "disabled")
                Enter_figy.config(state = "disabled")  
        
        #Set title:
        def_title = tki.IntVar(value = 0)
        check_default_title = Checkbutton(plotws, text = "Customize", variable = def_title, command = lambda:set_plottitle(def_title.get()))        
        check_default_title.place(x = 10, y = 240)   
        
        Label(plotws, text='Choose Figure Title:').place(x = 120, y = 240)
        
        figure_title = tki.StringVar(value = "")
        text_title = Text(plotws, height = 1, width = 20)
        text_title.place(x = 120, y = 270)        
        text_title.config(state = "disabled")
        
        def set_plottitle(boxon):
            if boxon % 2 == 1:
                text_title.config(state = "normal")
            else:
                text_title.config(state = "disabled")
        
        #Set titlesize 
        def_titlesize = tki.IntVar(value = 0)
        check_default_titlesize = Checkbutton(plotws, text = "Customize", variable = def_titlesize, command = lambda:set_titlesize(def_titlesize.get()))        
        check_default_titlesize.place(x = 10, y = 300)   
        
        Label(plotws, text='Choose Title Size:').place(x = 120, y = 300)
        
        titlesize = tki.StringVar(value = "14")
        Enter_titlesize = Entry(plotws, textvariable = titlesize, width = 6)
        Enter_titlesize.place(x = 120, y = 330)       
        Enter_titlesize.config(state = "disabled")
        
        def set_titlesize(boxon):
            if boxon % 2 == 1:
                Enter_titlesize.config(state = "normal")
            else:
                Enter_titlesize.config(state = "disabled")
        
        #Set ticksize 
        def_ticksize = tki.IntVar(value = 0)
        check_default_ticksize = Checkbutton(plotws, text = "Customize", variable = def_ticksize, command = lambda:set_ticksize(def_ticksize.get()))        
        check_default_ticksize.place(x = 10, y = 360)   
        
        Label(plotws, text='Choose Ticksize:').place(x = 120, y = 360)
        
        ticksize = tki.StringVar(value = "14")
        Enter_ticksize = Entry(plotws, textvariable = ticksize, width = 6)
        Enter_ticksize.place(x = 120, y = 390)       
        Enter_ticksize.config(state = "disabled")
        
        def set_ticksize(boxon):
            if boxon % 2 == 1:
                Enter_ticksize.config(state = "normal")
            else:
                Enter_ticksize.config(state = "disabled")

        #Set label
        def_label = tki.IntVar(value = 0)
        check_default_label = Checkbutton(plotws, text = "Customize", variable = def_label, command = lambda:set_label(def_label.get()))        
        check_default_label.place(x = 10, y = 420)   
        
        Label(plotws, text='Choose Labels:').place(x = 120, y = 420)
        
        label_x = tki.StringVar(value = "")
        label_y = tki.StringVar(value = "")
        
        axx_lbl = Label(plotws, text = 'x =')
        axx_lbl.place(x = 120, y = 450)
        Enter_labelx = Entry(plotws, textvariable = label_x, width = 6)
        Enter_labelx.place(in_ = axx_lbl, y = 0, relx = spacing)
        axy_lbl = Label(plotws, text = 'y =')
        axy_lbl.place(in_ = Enter_labelx, y = 0, relx = spacing)
        Enter_labely = Entry(plotws, textvariable = label_y, width = 6)
        Enter_labely.place(in_ = axy_lbl, y = 0, relx = spacing)
        
        Enter_labelx.config(state = "disabled")
        Enter_labely.config(state = "disabled")
        
        def set_label(boxon):
            if boxon % 2 == 1:
                Enter_labelx.config(state = "normal")
                Enter_labely.config(state = "normal")
            else:
                Enter_labelx.config(state = "disabled")
                Enter_labely.config(state = "disabled")
                
        #Set labelsize      
        def_labelsize = tki.IntVar(value = 0)
        check_default_labelsize = Checkbutton(plotws, text = "Customize", variable = def_labelsize, command = lambda:set_labelsize(def_labelsize.get()))        
        check_default_labelsize.place(x = 10, y = 480)   
        
        Label(plotws, text='Choose Labelsize:').place(x = 120, y = 480)
        
        labelsize = tki.StringVar(value = "14")
        Enter_labelsize = Entry(plotws, textvariable = labelsize, width = 6)
        Enter_labelsize.place(x = 120, y = 510)       
        Enter_labelsize.config(state = "disabled")
        
        def set_labelsize(boxon):
            if boxon % 2 == 1:
                Enter_labelsize.config(state = "normal")
            else:
                Enter_labelsize.config(state = "disabled")
        
        #Set vmin/vmax
        def_minmax = tki.IntVar(value = 0)
        check_default_minmax = Checkbutton(plotws, text = "Customize", variable = def_minmax, command = lambda:set_minmax(def_minmax.get()))        
        check_default_minmax.place(x = 10, y = 540)   
        
        Label(plotws, text='Choose Colormap Limits:').place(x = 120, y = 540)
        
        vmin = tki.IntVar(value = -5)
        vmax = tki.IntVar(value = 5)
        
        vmin_lbl = Label(plotws, text = 'vmin =')
        vmin_lbl.place(x = 120, y = 570)
        Enter_vmin = Entry(plotws, textvariable = vmin, width = 4)
        Enter_vmin.place(in_ = vmin_lbl, y = 0, relx = spacing)
        vmax_lbl = Label(plotws, text = 'vmax =')
        vmax_lbl.place(in_ = Enter_vmin, y = 0, relx = spacing)
        Enter_vmax = Entry(plotws, textvariable = vmax, width = 4)
        Enter_vmax.place(in_ = vmax_lbl, y = 0, relx = spacing)
        
        Enter_vmin.config(state = "disabled")
        Enter_vmax.config(state = "disabled")
        
        def set_minmax(boxon):
            if boxon % 2 == 1:
                Enter_vmin.config(state = "normal")
                Enter_vmax.config(state = "normal")
            else:
                Enter_vmin.config(state = "disabled")
                Enter_vmax.config(state = "disabled")
        
        conf_btn3 = Button(plotws, text='Confirm', command = lambda:destroy_widget_3(plotws, def_colormap.get(), def_figsize.get(), def_title.get(), \
        def_titlesize.get(), def_ticksize.get(), def_label.get(), def_labelsize.get(), def_minmax.get(), figure_x.get(), figure_y.get(), text_title.get('1.0','end-1c'), titlesize.get(), \
        ticksize.get(), label_x.get(), label_y.get(), labelsize.get(), vmin.get(), vmax.get(), cmap_to_use))
        
        conf_btn3.place(x = 120, y = 605)
        
        def destroy_widget_3(widget, boxon1, boxon2, boxon3, boxon4, boxon5, boxon6, boxon7, boxon8, figx, figy, title_name, titlesize, ticksize, labelx, labely,\
        labelsize, vmin, vmax, cmap_to_use):

            L = len(arr)
            if boxon1 % 2 == 0:
                cmap_to_use = "gray"
                
            if boxon2 % 2 == 0:
                figx = dim[1]/50
                figy = dim[0]/50
            else:
                figx = int(figx)
                figy = int(figy)
            
            if boxon4 % 2 == 0:
                titlesize = 14
            else:
                titlesize = int(titlesize)

            if boxon5 % 2 == 0:
                ticksize = 14
            else:
                ticksize = int(ticksize)

            if boxon7 % 2 == 0:
                labelsize = 14
            else:
                labelsize = int(labelsize)
            
            if boxon8 % 2 == 0:
                vmin = 0
                vmax = 1.5
            else:
                vmin = float(vmin)
                vmax = float(vmax)
        
            fig_anim = plt.figure(figsize=(figx, figy))
            if contr == 'X':
                ax_anim = plt.axes(xlim=(MinX, MaxX), ylim=(MinZ, MaxZ))
                nanarray = np.empty((dim[1], dim[0]))
                nanarray[:] = np.nan
                im = plt.imshow(nanarray, origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinZ, MaxZ])
                if boxon3 % 2 == 0:
                    ax_anim.set_title("Processed Shape", fontsize = titlesize)
                else: 
                    ax_anim.set_title(title_name, fontsize = titlesize)
                if boxon6 % 2 == 0:
                    ax_anim.set_ylabel("y", fontsize = labelsize)
                    ax_anim.set_xlabel("x", fontsize = labelsize)
                else: 
                    ax_anim.set_ylabel(labely, fontsize = labelsize)
                    ax_anim.set_xlabel(labelx, fontsize = labelsize) 
                ax_anim.tick_params(labelsize = ticksize)
            elif contr == 'Y': 
                ax_anim = plt.axes(xlim=(MinY, MaxY), ylim=(MinZ, MaxZ))
                nanarray = np.empty((dim[1], dim[0]))
                nanarray[:] = np.nan
                im = plt.imshow(nanarray, origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinY, MaxY, MinZ, MaxZ])
                if boxon6 % 2 == 0:
                    ax_anim.set_ylabel("y", fontsize = labelsize)
                    ax_anim.set_xlabel("x", fontsize = labelsize)
                else: 
                    ax_anim.set_ylabel(labely, fontsize = labelsize)
                    ax_anim.set_xlabel(labelx, fontsize = labelsize)
                if boxon3 % 2 == 0:
                    ax_anim.set_title("Processed Shape", fontsize = titlesize)
                else: 
                    ax_anim.set_title(title_name, fontsize = titlesize) 
                ax_anim.tick_params(labelsize = ticksize)
            elif contr == 'Z': 
                ax_anim = plt.axes(xlim=(MinX, MaxX), ylim=(MinY, MaxY))
                nanarray = np.empty((dim[1], dim[0]))
                nanarray[:] = np.nan
                im = plt.imshow(nanarray, origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinY, MaxY])
                if boxon6 % 2 == 0:
                    ax_anim.set_ylabel("y", fontsize = labelsize)
                    ax_anim.set_xlabel("x", fontsize = labelsize)
                else: 
                    ax_anim.set_ylabel(labely, fontsize = labelsize)
                    ax_anim.set_xlabel(labelx, fontsize = labelsize)
                if boxon3 % 2 == 0:
                    ax_anim.set_title("Processed Shape", fontsize = titlesize)
                else: 
                    ax_anim.set_title(title_name, fontsize = titlesize) 
                ax_anim.tick_params(labelsize = ticksize)
                
            def init():
                im.set_data(nanarray)
                #plt.axis('off')
                return [im]
        
            def animate(j):
                im.set_array(arr[j])
                #plt.axis('off')
                return [im]
        
            anim = FuncAnimation(fig_anim, animate, init_func=init,
                                    frames=L, interval=120, blit=True)
        
            anim.save(filename+'.gif', writer='imagemagick')
            
            plt.close()
        
            save_lbl = Label(ws, text = 'Saved!', foreground = 'green')    
            save_lbl.place(x = saved_px, y = 280)
        
            ws.after(2000, destroy_widget, save_lbl)
            plotws.destroy()
       
    def create_grid(arr, steps, contr, c):
        Nsteps_x = int(steps)
        
        if contr == "X":
            dx_new = (MaxX-MinX)/Nsteps_x
            Nsteps_y = (MaxZ-MinZ)/dx_new  
            x_axis = np.linspace(0, dim[1], Nsteps_x)
            y_axis = np.linspace(0, dim[0], int(Nsteps_y))        
        elif contr == 'Y':
            dx_new = (MaxY-MinY)/Nsteps_x
            Nsteps_y = (MaxZ-MinZ)/dx_new    
            x_axis = np.linspace(0, dim[1], Nsteps_x)
            y_axis = np.linspace(0, dim[0], int(Nsteps_y))
        elif contr == 'Z':
            dx_new = (MaxX-MinX)/Nsteps_x
            Nsteps_y = (MaxY-MinY)/dx_new    
            x_axis = np.linspace(0, dim[1], Nsteps_x)
            y_axis = np.linspace(0, dim[0], int(Nsteps_y))
            
        Grid = np.meshgrid(x_axis, y_axis)
        
        global full_coords
        full_coords = []
        
        for n_ind in range(len(arr)):    
            Tw10 = arr[n_ind,:,:].astype(np.uint8)
            ret, bin_10 = cv2.threshold(Tw10, 0.5, 255, cv2.THRESH_BINARY)
            
            cont_10, hierachy = cv2.findContours(bin_10, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    
            img_contours = np.zeros(bin_10.shape)
            cv2.drawContours(img_contours, cont_10, -1, (255,0,0), 2)
            
            lencont = []
            new_coords = []
            for j in range(len(Grid[0][0])):
                    for k in range(len(Grid[1])):
                        dist2 = []
                        for m in range(len(cont_10)):
                            lencont.append(len(cont_10[m]))
                        maxlen = max(lencont)
                        for m in range(len(cont_10)):
                            if lencont[m] == maxlen:
                                dist = cv2.pointPolygonTest(cont_10[m], tuple([Grid[0][0][j], Grid[1][k][0]]), False)
                            else:
                                dist2.append(cv2.pointPolygonTest(cont_10[m], tuple([Grid[0][0][j], Grid[1][k][0]]), False))                                
                        if dist > 0:
                            fail = 0
                            for l in range(len(dist2)):
                                if dist2[l] > 0:
                                    fail = 1
                            if fail == 0:
                                new_coords.append([Grid[0][0][j], Grid[1][k][0]])
            
            full_coords.append(new_coords)
        
        grid_lbl = Label(ws, text = 'Grid created!', foreground = 'green')    
        grid_lbl.place(x = 920, y = 400)
        
        ws.after(2000, destroy_widget, grid_lbl)
        
        if c == 0:
            global PhysCoord_btn
            global base_name7
            PhysCoord_btn = Button(ws, text = 'Get Coordinates', command = lambda:get_phys_coords(full_coords, contr, base_name7.get('1.0','end-1c')))
            PhysCoord_btn.place(x = col3_px, y = 430)
            base_name7 = Text(ws, height = 1, width = 30)
            base_name7.place(in_ = PhysCoord_btn, y = 0, relx = spacing)
        else:
            PhysCoord_btn.destroy()
            base_name7.destroy()
            PhysCoord_btn = Button(ws, text = 'Get Coordinates', command = lambda:get_phys_coords(full_coords, contr, base_name7.get('1.0','end-1c')))
            PhysCoord_btn.place(x = col3_px, y = 430)            
            base_name7 = Text(ws, height = 1, width = 30)
            base_name7.place(in_ = PhysCoord_btn, y = 0, relx = spacing)
            
        global c11
        c11 = 1
        
    def get_phys_coords(full_coords, contr, name):
        global phys_coords
        phys_coords = full_coords.copy()
        if contr == 'X':
            for j in range(len(full_coords)):
                savedcoords = []
                for k in range(len(full_coords[j])):
                    phys_coords[j][k][0] = MinX+dx*full_coords[j][k][0]
                    phys_coords[j][k][1] = MinZ+dz*full_coords[j][k][1]
                    savedcoords.append((float(phys_coords[j][k][0]),float(yy),float(phys_coords[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords)
        elif contr == 'Y':
            for j in range(len(full_coords)):
                savedcoords = []
                for k in range(len(full_coords[j])):           
                    phys_coords[j][k][0] = MinY+dy*full_coords[j][k][0]
                    phys_coords[j][k][1] = MinZ+dz*full_coords[j][k][1]
                    savedcoords.append((float(xx),float(phys_coords[j][k][0]),float(phys_coords[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords)
        elif contr == 'Z':
            for j in range(len(full_coords)):
                savedcoords = []
                for k in range(len(full_coords[j])):           
                    phys_coords[j][k][0] = MinX+dx*full_coords[j][k][0]
                    phys_coords[j][k][1] = MinY+dy*full_coords[j][k][1]
                    savedcoords.append((float(phys_coords[j][k][0]),float(phys_coords[j][k][1]), float(zz)))
                np.savetxt(name+str(j)+".txt", savedcoords)
                
        coord_lbl = Label(ws, text = 'Coordinates saved!', foreground = 'green')    
        coord_lbl.place(x = col3_px, y = 460)
        
        ws.after(2000, destroy_widget, coord_lbl)
        
    def create_random(arr, steps, contr, c): 
        num_points = int(steps)**2        

        random_x = np.random.randint(dim[1], size = (len(arr), num_points))
        random_y = np.random.randint(dim[0], size = (len(arr), num_points))        

        global full_coords2
        full_coords2 = []
        
        for n_ind in range(len(arr)):    
            Tw10 = arr[n_ind,:,:].astype(np.uint8)
            ret, bin_10 = cv2.threshold(Tw10, 0.5, 255, cv2.THRESH_BINARY)
            
            cont_10, hierachy = cv2.findContours(bin_10, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    
            img_contours = np.zeros(bin_10.shape)
            cv2.drawContours(img_contours, cont_10, -1, (255,0,0), 2)
            
            lencont = []
            new_coords2 = []
            
            for j in range(num_points):
                dist2 = []
                for m in range(len(cont_10)):
                    lencont.append(len(cont_10[m]))
                maxlen = max(lencont)
                for m in range(len(cont_10)):
                    if lencont[m] == maxlen:
                        dist = cv2.pointPolygonTest(cont_10[m], tuple([float(random_x[n_ind, j]), float(random_y[n_ind, j])]), False)                
                    else:
                        dist2.append(cv2.pointPolygonTest(cont_10[m], tuple([float(random_x[n_ind, j]), float(random_y[n_ind, j])]), False))
                if dist > 0:
                    fail = 0
                    for l in range(len(dist2)):
                        if dist2[l] > 0:
                            fail = 1
                    if fail == 0:
                        new_coords2.append([float(random_x[n_ind,j]), float(random_y[n_ind,j])]) 
            
            full_coords2.append(new_coords2)
        
        grid_lbl = Label(ws, text = 'Points created!', foreground = 'green')    
        grid_lbl.place(x = 970, y = 520)
        
        ws.after(2000, destroy_widget, grid_lbl)
        
        if c == 0:
            global PhysCoord_randbtn
            global base_name10
            PhysCoord_randbtn = Button(ws, text = 'Get Coordinates', command = lambda:get_phys_randcoords(full_coords2, contr, base_name10.get('1.0','end-1c')))
            PhysCoord_randbtn.place(x = col3_px, y = 550)
            base_name10 = Text(ws, height = 1, width = 30)
            base_name10.place(in_ = PhysCoord_randbtn, y = 0, relx = spacing)
        else:
            PhysCoord_randbtn.destroy()
            base_name10.destroy()
            PhysCoord_randbtn = Button(ws, text = 'Get Coordinates', command = lambda:get_phys_randcoords(full_coords2, contr, base_name10.get('1.0','end-1c')))
            PhysCoord_randbtn.place(x = col3_px, y = 550)
            base_name10 = Text(ws, height = 1, width = 30)
            base_name10.place(in_ = PhysCoord_randbtn, y = 0, relx = spacing)
            
        global c12
        c12 = 1
        
    def get_phys_randcoords(full_coords2, contr, name):
        global phys_coords2
        phys_coords2 = full_coords2.copy()
        if contr == 'X':
            for j in range(len(full_coords2)):
                savedcoords2 = []
                for k in range(len(full_coords[j])):
                    phys_coords2[j][k][0] = MinX+dx*full_coords2[j][k][0]
                    phys_coords2[j][k][1] = MinZ+dz*full_coords2[j][k][1]
                    savedcoords2.append((float(phys_coords2[j][k][0]),float(yy),float(phys_coords2[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords2)
        elif contr == 'Y':
            for j in range(len(full_coords2)):
                savedcoords2 = []
                for k in range(len(full_coords2[j])):           
                    phys_coords2[j][k][0] = MinY+dy*full_coords2[j][k][0]
                    phys_coords2[j][k][1] = MinZ+dz*full_coords2[j][k][1]
                    savedcoords2.append((float(xx),float(phys_coords2[j][k][0]),float(phys_coords2[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords2)
        elif contr == 'Z':
            for j in range(len(full_coords2)):
                savedcoords2 = []
                for k in range(len(full_coords2[j])):           
                    phys_coords2[j][k][0] = MinX+dx*full_coords2[j][k][0]
                    phys_coords2[j][k][1] = MinY+dy*full_coords2[j][k][1]
                    savedcoords2.append((float(phys_coords2[j][k][0]),float(phys_coords2[j][k][1]), float(zz)))
                np.savetxt(name+str(j)+".txt", savedcoords2)
                
        coord_lbl = Label(ws, text = 'Coordinates saved!', foreground = 'green')    
        coord_lbl.place(x = col3_px, y = 580)
        
        ws.after(2000, destroy_widget, coord_lbl)
        
    ws.protocol("WM_DELETE_WINDOW", ws.quit)
    ws.mainloop()
    ws.destroy()
    
elif selected_index == 2:
    ws = Tk()
    ws.title(Name+" <Create Source-Points Mode>")
    ws.geometry('450x370')

    #control parameters for avoiding creating widgets multiple times
    c1, c2, c3 = 0, 0, 0
    xsteps = tki.StringVar(value = 0)

    addat = Label(ws, text='Load current FR Mask:')
    addat.place(x = 20, y = 10)
    
    addatbtn = Button(ws, text ='Choose Files', command = lambda:open_file_npz()) 
    addatbtn.place(in_ = addat, y = 0, relx = spacing)
    
    upld = Button(ws, text='Load Files', command = lambda:uploadFiles_npz_only(file_path_npz, c1))
    upld.place(in_ = addatbtn, y = 0, relx = spacing)
    
    def open_file_npz():
        global file_path_npz
        file_path_npz = askopenfilenames(initialdir='./', filetypes=[('NPZ Files', '*npz')])
        
    def uploadFiles_npz_only(file_path_npz, c):
        global final
        final = []
        Test = np.load(file_path_npz[0], allow_pickle = True)
        for j in range(0, len(Test['data'])):
            final.append(Test['data'][int(j)])
        
        global dim, MinX, MaxX, MinY, MaxY, MinZ, MaxZ, dx, dy, dz, contr
        
        if (len(Test['x']) > 1) & (len(Test['y']) > 1):
            global zz
            zz = Test['z']
            #print(np.shape(Test['x']))
            dim = [len(Test['y']), len(Test['x'])]
            MinX = min(Test['x'])
            MaxX = max(Test['x'])
            MX = (MaxX-MinX)
            dx = MX/(dim[1]-1)
            MinY = min(Test['y'])
            MaxY = max(Test['y'])
            MY = (MaxY-MinY)
            dy = MY/(dim[0]-1)
            contr = 'Z'            
        elif (len(Test['x']) > 1):
            global yy
            yy = Test['y']
            #print(np.shape(Test['x']))
            dim = [len(Test['z']), len(Test['x'])]
            MinX = min(Test['x'])
            MaxX = max(Test['x'])
            MX = (MaxX-MinX)
            dx = MX/(dim[1]-1)
            MinZ = min(Test['z'])
            MaxZ = max(Test['z'])
            MZ = (MaxZ-MinZ)
            dz = MZ/(dim[0]-1)
            contr = 'X'            
        elif (len(Test['y']) > 1):
            global xx
            xx = Test['x']
            dim = [len(Test['z']), len(Test['y'])]
            MinY = min(Test['y'])
            MaxY = max(Test['y'])
            MY = (MaxY-MinY)
            dy = MY/(dim[1]-1)
            MinZ = min(Test['z'])
            MaxZ = max(Test['z'])
            MZ = (MaxZ-MinZ)
            dz = MZ/(dim[0]-1)
            contr = 'Y'
                
        Uploadnpz_lbl = Label(ws, text='Files Loaded Successfully!', foreground='green')
        Uploadnpz_lbl.place(x = 165, y = 40)
        ws.after(2000, destroy_widget, Uploadnpz_lbl)
        
        if c == 0:
            xsteps_lbl = Label(ws, text = 'Enter sample size (in x):')
            xsteps_lbl.place(x = 10, y = 70)
            Enter_xsteps = Entry(ws, textvariable = xsteps, width = wi)
            Enter_xsteps.place(in_ = xsteps_lbl, y = 0, relx = spacing)
    
            uniform_lbl = Label(ws, text = 'Uniform sampling:')
            uniform_lbl.place(x = 10, y = 100)
            Grid_Button = Button(ws, text = 'Create Grid', command = lambda:create_grid(final, xsteps.get(), contr, c2))
            Grid_Button.place(in_ = uniform_lbl, y = 0, relx = spacing)

            random_lbl = Label(ws, text = 'Random sampling:')
            random_lbl.place(x = 10, y = 220)
            Random_Button = Button(ws, text = 'Create Points', command = lambda:create_random(final, xsteps.get(), contr, c3))
            Random_Button.place(in_ = random_lbl, y = 0, relx = spacing)
            
        global c1
        c1 = 1
        
    def create_grid(arr, steps, contr, c):
        Nsteps_x = int(steps)
        arr = np.array(arr)
        
        if contr == "X":
            dx_new = (MaxX-MinX)/Nsteps_x
            Nsteps_y = (MaxZ-MinZ)/dx_new  
            x_axis = np.linspace(0, dim[1], Nsteps_x)
            y_axis = np.linspace(0, dim[0], int(Nsteps_y))        
        elif contr == 'Y':
            dx_new = (MaxY-MinY)/Nsteps_x
            Nsteps_y = (MaxZ-MinZ)/dx_new    
            x_axis = np.linspace(0, dim[1], Nsteps_x)
            y_axis = np.linspace(0, dim[0], int(Nsteps_y))
        elif contr == 'Z':
            dx_new = (MaxX-MinX)/Nsteps_x
            Nsteps_y = (MaxY-MinY)/dx_new    
            x_axis = np.linspace(0, dim[1], Nsteps_x)
            y_axis = np.linspace(0, dim[0], int(Nsteps_y))
            
        Grid = np.meshgrid(x_axis, y_axis)
        
        global full_coords
        full_coords = []
        
        for n_ind in range(len(arr)):    
            Tw10 = arr[n_ind,:,:].astype(np.uint8)
            ret, bin_10 = cv2.threshold(Tw10, 0.5, 255, cv2.THRESH_BINARY)
            
            cont_10, hierachy = cv2.findContours(bin_10, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    
            img_contours = np.zeros(bin_10.shape)
            cv2.drawContours(img_contours, cont_10, -1, (255,0,0), 2)
            
            lencont = []
            new_coords = []
            for j in range(len(Grid[0][0])):
                    for k in range(len(Grid[1])):
                        dist2 = []
                        for m in range(len(cont_10)):
                            lencont.append(len(cont_10[m]))
                        maxlen = max(lencont)
                        for m in range(len(cont_10)):
                            if lencont[m] == maxlen:
                                dist = cv2.pointPolygonTest(cont_10[m], tuple([Grid[0][0][j], Grid[1][k][0]]), False)
                            else:
                                dist2.append(cv2.pointPolygonTest(cont_10[m], tuple([Grid[0][0][j], Grid[1][k][0]]), False))                                
                        if dist > 0:
                            fail = 0
                            for l in range(len(dist2)):
                                if dist2[l] > 0:
                                    fail = 1
                            if fail == 0:
                                new_coords.append([Grid[0][0][j], Grid[1][k][0]])
            
            full_coords.append(new_coords)
        
        grid_lbl = Label(ws, text = 'Grid created!', foreground = 'green')    
        grid_lbl.place(x = 20, y = 130)
        
        ws.after(2000, destroy_widget, grid_lbl)
        
        if c == 0:
            base_name7 = Text(ws, height = 1, width = 30)
            base_name7.place(x = 10, y = 160)
            PhysCoord_btn = Button(ws, text = 'Get Coordinates', command = lambda:get_phys_coords(full_coords, contr, base_name7.get('1.0','end-1c')))
            PhysCoord_btn.place(in_ = base_name7, y = 0, relx = spacing)   

        global c2
        c2 = 1        
        
    def get_phys_coords(full_coords, contr, name):
        global phys_coords
        phys_coords = full_coords.copy()
        if contr == 'X':
            for j in range(len(full_coords)):
                savedcoords = []
                for k in range(len(full_coords[j])):
                    phys_coords[j][k][0] = MinX+dx*full_coords[j][k][0]
                    phys_coords[j][k][1] = MinZ+dz*full_coords[j][k][1]
                    savedcoords.append((float(phys_coords[j][k][0]),float(yy),float(phys_coords[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords)
        elif contr == 'Y':
            for j in range(len(full_coords)):
                savedcoords = []
                for k in range(len(full_coords[j])):           
                    phys_coords[j][k][0] = MinY+dy*full_coords[j][k][0]
                    phys_coords[j][k][1] = MinZ+dz*full_coords[j][k][1]
                    savedcoords.append((float(xx),float(phys_coords[j][k][0]),float(phys_coords[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords)
        elif contr == 'Z':
            for j in range(len(full_coords)):
                savedcoords = []
                for k in range(len(full_coords[j])):           
                    phys_coords[j][k][0] = MinX+dx*full_coords[j][k][0]
                    phys_coords[j][k][1] = MinY+dy*full_coords[j][k][1]
                    savedcoords.append((float(phys_coords[j][k][0]),float(phys_coords[j][k][1]), float(zz)))
                np.savetxt(name+str(j)+".txt", savedcoords)
                
        coord_lbl = Label(ws, text = 'Coordinates saved!', foreground = 'green')    
        coord_lbl.place(x = 20, y = 190)
        
        ws.after(2000, destroy_widget, coord_lbl)

    def create_random(arr, steps, contr, c): 
        arr = np.array(arr)
        num_points = int(steps)**2
        
        random_x = np.random.randint(dim[1], size = (len(arr), num_points))
        random_y = np.random.randint(dim[0], size = (len(arr), num_points))        

        global full_coords2
        full_coords2 = []
        
        for n_ind in range(len(arr)):    
            Tw10 = arr[n_ind,:,:].astype(np.uint8)
            ret, bin_10 = cv2.threshold(Tw10, 0.5, 255, cv2.THRESH_BINARY)
            
            cont_10, hierachy = cv2.findContours(bin_10, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    
            img_contours = np.zeros(bin_10.shape)
            cv2.drawContours(img_contours, cont_10, -1, (255,0,0), 2)
            
            lencont = []
            new_coords2 = []
            for j in range(num_points):
                dist2 = []
                for m in range(len(cont_10)):
                    lencont.append(len(cont_10[m]))
                maxlen = max(lencont)
                for m in range(len(cont_10)):
                    if lencont[m] == maxlen:
                        dist = cv2.pointPolygonTest(cont_10[m], tuple([float(random_x[n_ind, j]), float(random_y[n_ind, j])]), False)                
                    else:
                        dist2.append(cv2.pointPolygonTest(cont_10[m], tuple([float(random_x[n_ind, j]), float(random_y[n_ind, j])]), False))
                if dist > 0:
                    fail = 0
                    for l in range(len(dist2)):
                        if dist2[l] > 0:
                            fail = 1
                    if fail == 0:
                        new_coords2.append([float(random_x[n_ind,j]), float(random_y[n_ind,j])]) 
            
            full_coords2.append(new_coords2)
        
        grid_lbl = Label(ws, text = 'Points created!', foreground = 'green')    
        grid_lbl.place(x = 20, y = 250)
        
        ws.after(2000, destroy_widget, grid_lbl)
        
        if c == 0:
            base_name10 = Text(ws, height = 1, width = 30)
            base_name10.place(x = 10, y = 280)
            PhysCoord_randbtn = Button(ws, text = 'Get Coordinates', command = lambda:get_phys_randcoords(full_coords2, contr, base_name10.get('1.0','end-1c')))
            PhysCoord_randbtn.place(in_ = base_name10, y = 0, relx = spacing)
        
        global c3
        c3 = 1
        
    def get_phys_randcoords(full_coords2, contr, name):
        global phys_coords2
        phys_coords2 = full_coords2.copy()
        if contr == 'X':
            for j in range(len(full_coords2)):
                savedcoords2 = []
                for k in range(len(full_coords[j])):
                    phys_coords2[j][k][0] = MinX+dx*full_coords2[j][k][0]
                    phys_coords2[j][k][1] = MinZ+dz*full_coords2[j][k][1]
                    savedcoords2.append((float(phys_coords2[j][k][0]),float(yy),float(phys_coords2[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords2)
        elif contr == 'Y':
            for j in range(len(full_coords2)):
                savedcoords2 = []
                for k in range(len(full_coords2[j])):           
                    phys_coords2[j][k][0] = MinY+dy*full_coords2[j][k][0]
                    phys_coords2[j][k][1] = MinZ+dz*full_coords2[j][k][1]
                    savedcoords2.append((float(xx),float(phys_coords2[j][k][0]),float(phys_coords2[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords2)
        elif contr == 'Z':
            for j in range(len(full_coords2)):
                savedcoords2 = []
                for k in range(len(full_coords2[j])):           
                    phys_coords2[j][k][0] = MinX+dx*full_coords2[j][k][0]
                    phys_coords2[j][k][1] = MinY+dy*full_coords2[j][k][1]
                    savedcoords2.append((float(phys_coords2[j][k][0]),float(phys_coords2[j][k][1]), float(zz)))
                np.savetxt(name+str(j)+".txt", savedcoords2)
                
        coord_lbl = Label(ws, text = 'Coordinates saved!', foreground = 'green')    
        coord_lbl.place(x = 20, y = 310)
        
        ws.after(2000, destroy_widget, coord_lbl)
   
    ws.protocol("WM_DELETE_WINDOW", ws.quit)
    ws.mainloop()
    ws.destroy()

    
elif selected_index == 3:
    ws = Tk()
    ws.title(Name + '<Difference Map Points>')
    ws.geometry('860x670')
    
    canv_num = 0
    c1, c2, c3, c4, c5, c6 = 0, 0, 0, 0, 0, 0
    
    xsteps = tki.StringVar(value = 0)
    spin10_val = tki.StringVar(value=0)
    
    addat = Label(ws, text='Load FR Mask 1:')
    addat.place(x = 20, y = 10)
    
    addatbtn = Button(ws, text ='Choose Files', command = lambda:open_file_npz()) 
    addatbtn.place(in_ = addat, y = 0, relx = spacing)
    
    upld = Button(ws, text='Load Files', command = lambda:uploadFiles_npz_only(file_path_npz, c1))
    upld.place(in_ = addatbtn, y = 0, relx = spacing)
    
    def open_file_npz():
        global file_path_npz
        file_path_npz = askopenfilenames(initialdir='./', filetypes=[('NPZ Files', '*npz')])
        
    def uploadFiles_npz_only(file_path_npz, c):
        global final
        final = []
        Test = np.load(file_path_npz[0], allow_pickle = True)
        for j in range(0, len(Test['data'])):
            final.append(Test['data'][int(j)])
        
        global dim, MinX, MaxX, MinY, MaxY, MinZ, MaxZ, dx, dy, dz, contr
        
        if (len(Test['x']) > 1) & (len(Test['y']) > 1):
            global zz
            zz = Test['z']
            #print(np.shape(Test['x']))
            dim = [len(Test['y']), len(Test['x'])]
            MinX = min(Test['x'])
            MaxX = max(Test['x'])
            MX = (MaxX-MinX)
            dx = MX/(dim[1]-1)
            MinY = min(Test['y'])
            MaxY = max(Test['y'])
            MY = (MaxY-MinY)
            dy = MY/(dim[0]-1)
            contr = 'Z'            
        elif (len(Test['x']) > 1):
            global yy
            yy = Test['y']
            #print(np.shape(Test['x']))
            dim = [len(Test['z']), len(Test['x'])]
            MinX = min(Test['x'])
            MaxX = max(Test['x'])
            MX = (MaxX-MinX)
            dx = MX/(dim[1]-1)
            MinZ = min(Test['z'])
            MaxZ = max(Test['z'])
            MZ = (MaxZ-MinZ)
            dz = MZ/(dim[0]-1)
            contr = 'X'            
        elif (len(Test['y']) > 1):
            global xx
            xx = Test['x']
            dim = [len(Test['z']), len(Test['y'])]
            MinY = min(Test['y'])
            MaxY = max(Test['y'])
            MY = (MaxY-MinY)
            dy = MY/(dim[1]-1)
            MinZ = min(Test['z'])
            MaxZ = max(Test['z'])
            MZ = (MaxZ-MinZ)
            dz = MZ/(dim[0]-1)
            contr = 'Y'
                
        Uploadnpz_lbl = Label(ws, text='Files Loaded Successfully!', foreground='green')
        Uploadnpz_lbl.place(x = 165, y = 40)       
        ws.after(2000, destroy_widget, Uploadnpz_lbl)
        
        if c == 0:
            addat = Label(ws, text='Load FR Mask 2:')
            addat.place(x = 20, y = 70)
    
            addatbtn = Button(ws, text ='Choose Files', command = lambda:open_file_npz2()) 
            addatbtn.place(in_ = addat, y = 0, relx = spacing)
    
            upld = Button(ws, text='Load Files', command = lambda:uploadFiles_npz_only2(file_path_npz2, c2))
            upld.place(in_ = addatbtn, y = 0, relx = spacing)
            
        global c1 
        c1 = 1

    def open_file_npz2():
        global file_path_npz2
        file_path_npz2 = askopenfilenames(initialdir='./', filetypes=[('NPZ Files', '*npz')])
        
    def uploadFiles_npz_only2(file_path_npz2, c):
        global final2
        final2 = []
        Test = np.load(file_path_npz2[0], allow_pickle = True)
        for j in range(0, len(Test['data'])):
            final2.append(Test['data'][int(j)])
        
        global dim, MinX, MaxX, MinY, MaxY, MinZ, MaxZ, dx, dy, dz, contr
        
        if (len(Test['x']) > 1) & (len(Test['y']) > 1):
            global zz
            zz = Test['z']
            #print(np.shape(Test['x']))
            dim = [len(Test['y']), len(Test['x'])]
            MinX = min(Test['x'])
            MaxX = max(Test['x'])
            MX = (MaxX-MinX)
            dx = MX/(dim[1]-1)
            MinY = min(Test['y'])
            MaxY = max(Test['y'])
            MY = (MaxY-MinY)
            dy = MY/(dim[0]-1)
            contr = 'Z'            
        elif (len(Test['x']) > 1):
            global yy
            yy = Test['y']
            #print(np.shape(Test['x']))
            dim = [len(Test['z']), len(Test['x'])]
            MinX = min(Test['x'])
            MaxX = max(Test['x'])
            MX = (MaxX-MinX)
            dx = MX/(dim[1]-1)
            MinZ = min(Test['z'])
            MaxZ = max(Test['z'])
            MZ = (MaxZ-MinZ)
            dz = MZ/(dim[0]-1)
            contr = 'X'            
        elif (len(Test['y']) > 1):
            global xx
            xx = Test['x']
            dim = [len(Test['z']), len(Test['y'])]
            MinY = min(Test['y'])
            MaxY = max(Test['y'])
            MY = (MaxY-MinY)
            dy = MY/(dim[1]-1)
            MinZ = min(Test['z'])
            MaxZ = max(Test['z'])
            MZ = (MaxZ-MinZ)
            dz = MZ/(dim[0]-1)
            contr = 'Y'
        
        if np.shape(final) == np.shape(final2):        
            Uploadnpz_lbl = Label(ws, text='Files Loaded Successfully!', foreground='green')
            Uploadnpz_lbl.place(x = 165, y = 100)        
            ws.after(2000, destroy_widget, Uploadnpz_lbl)

        else:
            Uploadnpz_lbl = Label(ws, text='File Dimensions Do Not Match!', foreground='red')
            Uploadnpz_lbl.place(x = 165, y = 100)        
            ws.after(2000, destroy_widget, Uploadnpz_lbl)

        if c == 0:
            Diff_Button = Button(ws, text = 'Create Difference Map', command = lambda:get_diff(final, final2, c3))
            Diff_Button.place(x = 20, y = 130)
            
        global c2
        c2 = 1
        
    def get_diff(final, final2, c):
        global Diff
        Diff = np.array(final) - np.array(final2)
        Diff[Diff < 0] = 0
        
        Diff_lbl = Label(ws, text = 'Difference Map created', foreground = 'green')
        Diff_lbl.place(x = 200, y = 130)
        ws.after(2000, destroy_widget, Diff_lbl)
        
        if c == 0:
            global spin10
            spin10 = Spinbox(ws, from_ = 0, to = len(final)-1, textvariable = spin10_val, wrap = True, width = wi)
            spin10.place(x = 20, y = 160)
        
            vis7_btn = Button(ws, text = 'Visualize', command = lambda:Vis_diff(contr, Diff, spin10_val.get(), canv_num, c4))
            vis7_btn.place(in_ = spin10, y = 0, relx = spacing)
        else:
            spin10.destroy()
            spin10 = Spinbox(ws, from_ = 0, to = len(final)-1, textvariable = spin10_val, wrap = True, width = wi)
            spin10.place(x = 20, y = 160)     

        global c3
        c3 = 1
        
    def Vis_diff(contr, twist, num, num2, c):
        plt.close()
        #fig = plt.figure()
        num = int(num)
        fig = Figure(figsize=(4.5,3.5))
        plot1 = fig.add_subplot(111)
        if contr == 'X': 
            plot1.imshow(twist[num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinZ, MaxZ])
            plot1.set_title("Difference Map no. "+str(num), fontsize = 9)
            plot1.set_ylabel("Z", fontsize = 9)
            plot1.set_xlabel("X", fontsize = 9)
            plot1.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Y': 
            plot1.imshow(twist[num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinY, MaxY, MinZ, MaxZ])
            plot1.set_title("Difference Map no. "+str(num), fontsize = 9)
            plot1.set_ylabel("Z", fontsize = 9)
            plot1.set_xlabel("Y", fontsize = 9)
            plot1.tick_params(axis='both', which='major', labelsize=7)
        elif contr == 'Z':
            plot1.imshow(twist[num], origin = "lower", cmap = "gray", vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinY, MaxY])
            plot1.set_title("Difference Map no. "+str(num), fontsize = 9)
            plot1.set_ylabel("Y", fontsize = 9)
            plot1.set_xlabel("X", fontsize = 9)
            plot1.tick_params(axis='both', which='major', labelsize=7)            
        
        if num2 == 0:
            global canvas
            canvas = FigureCanvasTkAgg(fig, master=ws)
            canvas.draw()
            canvas.get_tk_widget().place(x = 20, y = 190)
        else:     
            canvas.get_tk_widget().destroy()
            canvas = FigureCanvasTkAgg(fig, master=ws)
            canvas.draw()
            canvas.get_tk_widget().place(x = 20, y = 190)
        
        global canv_num
        canv_num = 1
        
        if c == 0:
            base_name11 = Text(ws, height = 1, width = 30)
            base_name11.place(x = basecol1_px, y = 560)
            save_frames = Button(ws, text = 'Save Frames', command = lambda:savefunc(contr, Diff, base_name11.get('1.0','end-1c')))
            save_frames.place(x = 20, y = 560)
            
            base_name12 = Text(ws, height = 1, width = 30)
            base_name12.place(x = basecol1_px, y = 590)
            save_array = Button(ws, text = 'Save Arrays', command = lambda:savearr(Diff, base_name12.get('1.0','end-1c')))
            save_array.place(x = 20, y = 590)
            base_name13 = Text(ws, height = 1, width = 30)
            base_name13.place(x = basecol1_px, y = 620)
            save_anim = Button(ws, text = 'Save Animation', command = lambda:saveanim(Diff, base_name13.get('1.0','end-1c'), contr))
            save_anim.place(x = 20, y = 620)
            
            Label(ws, text = 'Enter sample size (in x):').place(x = col2_px, y = 10)
            Enter_xsteps = Entry(ws, textvariable = xsteps, width = wi)
            Enter_xsteps.place(x = col2_px, y = 40)
        
            Label(ws, text = 'Uniform sampling:').place(x = col2_px, y = 70)
            Grid_Button = Button(ws, text = 'Create Grid', command = lambda:create_grid(Diff, xsteps.get(), contr, c5))
            Grid_Button.place(x = col2_px, y = 100)
    
            Label(ws, text = 'Random sampling:').place(x = col2_px, y = 160)
            Random_Button = Button(ws, text = 'Create Points', command = lambda:create_random(Diff, xsteps.get(), contr, c6))
            Random_Button.place(x = col2_px, y = 190)
            
        global c4 
        c4 = 1


    def savefunc(contr, Diff, filenames):
    
        #invoke window to customize plotting options
        plotws = tki.Toplevel(ws)
        plotws.title("Plot Specifications")
        plotws.geometry(str(horsz_plotws)+'x640')
        plotws.grab_set()
        
        #Set colormap:
        global cmap_to_use
        cmap_to_use = "gray"
        
        #enable listbox if customize option is on
        def set_colormap(boxon):
            if boxon % 2 == 1:
                listbox3.config(state = "normal")
            else:
                listbox3.config(state = "disabled")

        #customization checkbox
        def_colormap = tki.IntVar(value = 0)
        check_default_colormap = Checkbutton(plotws, text = "Customize", variable = def_colormap, command = lambda:set_colormap(def_colormap.get()))        
        check_default_colormap.place(x = 10, y = 90)
        
        listbox3 = tki.Listbox(plotws, height=7, width = 25, selectmode=tki.SINGLE, exportselection=False)
        
        #listbox for colormaps
        for j in range(len(cmaps)):
            listbox3.insert(tki.END, cmaps[j])
        listbox3.place(x = 120, y = 35)
        listbox3.config(state = "disabled")
        
        colormap_lbl = Label(plotws, text = 'Choose Colormap:')    
        colormap_lbl.place(x = 120, y = 10)   
        
        #get selected colormap
        def color_selected(event):
            global cmap_to_use
            cmap_to_use = cmaps[int(listbox3.curselection()[0])]
    
        listbox3.bind('<<ListboxSelect>>', color_selected)        
        
        #Set figure size checkbox:
        def_figsize = tki.IntVar(value = 0)
        check_default_figsize = Checkbutton(plotws, text = "Customize", variable = def_figsize, command = lambda:set_figsize(def_figsize.get()))        
        check_default_figsize.place(x = 10, y = 180)   
        
        Label(plotws, text='Choose Figure Size:').place(x = 120, y = 180)
        
        #default figure sizes
        figure_x = tki.StringVar(value = "12")
        figure_y = tki.StringVar(value = "12")
        
        #entry boxes for figuresizes
        xfig = Label(plotws, text = 'x =')
        xfig.place(x = 120, y = 210)
        Enter_figx = Entry(plotws, textvariable = figure_x, width = 4)
        Enter_figx.place(in_ = xfig, y = 0, relx = spacing)
        yfig = Label(plotws, text = 'y =')
        yfig.place(in_ = Enter_figx, y = 0, relx = spacing)
        Enter_figy = Entry(plotws, textvariable = figure_y, width = 4)
        Enter_figy.place(in_ = yfig, y = 0, relx = spacing)
        
        Enter_figx.config(state = "disabled")
        Enter_figy.config(state = "disabled")
        
        #enable/disable figure entry boxes
        def set_figsize(boxon):
            if boxon % 2 == 1:
                Enter_figx.config(state = "normal")
                Enter_figy.config(state = "normal")
            else:
                Enter_figx.config(state = "disabled")
                Enter_figy.config(state = "disabled")  
        
        
        #same thing with the plot title:
        def_title = tki.IntVar(value = 0)
        check_default_title = Checkbutton(plotws, text = "Customize", variable = def_title, command = lambda:set_plottitle(def_title.get()))        
        check_default_title.place(x = 10, y = 240)   
        
        Label(plotws, text='Choose Figure Title:').place(x = 120, y = 240)
        
        figure_title = tki.StringVar(value = "")
        text_title = Text(plotws, height = 1, width = 20)
        text_title.place(x = 120, y = 270)        
        text_title.config(state = "disabled")
        
        def set_plottitle(boxon):
            if boxon % 2 == 1:
                text_title.config(state = "normal")
            else:
                text_title.config(state = "disabled")
        
        #same thing with the titlesize 
        def_titlesize = tki.IntVar(value = 0)
        check_default_titlesize = Checkbutton(plotws, text = "Customize", variable = def_titlesize, command = lambda:set_titlesize(def_titlesize.get()))        
        check_default_titlesize.place(x = 10, y = 300)   
        
        Label(plotws, text='Choose Title Size:').place(x = 120, y = 300)
        
        titlesize = tki.StringVar(value = "14")
        Enter_titlesize = Entry(plotws, textvariable = titlesize, width = 6)
        Enter_titlesize.place(x = 120, y = 330)       
        Enter_titlesize.config(state = "disabled")
        
        def set_titlesize(boxon):
            if boxon % 2 == 1:
                Enter_titlesize.config(state = "normal")
            else:
                Enter_titlesize.config(state = "disabled")
        
        #Same thing with the ticksizes 
        def_ticksize = tki.IntVar(value = 0)
        check_default_ticksize = Checkbutton(plotws, text = "Customize", variable = def_ticksize, command = lambda:set_ticksize(def_ticksize.get()))        
        check_default_ticksize.place(x = 10, y = 360)   
        
        Label(plotws, text='Choose Ticksize:').place(x = 120, y = 360)
        
        ticksize = tki.StringVar(value = "14")
        Enter_ticksize = Entry(plotws, textvariable = ticksize, width = 6)
        Enter_ticksize.place(x = 120, y = 390)       
        Enter_ticksize.config(state = "disabled")
        
        def set_ticksize(boxon):
            if boxon % 2 == 1:
                Enter_ticksize.config(state = "normal")
            else:
                Enter_ticksize.config(state = "disabled")

        #Same thing with the axis labels
        def_label = tki.IntVar(value = 0)
        check_default_label = Checkbutton(plotws, text = "Customize", variable = def_label, command = lambda:set_label(def_label.get()))        
        check_default_label.place(x = 10, y = 420)   
        
        Label(plotws, text='Choose Labels:').place(x = 120, y = 420)
        
        label_x = tki.StringVar(value = "")
        label_y = tki.StringVar(value = "")
        
        axx_lbl = Label(plotws, text = 'x =')
        axx_lbl.place(x = 120, y = 450)
        Enter_labelx = Entry(plotws, textvariable = label_x, width = 6)
        Enter_labelx.place(in_ = axx_lbl, y = 0, relx = spacing)
        axy_lbl = Label(plotws, text = 'y =')
        axy_lbl.place(in_ = Enter_labelx, y = 0, relx = spacing)
        Enter_labely = Entry(plotws, textvariable = label_y, width = 6)
        Enter_labely.place(in_ = axy_lbl, y = 0, relx = spacing)
        
        Enter_labelx.config(state = "disabled")
        Enter_labely.config(state = "disabled")
        
        def set_label(boxon):
            if boxon % 2 == 1:
                Enter_labelx.config(state = "normal")
                Enter_labely.config(state = "normal")
            else:
                Enter_labelx.config(state = "disabled")
                Enter_labely.config(state = "disabled")
                
        #same thing with the axis labelsize      
        def_labelsize = tki.IntVar(value = 0)
        check_default_labelsize = Checkbutton(plotws, text = "Customize", variable = def_labelsize, command = lambda:set_labelsize(def_labelsize.get()))        
        check_default_labelsize.place(x = 10, y = 480)   
        
        Label(plotws, text='Choose Labelsize:').place(x = 120, y = 480)
        
        labelsize = tki.StringVar(value = "14")
        Enter_labelsize = Entry(plotws, textvariable = labelsize, width = 6)
        Enter_labelsize.place(x = 120, y = 510)       
        Enter_labelsize.config(state = "disabled")
        
        def set_labelsize(boxon):
            if boxon % 2 == 1:
                Enter_labelsize.config(state = "normal")
            else:
                Enter_labelsize.config(state = "disabled")
        
        #Setting vmin/vmax values for the colormap
        def_minmax = tki.IntVar(value = 0)
        check_default_minmax = Checkbutton(plotws, text = "Customize", variable = def_minmax, command = lambda:set_minmax(def_minmax.get()))        
        check_default_minmax.place(x = 10, y = 540)   
        
        Label(plotws, text='Choose Colormap Limits:').place(x = 120, y = 540)
        
        vmin = tki.IntVar(value = 0)
        vmax = tki.IntVar(value = 1.5)
        
        vmin_lbl = Label(plotws, text = 'vmin =')
        vmin_lbl.place(x = 120, y = 570)
        Enter_vmin = Entry(plotws, textvariable = vmin, width = 4)
        Enter_vmin.place(in_ = vmin_lbl, y = 0, relx = spacing)
        vmax_lbl = Label(plotws, text = 'vmax =')
        vmax_lbl.place(in_ = Enter_vmin, y = 0, relx = spacing)
        Enter_vmax = Entry(plotws, textvariable = vmax, width = 4)
        Enter_vmax.place(in_ = vmax_lbl, y = 0, relx = spacing)
         
        Enter_vmin.config(state = "disabled")
        Enter_vmax.config(state = "disabled")
        
        def set_minmax(boxon):
            if boxon % 2 == 1:
                Enter_vmin.config(state = "normal")
                Enter_vmax.config(state = "normal")
            else:
                Enter_vmin.config(state = "disabled")
                Enter_vmax.config(state = "disabled")
        
        #confirm button to grab all variables from customization window and to destroy this window
        conf_btn3 = Button(plotws, text='Confirm', command = lambda:destroy_widget_2(plotws, def_colormap.get(), def_figsize.get(), def_title.get(), \
        def_titlesize.get(), def_ticksize.get(), def_label.get(), def_labelsize.get(), def_minmax.get(), figure_x.get(), figure_y.get(), text_title.get('1.0','end-1c'), titlesize.get(), \
        ticksize.get(), label_x.get(), label_y.get(), labelsize.get(), vmin.get(), vmax.get(), cmap_to_use))
        
        conf_btn3.place(x = 120, y = 605)
        
        #plotting+saving function, which saves the plot and destroys the customization window
        #boxonX are the variables communicating to the plotting function if the customization checkbox was on or off
        def destroy_widget_2(widget, boxon1, boxon2, boxon3, boxon4, boxon5, boxon6, boxon7, boxon8, figx, figy, title_name, titlesize, ticksize, labelx, labely,\
        labelsize, vmin, vmax, cmap_to_use):

            L = len(Diff)
            
            #if not customized, use default values/settings:            
            if boxon1 % 2 == 0:
                cmap_to_use = "RdBu_r"
                
            if boxon2 % 2 == 0:
                figx = dim[1]/50
                figy = dim[0]/50
            else:
                figx = int(figx)
                figy = int(figy)
            
            if boxon4 % 2 == 0:
                titlesize = 14
            else:
                titlesize = int(titlesize)

            if boxon5 % 2 == 0:
                ticksize = 14
            else:
                ticksize = int(ticksize)

            if boxon7 % 2 == 0:
                labelsize = 14
            else:
                labelsize = int(labelsize)
            
            #plotting and saving the figuresizes
            
            #Plotstr controls which array to plot
            #contr tells which dimensions (for cartesian: x, y, z) to use
            for j in range(L):
                fig = Figure(figsize=(figx, figy))
                plot1 = fig.add_subplot(111)
                if contr == 'X': 
                    if boxon8 % 2 == 0:
                        plot1.imshow(Diff[j], origin = "lower", cmap = cmap_to_use, vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinZ, MaxZ])
                    else:
                        plot1.imshow(Diff[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinZ, MaxZ])
                    if boxon3 % 2 == 0:
                        plot1.set_title("Difference Map no. "+str(j), fontsize = titlesize)
                    else: 
                        plot1.set_title(title_name, fontsize = titlesize)
                    if boxon6 % 2 == 0:
                        plot1.set_ylabel("Z", fontsize = labelsize)
                        plot1.set_xlabel("X", fontsize = labelsize)
                    else: 
                        plot1.set_ylabel(labely, fontsize = labelsize)
                        plot1.set_xlabel(labelx, fontsize = labelsize)                            
                    plot1.tick_params(labelsize = ticksize)
                    fig.savefig(filenames+str(j)+'.png')
                elif contr == 'Y':
                    if boxon8 % 2 == 0:
                        plot1.imshow(Diff[j], origin = "lower", cmap = cmap_to_use, vmin = 0, vmax = 1.5, extent = [MinY, MaxY, MinZ, MaxZ])
                    else:
                        plot1.imshow(Diff[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinY, MaxY, MinZ, MaxZ])
                    if boxon3 % 2 == 0:
                        plot1.set_title("Difference Map no. "+str(j), fontsize = titlesize)
                    else: 
                        plot1.set_title(title_name, fontsize = titlesize)
                    if boxon6 % 2 == 0:
                        plot1.set_ylabel("Z", fontsize = labelsize)
                        plot1.set_xlabel("Y", fontsize = labelsize)
                    else: 
                        plot1.set_ylabel(labely, fontsize = labelsize)
                        plot1.set_xlabel(labelx, fontsize = labelsize)  
                    plot1.tick_params(labelsize = ticksize)
                    fig.savefig(filenames+str(j)+'.png')
                elif contr == 'Z':
                    if boxon8 % 2 == 0:
                        plot1.imshow(Diff[j], origin = "lower", cmap = cmap_to_use, vmin = 0, vmax = 1.5, extent = [MinX, MaxX, MinY, MaxY])
                    else:
                        plot1.imshow(Diff[j], origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinY, MaxY])
                    if boxon3 % 2 == 0:
                        plot1.set_title("Difference Map no. "+str(j), fontsize = titlesize)
                    else: 
                        plot1.set_title(title_name, fontsize = titlesize)
                    if boxon6 % 2 == 0:
                        plot1.set_ylabel("Y", fontsize = labelsize)
                        plot1.set_xlabel("X", fontsize = labelsize)
                    else: 
                        plot1.set_ylabel(labely, fontsize = labelsize)
                        plot1.set_xlabel(labelx, fontsize = labelsize)  
                    plot1.tick_params(labelsize = ticksize)
                    fig.savefig(filenames+str(j)+'.png')
                            
            #correctly place label to indicate that the plot was indeed saved
            save_lbl = Label(ws, text = 'Saved!', foreground = 'green')    
            save_lbl.place(x = 420, y = 590)
            
            #destroy the "saved" label
            ws.after(2000, destroy_widget, save_lbl)
            plotws.destroy()
        

    def savearr(arr, filename):
        L = len(arr)
        
        if contr == 'X':
            x_vec = np.linspace(MinX, MaxX, dim[1])
            z_vec = np.linspace(MinZ, MaxZ, dim[0])
            np.savez(filename+".npz", data = arr, x = x_vec, y = [yy], z = z_vec)
        elif contr == 'Y':
            y_vec = np.linspace(MinY, MaxY, dim[1])
            z_vec = np.linspace(MinZ, MaxZ, dim[0])
            np.savez(filename+".npz", data = arr, x = [xx], y = y_vec, z = z_vec)
        elif contr == 'Z':
            y_vec = np.linspace(MinY, MaxY, dim[0])
            x_vec = np.linspace(MinX, MaxX, dim[1])
            np.savez(filename+".npz", data = arr, x = x_vec, y = y_vec, z = [zz])
        
        save_lbl = Label(ws, text = 'Saved!', foreground = 'green')  
        save_lbl.place(x = 420, y = 620) 

        ws.after(2000, destroy_widget, save_lbl)
  
    def saveanim(arr, filename, contr):
        plotws = tki.Toplevel(ws)
        plotws.title("Plot Specifications")
        plotws.geometry(str(horsz_plotws)+'x640')
        plotws.grab_set()
        
        #Set colormap:
        global cmap_to_use
        cmap_to_use = "gray"
        
        def set_colormap(boxon):
            if boxon % 2 == 1:
                listbox3.config(state = "normal")
            else:
                listbox3.config(state = "disabled")

        def_colormap = tki.IntVar(value = 0)
        check_default_colormap = Checkbutton(plotws, text = "Customize", variable = def_colormap, command = lambda:set_colormap(def_colormap.get()))        
        check_default_colormap.place(x = 10, y = 90)
        
        #cmap_to_use = tki.StringVar(value = '')
        listbox3 = tki.Listbox(plotws, height=7, width = 25, selectmode=tki.SINGLE, exportselection=False)
        
        for j in range(len(cmaps)):
            listbox3.insert(tki.END, cmaps[j])
        listbox3.place(x = 120, y = 35)
        listbox3.config(state = "disabled")
        
        colormap_lbl = Label(plotws, text = 'Choose Colormap:')
        colormap_lbl.place(x = 120, y = 10)   
        
        def color_selected(event):
            global cmap_to_use
            cmap_to_use = cmaps[int(listbox3.curselection()[0])]
    
        listbox3.bind('<<ListboxSelect>>', color_selected)
        
        #Set figure size:
        def_figsize = tki.IntVar(value = 0)
        check_default_figsize = Checkbutton(plotws, text = "Customize", variable = def_figsize, command = lambda:set_figsize(def_figsize.get()))        
        check_default_figsize.place(x = 10, y = 180)   
        
        Label(plotws, text='Choose Figure Size:').place(x = 120, y = 180)
        
        figure_x = tki.StringVar(value = "12")
        figure_y = tki.StringVar(value = "12")
        
        xfig = Label(plotws, text = 'x =')
        xfig.place(x = 120, y = 210)
        Enter_figx = Entry(plotws, textvariable = figure_x, width = 4)
        Enter_figx.place(in_ = xfig, y = 0, relx = spacing)
        yfig = Label(plotws, text = 'y =')
        yfig.place(in_ = Enter_figx, y = 0, relx = spacing)
        Enter_figy = Entry(plotws, textvariable = figure_y, width = 4)
        Enter_figy.place(in_ = yfig, y = 0, relx = spacing)
        
        Enter_figx.config(state = "disabled")
        Enter_figy.config(state = "disabled")
        
        def set_figsize(boxon):
            if boxon % 2 == 1:
                Enter_figx.config(state = "normal")
                Enter_figy.config(state = "normal")
            else:
                Enter_figx.config(state = "disabled")
                Enter_figy.config(state = "disabled")  
        
        #Set title:
        def_title = tki.IntVar(value = 0)
        check_default_title = Checkbutton(plotws, text = "Customize", variable = def_title, command = lambda:set_plottitle(def_title.get()))        
        check_default_title.place(x = 10, y = 240)   
        
        Label(plotws, text='Choose Figure Title:').place(x = 120, y = 240)
        
        figure_title = tki.StringVar(value = "")
        text_title = Text(plotws, height = 1, width = 20)
        text_title.place(x = 120, y = 270)        
        text_title.config(state = "disabled")
        
        def set_plottitle(boxon):
            if boxon % 2 == 1:
                text_title.config(state = "normal")
            else:
                text_title.config(state = "disabled")
        
        #Set titlesize 
        def_titlesize = tki.IntVar(value = 0)
        check_default_titlesize = Checkbutton(plotws, text = "Customize", variable = def_titlesize, command = lambda:set_titlesize(def_titlesize.get()))        
        check_default_titlesize.place(x = 10, y = 300)   
        
        Label(plotws, text='Choose Title Size:').place(x = 120, y = 300)
        
        titlesize = tki.StringVar(value = "14")
        Enter_titlesize = Entry(plotws, textvariable = titlesize, width = 6)
        Enter_titlesize.place(x = 120, y = 330)       
        Enter_titlesize.config(state = "disabled")
        
        def set_titlesize(boxon):
            if boxon % 2 == 1:
                Enter_titlesize.config(state = "normal")
            else:
                Enter_titlesize.config(state = "disabled")
        
        #Set ticksize 
        def_ticksize = tki.IntVar(value = 0)
        check_default_ticksize = Checkbutton(plotws, text = "Customize", variable = def_ticksize, command = lambda:set_ticksize(def_ticksize.get()))        
        check_default_ticksize.place(x = 10, y = 360)   
        
        Label(plotws, text='Choose Ticksize:').place(x = 120, y = 360)
        
        ticksize = tki.StringVar(value = "14")
        Enter_ticksize = Entry(plotws, textvariable = ticksize, width = 6)
        Enter_ticksize.place(x = 120, y = 390)       
        Enter_ticksize.config(state = "disabled")
        
        def set_ticksize(boxon):
            if boxon % 2 == 1:
                Enter_ticksize.config(state = "normal")
            else:
                Enter_ticksize.config(state = "disabled")

        #Set label
        def_label = tki.IntVar(value = 0)
        check_default_label = Checkbutton(plotws, text = "Customize", variable = def_label, command = lambda:set_label(def_label.get()))        
        check_default_label.place(x = 10, y = 420)   
        
        Label(plotws, text='Choose Labels:').place(x = 120, y = 420)
        
        label_x = tki.StringVar(value = "")
        label_y = tki.StringVar(value = "")
        
        axx_lbl = Label(plotws, text = 'x =')
        axx_lbl.place(x = 120, y = 450)
        Enter_labelx = Entry(plotws, textvariable = label_x, width = 6)
        Enter_labelx.place(in_ = axx_lbl, y = 0, relx = spacing)
        axy_lbl = Label(plotws, text = 'y =')
        axy_lbl.place(in_ = Enter_labelx, y = 0, relx = spacing)
        Enter_labely = Entry(plotws, textvariable = label_y, width = 6)
        Enter_labely.place(in_ = axy_lbl, y = 0, relx = spacing)
        
        Enter_labelx.config(state = "disabled")
        Enter_labely.config(state = "disabled")
        
        def set_label(boxon):
            if boxon % 2 == 1:
                Enter_labelx.config(state = "normal")
                Enter_labely.config(state = "normal")
            else:
                Enter_labelx.config(state = "disabled")
                Enter_labely.config(state = "disabled")
                
        #Set labelsize      
        def_labelsize = tki.IntVar(value = 0)
        check_default_labelsize = Checkbutton(plotws, text = "Customize", variable = def_labelsize, command = lambda:set_labelsize(def_labelsize.get()))        
        check_default_labelsize.place(x = 10, y = 480)   
        
        Label(plotws, text='Choose Labelsize:').place(x = 120, y = 480)
        
        labelsize = tki.StringVar(value = "14")
        Enter_labelsize = Entry(plotws, textvariable = labelsize, width = 6)
        Enter_labelsize.place(x = 120, y = 510)       
        Enter_labelsize.config(state = "disabled")
        
        def set_labelsize(boxon):
            if boxon % 2 == 1:
                Enter_labelsize.config(state = "normal")
            else:
                Enter_labelsize.config(state = "disabled")
        
        #Set vmin/vmax
        def_minmax = tki.IntVar(value = 0)
        check_default_minmax = Checkbutton(plotws, text = "Customize", variable = def_minmax, command = lambda:set_minmax(def_minmax.get()))        
        check_default_minmax.place(x = 10, y = 540)   
        
        Label(plotws, text='Choose Colormap Limits:').place(x = 120, y = 540)
        
        vmin = tki.IntVar(value = 0)
        vmax = tki.IntVar(value = 1.5)
        
        vmin_lbl = Label(plotws, text = 'vmin =')
        vmin_lbl.place(x = 120, y = 570)
        Enter_vmin = Entry(plotws, textvariable = vmin, width = 4)
        Enter_vmin.place(in_ = vmin_lbl, y = 0, relx = spacing)
        vmax_lbl = Label(plotws, text = 'vmax =')
        vmax_lbl.place(in_ = Enter_vmin, y = 0, relx = spacing)
        Enter_vmax = Entry(plotws, textvariable = vmax, width = 4)
        Enter_vmax.place(in_ = vmax_lbl, y = 0, relx = spacing)
        
        Enter_vmin.config(state = "disabled")
        Enter_vmax.config(state = "disabled")
        
        def set_minmax(boxon):
            if boxon % 2 == 1:
                Enter_vmin.config(state = "normal")
                Enter_vmax.config(state = "normal")
            else:
                Enter_vmin.config(state = "disabled")
                Enter_vmax.config(state = "disabled")
        
        conf_btn3 = Button(plotws, text='Confirm', command = lambda:destroy_widget_3(plotws, def_colormap.get(), def_figsize.get(), def_title.get(), \
        def_titlesize.get(), def_ticksize.get(), def_label.get(), def_labelsize.get(), def_minmax.get(), figure_x.get(), figure_y.get(), text_title.get('1.0','end-1c'), titlesize.get(), \
        ticksize.get(), label_x.get(), label_y.get(), labelsize.get(), vmin.get(), vmax.get(), cmap_to_use))
        
        conf_btn3.place(x = 120, y = 605)
        
        def destroy_widget_3(widget, boxon1, boxon2, boxon3, boxon4, boxon5, boxon6, boxon7, boxon8, figx, figy, title_name, titlesize, ticksize, labelx, labely,\
        labelsize, vmin, vmax, cmap_to_use):

            L = len(arr)
            if boxon1 % 2 == 0:
                cmap_to_use = "RdBu_r"
                
            if boxon2 % 2 == 0:
                figx = dim[1]/50
                figy = dim[0]/50
            else:
                figx = int(figx)
                figy = int(figy)
            
            if boxon4 % 2 == 0:
                titlesize = 14
            else:
                titlesize = int(titlesize)

            if boxon5 % 2 == 0:
                ticksize = 14
            else:
                ticksize = int(ticksize)

            if boxon7 % 2 == 0:
                labelsize = 14
            else:
                labelsize = int(labelsize)
            
            if boxon8 % 2 == 0:
                vmin = 0
                vmax = 1.5
            else:
                vmin = float(vmin)
                vmax = float(vmax)
        
            fig_anim = plt.figure(figsize=(figx, figy))
            if contr == 'X':
                ax_anim = plt.axes(xlim=(MinX, MaxX), ylim=(MinZ, MaxZ))
                nanarray = np.empty((dim[1], dim[0]))
                nanarray[:] = np.nan
                im = plt.imshow(nanarray, origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinZ, MaxZ])
                if boxon3 % 2 == 0:
                    ax_anim.set_title("Difference Map", fontsize = titlesize)
                else: 
                    ax_anim.set_title(title_name, fontsize = titlesize)
                if boxon6 % 2 == 0:
                    ax_anim.set_ylabel("Z", fontsize = labelsize)
                    ax_anim.set_xlabel("X", fontsize = labelsize)
                else: 
                    ax_anim.set_ylabel(labely, fontsize = labelsize)
                    ax_anim.set_xlabel(labelx, fontsize = labelsize) 
                ax_anim.tick_params(labelsize = ticksize)
            elif contr == 'Y': 
                ax_anim = plt.axes(xlim=(MinY, MaxY), ylim=(MinZ, MaxZ))
                nanarray = np.empty((dim[1], dim[0]))
                nanarray[:] = np.nan
                im = plt.imshow(nanarray, origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinY, MaxY, MinZ, MaxZ])
                if boxon6 % 2 == 0:
                    ax_anim.set_ylabel("Z", fontsize = labelsize)
                    ax_anim.set_xlabel("Y", fontsize = labelsize)
                else: 
                    ax_anim.set_ylabel(labely, fontsize = labelsize)
                    ax_anim.set_xlabel(labelx, fontsize = labelsize)
                if boxon3 % 2 == 0:
                    ax_anim.set_title("Difference Map", fontsize = titlesize)
                else: 
                    ax_anim.set_title(title_name, fontsize = titlesize) 
                ax_anim.tick_params(labelsize = ticksize)
            elif contr == 'Z': 
                ax_anim = plt.axes(xlim=(MinX, MaxX), ylim=(MinY, MaxY))
                nanarray = np.empty((dim[1], dim[0]))
                nanarray[:] = np.nan
                im = plt.imshow(nanarray, origin = "lower", cmap = cmap_to_use, vmin = vmin, vmax = vmax, extent = [MinX, MaxX, MinY, MaxY])
                if boxon6 % 2 == 0:
                    ax_anim.set_ylabel("Y", fontsize = labelsize)
                    ax_anim.set_xlabel("X", fontsize = labelsize)
                else: 
                    ax_anim.set_ylabel(labely, fontsize = labelsize)
                    ax_anim.set_xlabel(labelx, fontsize = labelsize)
                if boxon3 % 2 == 0:
                    ax_anim.set_title("Difference Map", fontsize = titlesize)
                else: 
                    ax_anim.set_title(title_name, fontsize = titlesize) 
                ax_anim.tick_params(labelsize = ticksize)
                
            def init():
                im.set_data(nanarray)
                #plt.axis('off')
                return [im]
        
            def animate(j):
                im.set_array(arr[j])
                #plt.axis('off')
                return [im]
        
            anim = FuncAnimation(fig_anim, animate, init_func=init,
                                    frames=L, interval=120, blit=True)
        
            anim.save(filename+'.gif', writer='imagemagick')
            
            plt.close()
            
            save_lbl = Label(ws, text = 'Saved!', foreground = 'green')    
            save_lbl.place(x = 420, y = 650)
            
            ws.after(2000, destroy_widget, save_lbl)
            plotws.destroy()
            
        
    def create_grid(arr, steps, contr, c):
        Nsteps_x = int(steps)
        arr = np.array(arr)
        
        if contr == "X":
            dx_new = (MaxX-MinX)/Nsteps_x
            Nsteps_y = (MaxZ-MinZ)/dx_new  
            x_axis = np.linspace(0, dim[1], Nsteps_x)
            y_axis = np.linspace(0, dim[0], int(Nsteps_y))        
        elif contr == 'Y':
            dx_new = (MaxY-MinY)/Nsteps_x
            Nsteps_y = (MaxZ-MinZ)/dx_new    
            x_axis = np.linspace(0, dim[1], Nsteps_x)
            y_axis = np.linspace(0, dim[0], int(Nsteps_y))
        elif contr == 'Z':
            dx_new = (MaxX-MinX)/Nsteps_x
            Nsteps_y = (MaxY-MinY)/dx_new    
            x_axis = np.linspace(0, dim[1], Nsteps_x)
            y_axis = np.linspace(0, dim[0], int(Nsteps_y))
            
        Grid = np.meshgrid(x_axis, y_axis)
        
        global full_coords
        full_coords = []
        
        for n_ind in range(len(arr)):    
            Tw10 = arr[n_ind,:,:].astype(np.uint8)
            ret, bin_10 = cv2.threshold(Tw10, 0.5, 255, cv2.THRESH_BINARY)
            
            cont_10, hierachy = cv2.findContours(bin_10, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    
            img_contours = np.zeros(bin_10.shape)
            cv2.drawContours(img_contours, cont_10, -1, (255,0,0), 2)
            
            lencont = []
            new_coords = []
            for j in range(len(Grid[0][0])):
                    for k in range(len(Grid[1])):
                        dist2 = []
                        for m in range(len(cont_10)):
                            lencont.append(len(cont_10[m]))
                        maxlen = max(lencont)
                        for m in range(len(cont_10)):
                            if lencont[m] == maxlen:
                                dist = cv2.pointPolygonTest(cont_10[m], tuple([Grid[0][0][j], Grid[1][k][0]]), False)
                            else:
                                dist2.append(cv2.pointPolygonTest(cont_10[m], tuple([Grid[0][0][j], Grid[1][k][0]]), False))                                
                        if dist > 0:
                            fail = 0
                            for l in range(len(dist2)):
                                if dist2[l] > 0:
                                    fail = 1
                            if fail == 0:
                                new_coords.append([Grid[0][0][j], Grid[1][k][0]])
            
            full_coords.append(new_coords)
        
        grid_lbl = Label(ws, text = 'Grid created!', foreground = 'green')    
        grid_lbl.place(x = col2_px, y = 130)
        
        ws.after(2000, destroy_widget, grid_lbl)
        
        if c == 0:
            base_name7 = Text(ws, height = 1, width = 30)
            base_name7.place(x = col2_px, y = 250)
            PhysCoord_btn = Button(ws, text = 'Get Coordinates', command = lambda:get_phys_coords(full_coords, contr, base_name7.get('1.0','end-1c')))
            PhysCoord_btn.place(x = col2_px, y = 280)
            
        global c5 
        c5 = 1
        
    def get_phys_coords(full_coords, contr, name):
        global phys_coords
        phys_coords = full_coords.copy()
        if contr == 'X':
            for j in range(len(full_coords)):
                savedcoords = []
                for k in range(len(full_coords[j])):
                    phys_coords[j][k][0] = MinX+dx*full_coords[j][k][0]
                    phys_coords[j][k][1] = MinZ+dz*full_coords[j][k][1]
                    savedcoords.append((float(phys_coords[j][k][0]),float(yy),float(phys_coords[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords)
        elif contr == 'Y':
            for j in range(len(full_coords)):
                savedcoords = []
                for k in range(len(full_coords[j])):           
                    phys_coords[j][k][0] = MinY+dy*full_coords[j][k][0]
                    phys_coords[j][k][1] = MinZ+dz*full_coords[j][k][1]
                    savedcoords.append((float(xx),float(phys_coords[j][k][0]),float(phys_coords[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords)
        elif contr == 'Z':
            for j in range(len(full_coords)):
                savedcoords = []
                for k in range(len(full_coords[j])):           
                    phys_coords[j][k][0] = MinX+dx*full_coords[j][k][0]
                    phys_coords[j][k][1] = MinY+dy*full_coords[j][k][1]
                    savedcoords.append((float(phys_coords[j][k][0]),float(phys_coords[j][k][1]), float(zz)))
                np.savetxt(name+str(j)+".txt", savedcoords)
                
        coord_lbl = Label(ws, text = 'Coordinates saved!', foreground = 'green')    
        coord_lbl.place(x = col2_px, y = 310)
        
        ws.after(2000, destroy_widget, coord_lbl)

    def create_random(arr, steps, contr, c): 
        arr = np.array(arr)
        num_points = int(steps)**2
        
        random_x = np.random.randint(dim[1], size = (len(arr), num_points))
        random_y = np.random.randint(dim[0], size = (len(arr), num_points))        

        global full_coords2
        full_coords2 = []
        
        for n_ind in range(len(arr)):    
            Tw10 = arr[n_ind,:,:].astype(np.uint8)
            ret, bin_10 = cv2.threshold(Tw10, 0.5, 255, cv2.THRESH_BINARY)
            
            cont_10, hierachy = cv2.findContours(bin_10, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    
            img_contours = np.zeros(bin_10.shape)
            cv2.drawContours(img_contours, cont_10, -1, (255,0,0), 2)
            
            lencont = []
            new_coords2 = []
            for j in range(num_points):
                dist2 = []
                for m in range(len(cont_10)):
                    lencont.append(len(cont_10[m]))
                maxlen = max(lencont)
                for m in range(len(cont_10)):
                    if lencont[m] == maxlen:
                        dist = cv2.pointPolygonTest(cont_10[m], tuple([float(random_x[n_ind, j]), float(random_y[n_ind, j])]), False)                
                    else:
                        dist2.append(cv2.pointPolygonTest(cont_10[m], tuple([float(random_x[n_ind, j]), float(random_y[n_ind, j])]), False))
                if dist > 0:
                    fail = 0
                    for l in range(len(dist2)):
                        if dist2[l] > 0:
                            fail = 1
                    if fail == 0:
                        new_coords2.append([float(random_x[n_ind,j]), float(random_y[n_ind,j])]) 
            
            full_coords2.append(new_coords2)
        
        grid_lbl = Label(ws, text = 'Points created!', foreground = 'green')    
        grid_lbl.place(x = col2_px, y = 220)
        
        ws.after(2000, destroy_widget, grid_lbl)
        
        if c == 0:
            base_name10 = Text(ws, height = 1, width = 30)
            base_name10.place(x = col2_px, y = 250)
            PhysCoord_randbtn = Button(ws, text = 'Get Coordinates', command = lambda:get_phys_randcoords(full_coords2, contr, base_name10.get('1.0','end-1c')))
            PhysCoord_randbtn.place(x = col2_px, y = 280)
        
        global c6
        c6 = 1
        
    def get_phys_randcoords(full_coords2, contr, name):
        global phys_coords2
        phys_coords2 = full_coords2.copy()
        if contr == 'X':
            for j in range(len(full_coords2)):
                savedcoords2 = []
                for k in range(len(full_coords[j])):
                    phys_coords2[j][k][0] = MinX+dx*full_coords2[j][k][0]
                    phys_coords2[j][k][1] = MinZ+dz*full_coords2[j][k][1]
                    savedcoords2.append((float(phys_coords2[j][k][0]),float(yy),float(phys_coords2[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords2)
        elif contr == 'Y':
            for j in range(len(full_coords2)):
                savedcoords2 = []
                for k in range(len(full_coords2[j])):           
                    phys_coords2[j][k][0] = MinY+dy*full_coords2[j][k][0]
                    phys_coords2[j][k][1] = MinZ+dz*full_coords2[j][k][1]
                    savedcoords2.append((float(xx),float(phys_coords2[j][k][0]),float(phys_coords2[j][k][1])))
                np.savetxt(name+str(j)+".txt", savedcoords2)
        elif contr == 'Z':
            for j in range(len(full_coords2)):
                savedcoords2 = []
                for k in range(len(full_coords2[j])):           
                    phys_coords2[j][k][0] = MinX+dx*full_coords2[j][k][0]
                    phys_coords2[j][k][1] = MinY+dy*full_coords2[j][k][1]
                    savedcoords2.append((float(phys_coords2[j][k][0]),float(phys_coords2[j][k][1]), float(zz)))
                np.savetxt(name+str(j)+".txt", savedcoords2)
                
        coord_lbl = Label(ws, text = 'Coordinates saved!', foreground = 'green')    
        coord_lbl.place(x = col2_px, y = 310)

    ws.protocol("WM_DELETE_WINDOW", ws.quit)
    ws.mainloop()
    ws.destroy()
