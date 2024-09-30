#!/usr/bin/env python3

from difflib import SequenceMatcher
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
import csv
import os
import shutil
import sys
import tempfile

def main():
   args = getargs()
   root = Mainwindow()
   root.mainloop()

#GUI Classes
class Mainwindow(tk.Tk):
   def __init__(self):
      super().__init__()
      self.category = Category()
      self.tframe = Transactf(self, self.category)
      self.cats = Catf(self, self.category)
      self.optst = Optft(self, self.category)
      self.optsc = Optfc(self, self.category)

class Transactf(ScrolledText):
   def __init__(self, parent, category):
      super().__init__(parent)
      self.parent=parent
      self.catdat = category
      self.transactions = []
      self.labeledlist = {}
      self.grid(row=0, column=1, sticky='nsew')
      self.bind('<Button-3>', self.textclick)
#self.bind("<Button-1>", lambda e: "break")
      self.bind("<Button-2>", lambda e: "break")
      self.bind("<Key>", lambda e: "break")
      self.readtransact()
      self.loadtransact()
      
   def reloadtransact(self):
      self.clearwindow()
      self.loadtransact()

   def clearwindow(self):
      for tag in self.tag_names():
         self.tag_remove(tag, "1.0", "end")
      self.delete("1.0", "end")

   def loadtransact(self):
      linenum = 1
      for l in self.transactions:
         tagname = "line" + str(linenum)
         self.insert(tk.END, l[0])
         self.insert(tk.END, ', ')
         if str(linenum) in self.labeledlist:
            self.insert(tk.END, self.labeledlist[str(linenum)], tagname)
         else:
            cat = self.catdat.bestcatmatch(l[1])
            self.insert(tk.END, cat, tagname)
         self.insert(tk.END, ', ')
         self.insert(tk.END, l[2])
         self.insert(tk.END, ', ')
         self.insert(tk.END, l[1])
         self.insert(tk.END, '\n')
         if str(linenum) in self.labeledlist:
            self.tag_configure(tagname,background='green')
         else:
            self.tag_configure(tagname,background='red')
         linenum = linenum + 1

#TODO undo
   def textclick(self, event):
      index = event.widget.index("@%d,%d" % (event.x, event.y))
      (row, col) = index.split('.')
      if 0 < self.parent.cats.selline <= len(self.catdat.catlist):
         newcat = self.catdat.catlist[self.parent.cats.selline - 1]
         self.changecat(row, newcat)

   def editcat(self, oldcat, newcat):
      linenum = 1
      for l in self.transactions:
         tagname = "line" + str(linenum)
         place = self.tag_ranges(tagname) #should be just one range
         cat = self.get(place[0], place[1])
         if oldcat == cat:
            self.changecat(linenum, newcat)
         linenum = linenum + 1


   def changecat(self, linenum, newcat):
      tagname = "line" + str(linenum)
      place = self.tag_ranges(tagname) #should be just one range
      oldcat = self.get(place[0], place[1])
      self.delete(place[0], place[1]) 
      self.insert(place[0], newcat, tagname) 
      self.labeledlist[str(linenum)] = newcat
      self.tag_configure(tagname, background='green')

   def readtransact(self):
      global IFILE
      with open (IFILE) as infile:
         self.rawtransactions = infile.readlines()
         linenum = 1
         for l in self.rawtransactions:
            ll = [ '"{}"'.format(x) for x in next(csv.reader([l], delimiter=',', quotechar='"')) ]
            if linenum == 1 and '/' not in ll[0]: #header line
               self.transactheader = l
            else:
               newll = []
               for s in ll:
                  if s.startswith('"') and s.endswith('"'):
                     s= s[1:-1]
                  newll.append(s)
               self.transactions.append(newll)
            linenum = linenum + 1

   def writetransact(self):
      global IFILE, OFILE
      if OFILE == '':
         (base, ext) = os.path.splitext(IFILE)
         OFILE = base + "-cat"
         if len(ext) > 0:
            OFILE = OFILE + ext
      with open(OFILE, 'w') as ofile:
         if len(self.transactheader) != 0:
            ofile.write(self.transactheader)
         linenum = 1
         first = True
         for l in self.rawtransactions:
            if first == False or len(self.transactheader) == 0:
               tagname = "line" + str(linenum)
               place = self.tag_ranges(tagname) #should be just one range
               print(tagname, place, l)
               cat = self.get(place[0], place[1])
               ofile.write(l.rstrip())
               ofile.write(',"')
               ofile.write(cat)
               ofile.write('"\n')
               linenum = linenum + 1
            first = False


