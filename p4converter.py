#!/usr/bin/python
#P4 CONVERTER V1.0

import re
import tkinter as tk
from tkinter import filedialog, messagebox

root = tk.Tk()
root.withdraw()

res = messagebox.askokcancel("Question","Seleziona file P4 nuova")
if res:
    file_list = filedialog.askopenfilenames()
    if len(file_list) <=0:
        exit()
    
    res = messagebox.askokcancel("Question","Seleziona cartella P4 vecchia")

    if res & len(file_list)>0:
        destdir = filedialog.askdirectory()
        if len(destdir)<=0:
            exit()
    else:
        exit()
else:
    exit()

def getFilename(file_path):
    filename_index = file_path.rfind("/")
    if filename_index > -1:
        filename = file_path[filename_index+1:-3]
    return filename

def p4converter(file_path):
    with open(file_path) as f:
        read_data = f.read()

    #print(read_data)
    result = ''


    lines = read_data.splitlines()

    # Nome programma
    spessore=''
    refline=''
    i = 0
    for text in lines:
        if text.find('COD')>-1: 
            ind = text.index("'")
            result += 'COD:' + text[ind+1:-1:] + '\nREM:\n'
        elif text.find('MAT')>-1:
            ind = text.index("S ")
            spessore += "S" + text[ind+1:-1:].strip()
        elif text.find('DIM:')>-1:
            result+='DIM:X'
            Xstart = text.index("X")+1
            Xend = text.index("Z")-1
            result +=  text[Xstart:Xend:].strip() + " Z"
            Zstart = text.index("Z")+1
            result +=  text[Zstart::].strip() + ' ' + spessore + '\n'
        
        elif text.find('REF:')>-1: #REF LINE BUILD
            X1start = text.index("X1")+2
            X1end = text.index("Z1")-1
            Z1start = text.index("Z1")+2
            Z1end = text.index("X2")-1
            X2start = text.index("X2")+2
            X2end = text.index("Z2")-1
            Z2start = text.index("Z2")+2
            Z2end = text.index("X3")-1



            refline += 'REF:X1:' +  text[X1start:X1end:].strip()
            refline += ' X2:' + text[X2start:X2end:].strip()
            refline += ' Z1:' + text[Z1start:Z1end:].strip()
            refline += ' Z2:' + text[Z2start:Z2end:].strip()
            # add G value from bendings
            refline += ' G1:-80 RS RA CZ'
            result += refline

        elif text.find('ROT:')>-1:
            text = "".join(text.split())
            rotline='\nBEN:'
            benno = text.index(":")+2
            rotline+=text[benno:benno+1]
            

            result += rotline
            #rotline+=
        elif text.find('BEN')>-1:
            text = "".join(text.split())
            if text.find('BEN:')>-1:
                
                y = re.search("L\d+\.\d+",text)
                rotangle = ' +' + text[y.start()+1:y.end()]
            
                x=re.search("A\d+\.\d",text)
            
                if x!=None:
                    
                    rotangle += ' ' + text[x.start(): x.end()] + ' '
                else:
                    rotangle += ' A90 '
            elif text.find('BEN-:')>-1:
                y = re.search("L\d+\.\d+",text)
                rotangle = ' -' + text[y.start()+1:y.end()]
            
                x=re.search("A\d+\.\d",text)
            
                if x!=None:
                    rotangle += ' ' + text[x.start(): x.end()] + ' '
                else:
                    rotangle += ' A90 '
            if float(spessore[1:])>= 2:
                rotangle += 'RH AC2'
            else:
                rotangle += 'RI AC2'
            result += rotangle
        elif text.find('END:')>-1 and len(text)==4:
            result += '\nMCM:MQ8\nEND'
        i = i+1
    return result

for file_path in file_list:

    out=p4converter(file_path)
        
    f = open(destdir+"/"+ getFilename(file_path) +"_OLD.P4", "w")
    f.write(out)
    f.close()