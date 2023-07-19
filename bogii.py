
import time
import twl
#import tkinter.ttk
# The tkinter includes will allow us to draw a representation of the current board in
# color to represent the order of letters
import tkinter as tk
from tkinter import Tk, Label, Button
from tkinter.ttk import *
from colorama import Fore, Back, Style
import numpy as np

# The string defined blow, should be 16 characters in length, representing four
# rows of four characters per row characteristic of a typical Boggle board.
ltrlist = "ptnplyrahlettotd"

# Below, find a dictionary defining the assigned Boggle values associated with the dice
# in a standard games of Boggle
score_dict = {
'a': 1,
'b': 2,
'c': 3,
'd': 2,
'e': 1,
'f': 4,
'g': 2,
'h': 4,
'i': 1,
'j': 0,
'k': 0,
'l': 2,
'm': 3,
'n': 1,
'o': 1,
'p': 3,
'q': 0,
'r': 1,
's': 1,
't': 1,
'u': 1,
'v': 0,
'w': 0,
'x': 0,
'y': 4,
'z': 10
}

global_choices = {}
grid = {}

# "chain", the list below defined (with the 4x4 row board being defined from top left to bottom right counting
# from 0 to 15 (HEX 'F')
chain = ["145","04562","13567","267","01589","0124689A", "123579AB","236AB","459CD","4568ACDE","5679B","67AEF","89D","89ACE","9ABDF","ABE"]
chainDone = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
chainOrder = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

results = {}

to_delete = []

wordcounter = 0