class Catf(ScrolledText):
   def __init__(self, parent, category):
      global transactions
      super().__init__(parent)
      self.parent=parent
      self.catdat = category
      self.selline = 0
      self.grid(row=1, column=1, sticky='nsew')
      self.bind('<Button-3>', self.textclick)
#self.bind("<Button-1>", lambda e: "break")
      self.bind("<Button-2>", lambda e: "break")
      self.bind("<Key>", lambda e: "break")
      self.putcatsinwindow()

   def putcatsinwindow(self):
      cats = self.catdat.getcatlist()
      linenum = 1
      for c in cats:
         tagname = "line" + str(linenum)
         self.tag_configure(tagname)
         self.insert(tk.END, c, tagname)
         self.insert(tk.END, '\n')
         linenum = linenum + 1

   def clearwindow(self):
      for tag in self.tag_names():
         self.tag_remove(tag, "1.0", "end")
      self.delete("1.0", "end")

   def resetcatlist(self):
      self.clearwindow()
      self.putcatsinwindow()

   def textclick(self, event):
      index = event.widget.index("@%d,%d" % (event.x, event.y))
      (row, col) = index.split('.')
        #set all tags to normal background
      taglist = self.tag_names()
      for tag in taglist:
         self.tag_configure(tag,foreground='black')
      tagname = "line" + str(row)
      self.tag_configure(tagname,foreground='blue')
      self.selline = int(row)
#TODO: can selline be larger than number of cats in window?


class Optft(tk.Frame):
   def __init__(self, parent, category):
      global transactions
      super().__init__(parent, width=200)
      self.parent=parent
      self.catdat = category
      self.grid(row=0, column = 0, sticky='nsew')
      recalc = tk.Button(self,text="recalc", command=self.recalc)
      recalc.grid(row=0,column=0)
      adds = tk.Button(self,text="add match", command=self.addmatch)
      adds.grid(row=1,column=0)
      save = tk.Button(self,text="save", command=self.save)
      save.grid(row=2,column=0)
      quitbutton = tk.Button(self,text="quit")
      quitbutton.grid(row=3,column=0)

#TODO undo
   def addmatch(self):
      new = self.parent.tframe.get(tk.SEL_FIRST, tk.SEL_LAST).lower()
      catnum = self.parent.cats.selline
      if catnum != 0:
         self.catdat.addmatch(catnum - 1, new)

#TODO undo
   def recalc(self):
      self.parent.tframe.reloadtransact()

   def save(self):
      self.catdat.writecatfile()
      self.parent.tframe.writetransact()

class Optfc(tk.Frame):
   def __init__(self, parent, category):
      global transactions
      super().__init__(parent, width=200)
      self.parent=parent
      self.catdat = category
      self.editingc=False
      self.editingm=False
      self.grid(row=1, column = 0, sticky='nsew')
      self.columnconfigure(0,weight=1)
      self.rowconfigure(5,weight=5)
      self.edita = tk.Button(self,text="add cat", command=self.addcatsbutton)
      self.edita.grid(row=0,column=0)
      self.editd = tk.Button(self,text="del cat", command=self.delcatsbutton)
      self.editd.grid(row=1,column=0)
      self.editc = tk.Button(self,text="edit cat", command=self.editcatsbutton)
      self.editc.grid(row=2,column=0)
      self.editm = tk.Button(self,text="edit match", command=self.editmatchbutton)
      self.editm.grid(row=3,column=0)
      self.edits = tk.Button(self,text="sort", command=self.sortcats)
      self.edits.grid(row=4,column=0)
      self.edith = tk.Button(self,text="help", command=self.helpbutton)
      self.edith.grid(row=5,column=0,sticky='s')

#TODO undo
   def addcatsbutton(self):
      y = Catedit(self.parent, self.catdat, 0)

