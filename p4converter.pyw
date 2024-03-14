#!/usr/bin/python
#P4 CONVERTER V1.0

import re
import tkinter as tk
import sys
import pyi_splash
from tkinter import filedialog, messagebox

root = tk.Tk()
root.withdraw()

pyi_splash.close()
res = messagebox.askokcancel("Step 1","Seleziona file P4 nuova")


if res:
    file_list = filedialog.askopenfilenames(title='Seleziona file da convertire', filetypes=[
                    ("file di piegatura P4", ".p4")
                ],initialdir="Y:\programmi_S4\P4_0643\production")
    if len(file_list) <=0:
         sys.exit(0)
    
    res = messagebox.askokcancel("Step 2","Seleziona cartella P4 vecchia")
    
    if res and len(file_list)>0:
        
        destdir = filedialog.askdirectory(initialdir="Y:\programmi_S4\P4_427\production\\")
        if len(destdir)<=0:
            sys.exit(0)
    else:
        
        sys.exit(0)
else:
    sys.exit(0)

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

    spessore=''
    refline=''
    X = 0.0
    Z = 0.0
    X1= 0.0
    Z1=0.0
    X2= 0.0
    Z2=0.0
    hasN= False
    hasN2 = False
    BEN1=False
    B1L=0.0
    G1=0.0
    filename = ''

    i = 0
    for text in lines:
        if text.find('COD')>-1: 
            ind = text.index("'")
            filename = text[ind+1:-1:]
            result += 'COD:' + filename + '\r\nREM:\r\n'
        elif text.find('MAT')>-1:
            if text.find("S ")>-1:
                ind = text.index("S ")
                spessore += "S" + text[ind+1:-1:].strip()
            elif text.find("SHEET") > -1:
                ind = text.index("SHEET ")
                spessore += "S" + text[ind+7] + "." + text[ind+8]
            else:
                return Exception.add_note("Spessore materiale non trovato")
        elif text.find('DIM:')>-1:
            result+='DIM:X'




            Xstart = text.index("X")+1
            Xend = text.index("Z")-1
            result +=  text[Xstart:Xend:].strip() + " Z"
            Zstart = text.index("Z")+1
            result +=  text[Zstart::].strip() + ' ' + spessore + '\r\n'

            X=float(text[Xstart:Xend:].strip())
            Z=float(text[Zstart::].strip())
        
        elif text.find('REF:')>-1: #REF LINE BUILD
            X1start = text.index("X1")+2
            X1end = text.index("Z1")-1
            Z1start = text.index("Z1")+2
            Z1end = text.index("X2")-1
            X2start = text.index("X2")+2
            X2end = text.index("Z2")-1
            Z2start = text.index("Z2")+2
            Z2end = text.index("X3")-1


            X1=float(text[X1start:X1end:].strip())
            X2=float(text[X2start:X2end:].strip())
            Z1=float(text[Z1start:Z1end:].strip())
            Z2=float(text[Z2start:Z2end:].strip())


            refline += 'REF:X1:' +  text[X1start:X1end:].strip()
            refline += ' X2:' + text[X2start:X2end:].strip()
            refline += ' Z1:' + text[Z1start:Z1end:].strip()
            refline += ' Z2:' + text[Z2start:Z2end:].strip()

            if text.find(" N1") > 0: # no scantonatura su lato 1 (SX)
                hasN = True
                refline += ' G1:-80 RS RA CZ'
            elif text.find(" N2") > 0: # no scantonatura su lato 2 (a destra)
                hasN2 = True
                refline += ' G1:-80 RS RA CZ'
            elif text.find(" N") > 0:
                hasN = True
                refline += ' G1:-80 N RS RA CZ'
            else:
                hasN=False
                refline += ' G1:-80 RS RA CZ'
            # add G value from bending lines
            # formula -> (0.5*X-X1)*.5
            #
            #  refline += 'G1:' + text[Xstart:Xend:].strip() -text[X1start:X1end].strip()
            
            

            
            result += refline

        elif text.find('ROT:')>-1:
            text = "".join(text.split())
            rotline='\r\nBEN:'
            benno = text.index(":")+2
            rotline+=text[benno:benno+1]
            result += rotline
            
            side=int(text[benno:benno+1])

            if side == 1:
                BEN1 = True
            else:
                BEN1 = False


            #rotline+=
        elif text.find('BEN')>-1:
            text = "".join(text.split())
            if text.find('BEN:')>-1:
                
                y = re.search("L\d+\.\d+",text)
                rotangle = ' +' + text[y.start()+1:y.end()]
                
                if BEN1 == True:
                    B1L = float(text[y.start()+1:y.end()])
                
                x=re.search("A\d+\.\d",text)
            
                if x!=None:
                    
                    rotangle += ' ' + text[x.start(): x.end()] + ' '
                else:
                    rotangle += ' A90 '
            elif text.find('BEN-:')>-1:
                y = re.search("L\d+\.\d+",text)
                rotangle = ' -' + text[y.start()+1:y.end()]

                if BEN1 == True:
                    B1L = float(text[y.start()+1:y.end()])

                x=re.search("A\d+\.\d",text)
            
                if x!=None:
                    rotangle += ' ' + text[x.start(): x.end()] + ' '
                else:
                    rotangle += ' A90 '
            if float(spessore[1:])>= 2:
                rotangle += 'RH AC4'
            else:
                rotangle += 'RI AC4'
            result += rotangle
        elif text.find('END:')>-1 and len(text)==4:
            result += '\r\nMCM:MQ8\r\nEND'
        i = i+1
        
    if abs(abs(X1) - abs(0.5*X-5)) > 5:
        if X1-0.5*X>0:
            G1=(0.5*X+B1L)-X1
        else:
            G1=0.5*X-X1
    elif abs(abs(X1) - abs(0.5*X-5)) < 5:
        G1=(0.5*X+B1L)-X1


    if not hasN and hasN2:
        result = result.replace('G1:-80','G1:'+str(round(G1, 1))+' N')
    elif not hasN:
        result = result.replace('G1:-80','G1:'+ str(round(G1, 1)))
        

    return result
try:
    for file_path in file_list:

        out=p4converter(file_path)
            
        f = open(destdir+"/"+ getFilename(file_path) +".P4", "w", encoding='ansi')
        f.write(out)
        f.close()
    messagebox.showinfo(title="Completato", message="Conversione completata con successo")
except Exception as e:
    messagebox.showerror(title="Errore", message="Errore di conversione. Verificare programmi")
    print(e)