class MindBoggle():
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.toggleSort = True

        self.squaresOrder = {}
        self.board = np.zeros((4,4))

        self.hiPriList = tk.Listbox(master,font="Courier 18")
        self.hiPriList.pack(fill=tk.BOTH,pady=10, padx=10,side=tk.LEFT)

        self.loPriList = tk.Listbox(master,font="Courier 18")
        self.loPriList.pack(fill=tk.BOTH,pady=10, padx=10,side=tk.BOTTOM)

        self.hiPriIndex = 1
        self.hiList = []
        self.loList = []
        self.lwl = []
        self.chainOrder = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.letterCanvas = tk.Canvas(master, background="white",width=500,height=500)
        self.letterCanvas.create_rectangle(1, 1, 290, 290)
        self.letterCanvas.pack(fill=tk.BOTH, side=tk.RIGHT)
        colo = "grey"
        for y in range(4):
            for x in range(4):
                if x % 2 == 1:
                    colo = "grey"
                else:
                    colo = "grey"
                self.board[x,y] = self.letterCanvas.create_rectangle((x * 60) + ((x + 1) * 10),((y * 60) + ((y + 1) * 10),((x + 1) * 70),((y + 1) * 70)), fill=colo)

        self.hiPriList.bind('<Return>', lambda event: self.removeItemFromHi())
        self.hiPriList.bind('<<ListboxSelect>>', self.onSelect())
        self.wholeWordText = self.letterCanvas.create_text(10, 300, anchor=tk.NW, fill="black", font="Courier 44", text="")
        self.firstPass = 1
        self.listOfWords = {}
        super().__init__()
        self.run_it()
        #self.do_full_lookup()


    def onSelect(self):
        if hasattr(self, 'wholeWordText'):
            self.newSelection()


    def colorGrid(self):
        colo = "grey"
        for w in range(16):
            self.chainOrder[w] = 0

        for w in range(16):
            if w < len(self.targetSquaresOrder):
                box = int(self.targetSquaresOrder[w],16)
                self.chainOrder[box] = w+1

        d = len(self.targetSquaresOrder)
        mid = self.targetSquaresOrder[2:d-1]
        for y in range(4):
            for x in range(4):
                sq = ((y*4)+x)
                if self.chainOrder[sq] == 1:
                    colo = "green"
                elif self.chainOrder[sq] == 2:
                    colo = "pink"
                elif self.chainOrder[sq] == d:
                    colo = "red"
                elif self.chainOrder[sq] >2 and self.chainOrder[sq] < d:
                    colo = "lavenderblush"
                else:
                    colo = "grey"

                xa = (x * 60) + ((x + 1) * 10)
                ya = (y * 60) + ((y + 1) * 10)
                xb = ((x + 1) * 70)
                yb = ((y + 1) * 70)
                rect = self.letterCanvas.create_rectangle((xa,ya,xb,yb),fill=colo)
                #rect = self.letterCanvas.create_rectangle((x * 60) + ((x + 1) * 10),((y * 60) + ((y + 1) * 10),((x + 1) * 70),((y + 1) * 70)), fill=colo)
                oval = self.letterCanvas.create_oval(xa+15,ya+15,xb-15,yb-15,fill="black")
                order = self.chainOrder[sq]
                if (order > 0):
                    self.letterCanvas.create_text(((xa+xb)//2),((ya+yb)//2), anchor=tk.CENTER, fill="white", font="Courier 22", text=str(self.chainOrder[sq]))
                self.board[x, y] = rect

        end =1

    def removeItemFromHi(self):
        #sel = self.hiPriList.curselection()
        #for index in sel[::-1]:
        #    self.hiPriList.delete(index)
        self.removeCurrentRootWord()
        self.newSelection()

    def getVerbNoun(self, wrd):
        result = []
        if wrd[-2:] == "es":
            result.insert(0,wrd[:-2])
            result.insert(0, wrd[:-1])
            result.insert(0, wrd)
        else:
            if wrd[-1:] == "s":
                result.insert(0, wrd[:-1])
                #result.insert(0,wrd)
            else:
                result.insert(0,wrd)
        return result

    def newSelection(self):
        self.choices = ""
        self.lwl_set = []

        self.letterCanvas.itemconfigure(self.wholeWordText, text=self.choices)
        self.hiPriList.select_set(0)
        if not hasattr(self, 'firstPass') or self.firstPass == 0:
            self.firstPass = 1
        else:
            curr=0
            r = self.hiPriList.get(curr)
            sword = r.split(",",2)
            keyFieldNum = 1
            #if self.toggleSort:
                #keyFieldNum = 3
            newSelWord = sword[keyFieldNum]
            newEncodedWord = sword[keyFieldNum+1]
            self.vrbno = self.getVerbNoun(newSelWord)
            for v in self.vrbno:
                self.makeAlternalist(v)
            self.lwl_set = set(self.lwl)
            if len(self.lwl_set):
                for c in self.lwl_set:
                    self.choices = self.choices + c + "\n"
            self.letterCanvas.itemconfigure(self.wholeWordText,text=self.choices)
            self.targetSquaresOrder = self.squaresOrder[newSelWord]
            self.colorGrid()

    def makeAlternalist(self,verbnoun):
        version_a = verbnoun
        version_b = verbnoun + "s"
        version_c = verbnoun + "ed"
        version_d = verbnoun + "er"
        version_e = verbnoun + "r"
        version_f = "re" + verbnoun
        version_g = verbnoun + "ing"
        version_h = verbnoun + "es"
        wrd_idx= 1

        item_num = 0
        self.to_pop = []
        self.lwl_too = []
        if version_a in self.listOfWords.keys():
            self.lwl.insert(0,version_a)
            self.to_pop.insert(0,item_num)
        if version_b in self.listOfWords.keys():
            self.lwl.insert(0, version_b)
            self.to_pop.insert(0, item_num)
        if version_c in self.listOfWords.keys():
            self.lwl.insert(0,version_c)
            self.to_pop.insert(0, item_num)
        if version_d in self.listOfWords.keys():
            self.lwl.insert(0,version_d)
            self.to_pop.insert(0, item_num)
        if version_e in self.listOfWords.keys():
            self.lwl.insert(0,version_e)
            self.to_pop.insert(0, item_num)
        if version_f in self.listOfWords.keys():
            self.lwl.insert(0,version_f)
            self.to_pop.insert(0, item_num)
        if version_g in self.listOfWords.keys():
            self.lwl.insert(0, version_g)
            self.to_pop.insert(0, item_num)
        if version_h in self.listOfWords.keys():
            self.lwl.insert(0, version_h)
            self.to_pop.insert(0, item_num)


    def removeCurrentRootWord(self):
        for item in self.lwl_set:
            entry = self.listOfWords[item]
            self.hiList.remove(entry)
            for i in range(self.hiPriList.size()):
                sample = self.hiPriList.get(i)
                if sample == entry:
                    self.hiPriList.delete(i)
                    break
            del self.listOfWords[item]
        self.lwl.clear()
        self.lwl_set.clear()
        self.choices = ""
        self.hiPriList.select_set(0)
        self.hiPriList.focus_set()


    def makeGrid(self):
        global grid, ltrlist
        grid = list (ltrlist)
        print("Letter List = " + str(grid))

    def print_word_directions(self):
        print("print_word_directions()")

    def extractWordFromLabel(self,labl):
        sword = labl.split(", ", 3)
        return sword[1]



    def run_it(self):
        global chainDone
        global results

        self.total_score =0
        self.makeGrid()
        self.refreshChain()

        self.justBeginning = 1
        self.loPriIndex = 0
        start = time.time()
        for j in range(16):
            if j >= 3:
                self.justBeginning = 0
            i = 15 - j
            hpos = hex(i)
            ipos = i
            s = str(hpos)
            ltr = s[2]
            final_word = ltr
            chainDone[ipos] = 1
            self.findNextLetter(final_word, chainDone)
            #for w in to_delete:
            #    results.pop(w)
            chainDone[ipos] = 0

        self.fillListboxes()
        self.hiPriList.select_set(0)
        self.hiPriList.focus_set()
        if hasattr(self, 'wholeWordText'):
            self.newSelection()


    def setTargetWord(w, self):
        self.targetWord = w
        self.targetWordIndex = 0


    def deleteVisibleLetters(self):
        for i in range(16):
            visibleLetters[i] = 0

    def refreshChain(self):
        global chainDone
        chain = ["145","04562","13567","267","01589","0124689A", "123579AB","236AB","459CD","4568ACDE","5679B","67AEF","89D","89ACE","9ABDF","ABE"]
        chainDone = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    def findNextLetter(self, chainStr, chainDone):
        lastLetterofNumber = int(chainStr[-1], base=16)
        possibles = chain[(int(lastLetterofNumber))]
        for nextdigit in possibles:

            idx = int(nextdigit,16)

            if chainDone[idx] == 1:
                continue

            if len(chainStr) <= 8:
                chainDone[idx] = 1
                chainStr += nextdigit
                #print("ADD Lead: " + str(nextdigit))
                if len(chainStr) >= 3:
                    if self.check_word(chainStr) == 1:
                        print(chainStr)
                self.findNextLetter(chainStr,chainDone)

                # Remove added letter
                #print("DROP Lead: " + str(chainStr[:-1]))

                chainStr = chainStr[:-1]
                chainDone[idx] = 0


    def check_word(self, chainStr):
        global results
        global grid
        global score_dict
        global to_delete
        final_string = ""
        final_score = 0
        chn=""


        for e in chainStr:
            ltr = int(e, base=16)
            final_string = final_string + grid[ltr]
            final_score = final_score + score_dict.get(grid[ltr])

        final_check_string = final_string.replace("q","qu",1)
        if twl.check(final_check_string) == True:
            self.squaresOrder[final_check_string] = chainStr

            prev_singular_pts = 0

            if final_string[-1:] == 's' and len(final_string) > 3:
                if final_string[0:-1] in results:
                    prev_singular_pts = results[final_string[0:-1]]

            if not final_string in results:
                final_len = len(final_string)
                final_score = final_score + ((final_len - 3) * 10)
                results[final_string] = final_score

                present_str = str(final_score).zfill(3) + "," + final_string + ","
                if  self.toggleSort:
                    present_str += chainStr

                if final_len >= 3:
                    self.hiList.insert(self.hiPriIndex,present_str)
                    slist = present_str.split(",")
                    if self.justBeginning and len(slist[1]) <= 4:
                       print (slist[1])

                    self.listOfWords[final_string] = present_str
                    self.hiPriIndex = self.hiPriIndex +1

    # mySort()
    # Custom sort function
    def mySort(self, e):
        if not self.toggleSort:
            retval = e
        else:
            sword = e.split(",",2)
            theword = sword[2]
            l = len(theword)
            if l > 9:
                l = 9
            pre = str(l)
            retval = pre + theword

        return retval

    # fillListboxes(self)
    # Uses hiList populate the listboxes
    def fillListboxes(self):
        self.hiList.sort(key=self.mySort, reverse=True)
        self.hiPriIndex = 0;

        for contentItem in self.hiList:
            self.hiPriList.insert(self.hiPriIndex, contentItem)
            self.hiPriIndex += 1

# MAIN FUNCTION
if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("700x800")
    mb = MindBoggle(root)
    root.mainloop()