#TODO undo
   def delcatsbutton(self):
      pos = self.parent.cats.selline
      if pos > 0 and len(self.catdat.catlist) >= pos:
         cat = self.catdat.catlist[pos - 1]
         self.catdat.delfromcatlist(pos - 1) #line to index
         self.parent.tframe.editcat(cat, ' ')
         self.parent.cats.resetcatlist()
#TODO Error window that cat not selected

   def editcatsbutton(self):
      pos = self.parent.cats.selline
      if pos > 0:
         y = Catedit(self.parent, self.catdat, pos)
#TODO Error window that cat not selected

   def editmatchbutton(self):
      pos = self.parent.cats.selline
      if pos > 0:
         y = Matchedit(self.parent, self.catdat, pos)
#TODO Error window that cat not selected

#TODO undo
   def sortcats(self):
      print("implement category sort")

   def helpbutton(self):
      y = Helpwin(self)

#TODO undo
class Catedit(tk.Toplevel):
   def __init__(self, root, category, position):
      super().__init__()
      self.root = root
      self.catdat = category
      self.position = position
      self.wm_title("Category Editor")
      self.cancelb = tk.Button(self, text="cancel", command=self.cancel)
      self.cancelb.grid(row=0,column=0)
      self.okb = tk.Button(self, text="OK", command=self.ok)
      self.okb.grid(row=0,column=1)
      self.tbox = tk.Entry(self)
      self.tbox.grid(row=1,column=0,columnspan=2)
      self.tbox.bind("<Return>", self.enterpressed)
      if self.position > 0:  #editing an existing
         self.tbox.insert(tk.END, self.catdat.catlist[position - 1])

   def enterpressed(self, key):
      self.ok()

   def ok(self):
      if self.position == 0:
         self.catdat.addtocatlist(self.tbox.get())
      else:
         self.catdat.changecat(self.position, self.tbox.get())
      self.root.cats.resetcatlist()
      self.destroy()
      self.update()

   def cancel(self):
      self.destroy()
      self.update()

#TODO undo
class Matchedit(tk.Toplevel):
   def __init__(self, root, category, catline):
      super().__init__()
      self.root = root
      self.catdat = category
      self.wm_title("Match Editor")
      self.cancelb = tk.Button(self, text="cancel", command=self.cancel)
      self.cancelb.grid(row=0,column=0)
      self.okb = tk.Button(self, text="OK", command=self.ok)
      self.okb.grid(row=0,column=1)
      self.tbox = ScrolledText(self, height=15, width=60)
      self.tbox.grid(row=1,column=0,columnspan=2)
      self.tbox.bind("<Return>", self.enterpressed)
      self.catpos = catline - 1
      matches = self.root.category.getcurrentmatches(self.catpos)
      for e in matches:
         self.tbox.insert(tk.END, e)
         self.tbox.insert(tk.END, '\n')

   def enterpressed(self, key):
      self.ok()

   def ok(self):
#self.root.category.addtocatlist(self.tbox.get())
#      self.root.cats.resetcatlist()
      matches = self.tbox.get('1.0', tk.END).splitlines()
      self.catdat.setcatmatches(self.catpos, matches)
      self.destroy()
      self.update()

   def cancel(self):
      self.destroy()
      self.update()

class Helpwin(tk.Toplevel):
   def __init__(self, root):
      super().__init__()
      global HELPSTRING
      self.root = root
      self.okb = tk.Button(self, text="OK", command=self.ok)
      self.okb.grid(row=0,column=1)
      self.hbox = ScrolledText(self, height=15, width=60)
      self.hbox.grid(row=1,column=0,columnspan=2)
      self.hbox.insert('1.0', HELPSTRING)

   def ok(self):
      self.destroy()
      self.update()

#Data Classes
class Category():
   catlist = []
   catmatch = []   #list of 2 element lists [match, cat], match always lower case
   def __init__(self):
      self.readcatfile()
      self.changed=False

   def readcatfile(self):
      global CATEGORIES
      try:
         with open (CATEGORIES) as infile:
            for l in infile:
               ll = [ '"{}"'.format(x) for x in next(csv.reader([l], delimiter=',', quotechar='"')) ]
               newll = []
               for s in ll:
                  if s.startswith('"') and s.endswith('"'):
                     s= s[1:-1]
                  newll.append(s)
               if len(newll) > 0:
                  self.addtocatlist(newll[0])
                  if len(newll) > 1:
                     for match in newll[1:]:
                        self.addcatmatch(match, newll[0])
      except Exception as error:
         tk.messagebox.showerror('Read category file', error)

   def writecatfile(self):
#copy category file to /tmp/tmpfilename
      if self.changed == True:
         try:
            tmpdir = tempfile._get_default_tempdir()
            temp_name = "categorymap_" + next(tempfile._get_candidate_names())
            tmpfile = os.path.join(tmpdir, temp_name)
            shutil.copyfile(CATEGORIES, tmpfile)
   #write new category file
            f = open(CATEGORIES, 'w')
            for c in self.catlist:
               f.write('"'+c+'"')
               for cm in self.catmatch:
                  if cm[1] == c:
                     f.write(',"'+cm[0]+'"')
               f.write('\n')
         except Exception as error:
            tk.messagebox.showerror('Write Error', error)
            #print('error ', error)

   def changecat(self, catpos, newcat):
      oldcat = catlist[catpos]
      catlist[catpos] = newcat
      newmatch = []
      for e in catmatch:  
         if e[1] == oldcat:
            newmatch.append(e[0], newcat)
         else:
            newmatch.append(e)
      self.catmatch = newmatch
      self.changed = True

   def addcatmatch(self, match, cat):
      self.catmatch.append([match, cat])
      self.changed = True

   def bestcatmatch(self,expense):
      bestscore = 0
      retcat = ' '
      for cm in self.catmatch:
         score = SequenceMatcher(None, expense.lower(), cm[0]).ratio()
         if score > bestscore:
            bestscore = score
            retcat = cm[1]
      return retcat

   def getcurrentmatches(self, catpos): #return matches for selected category
      cat = self.catlist[catpos]
      ret = []
      for e in self.catmatch:
         if e[1] == cat:
            ret.append(e[0])
      return ret

   def setcatmatches(self, catpos, newmatches):
      cat = self.catlist[catpos]
      newmatch = []
      for e in self.catmatch:
         if e[1] != cat:
            newmatch.append(e)
      for e in newmatches:
         if len(e) > 0:
            newmatch.append([e, cat])
      self.catmatch = newmatch   #replace with new array
      self.changed = True

   def addmatch(self, catnum, match):
      cat = self.catlist[catnum]
      self.addcatmatch(match, cat)
      self.changed = True

   def delfromcatlist(self, pos):
      del self.catlist[pos]
      self.changed = True

   def addtocatlist(self, cat):
      self.catlist.append(cat)
      self.changed = True

   def getcatlist(self):
      return self.catlist


#initial guess of category


STATEFILE="savestate"
OFILE=""
CATEGORIES="categorymap"
def getargs():
   global STATEFILE, OFILE, IFILE
   args = {}
   numargs = len(sys.argv)
   if numargs < 2:
      usage()
   if sys.argv[1] == '-s':
      if numargs < 4:
         usage()
      STATEFILE = sys.argv[2]
      IFILE = sys.argv[3]
      if numargs == 5:
         OFILE = sys.argv[4]
   else:
      IFILE = sys.argv[1]
      if numargs == 3:
         OFILE = sys.argv[2]

def usage():
   print("categorizer.py [-s statefile] ifile [ofile]")
   exit(1)

HELPSTRING=\
"""\
Usage:  categorizer.py expenses_file
Expenses file is a .csv, with fields: 
   Date,Description,Amount,Balance,Post Date

On startup, the expenses file is read and put into the top window.

The file categorymap is read, and categories are listed in the bottom window.

An initial guess of category is made for each of the expenses.  This guess is highlighted in red.

Using the right mouse button, an expense can be highlighted.  Once one is highlighted, a right click on a line in the expense windwo will assign that category to that expense.

Strings can be selected with the left mouse button in the expense window.  If one is selected, and the 'add match' button is pressed, that string will be added to the list of match strings for the selected category.

Categories can be added, deleted, or the name edited.  The set of match strings for a category can be edited.  If any of these change, the categorymap file will be written when the save button is pressed.

Pressing the recalc button will recheck all the default assigned categories to see if they are still assigned to the best matching category.  Any manually assigned category will not be changed.
"""

main()
