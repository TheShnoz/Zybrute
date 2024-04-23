from tkinter import *
import solver as zb
import json
root = Tk()
root.geometry("480x600")
root.title("ZYBRUTE")
#root.resizable(False, False)
root.columnconfigure((0,1,2,3,4), weight =1)
root.rowconfigure((0,1,2,3,4), weight =0, uniform='a')

sf = Frame(root)
sf.columnconfigure((0,1,2,3,4), weight=1)
sf.rowconfigure((0,1,2,3,4), weight=0, uniform='a')

header = Label(root, text="", font=("Sans Serif", 25), highlightbackground="black", highlightthickness=2)
header.grid(row=0, column=0, columnspan=5, sticky="new")

errorlabel = Label(sf, fg="red")
errorlabel.grid(row=4, column=0, columnspan=5, sticky="ew", padx=100)

usr = ""
pwd = ""
auth = ""
userid = ""
book = None
chapter = None
startindex = None
endindex = None

def SigninScreen():
    sf.grid(row=1, column=0, rowspan=5,columnspan=6, sticky="ew")
    header.config(text="Zybrute")
    
    global usr
    global pwd
    usernamelabel = Label(sf, text="Zybooks Email: ")
    global usernameentry
    usernameentry = Entry(sf, textvariable = usr)
   
    passwordlabel = Label(sf, text="Zybooks Password: ")
    global passwordentry
    passwordentry = Entry(sf, textvariable = pwd)

    sub_btn = Button(sf, text = 'Get assignments', command = testsignin)


    usernamelabel.grid(row=1, column=0, columnspan=1, sticky="ew")
    usernameentry.grid(row=1, column=1, columnspan=2, sticky="ew")

    passwordlabel.grid(row=2, column=0, columnspan=1, sticky='ew', pady=15)
    passwordentry.grid(row=2, column=1, columnspan=2, sticky='ew')

    sub_btn.grid(row=3, column=0, columnspan=5, sticky="ew", padx=100)

def testsignin():
    print("testing signin")
    global usr
    global pwd
    usr = usernameentry.get()
    pwd = passwordentry.get()
    if usr == "" or pwd == "":
            errorlabel.config(text="1 or more fields are empty")
            return False
    else:
        errorlabel.config(text="")
        try:
            response = zb.signin(usr, pwd)
            global auth
            global userid       
            global ref
            auth = response["session"]["auth_token"]
            print("auth token: " + auth)
            userid = response["session"]["user_id"]
            #zb.t_spfd = 0
        except:
            errorlabel.config(text="ERROR, check if your credentials are correct")
            return False
        errorlabel.config(text="")
        getbooks()
        print("success")
        return True


#MAIN CONFIG SCREEN
MainF = Frame(root)
MainF.columnconfigure((0,1,2,3,4), weight=1)
MainF.rowconfigure((0,1,2,3,4), weight= 0,uniform='a')

def getbooks():
    sf.grid_forget()
    MainF.grid(row=1, column=0, rowspan = 5, columnspan= 6, sticky="ew")
    root.tkraise(MainF)
    global auth
    global userid

    Label(MainF, text="Book Selection: ").grid(row=1, column=0, columnspan=1, sticky= "ew")

    bookdict = zb.getbooks(userid, auth)

    #terrible, awful way to do this, but whatever
    booknames = list(bookdict.keys())
    bookcodes = list(bookdict.values())
    selectedbook = StringVar(value = booknames[0])

    bookchoice = OptionMenu(MainF, selectedbook, *booknames, command= lambda selectedbook : getchapters(bookdict[selectedbook]))
    bookchoice.grid(row=1, column=1, columnspan= 2, sticky="ew")


def getchapters(bookcode):
    print(bookcode)
    global usr, pwd, auth
    response = zb.signin(usr, pwd)
    auth = response["session"]["auth_token"]
    global book
    book = bookcode
    Label(MainF, text="Chapter Selection: ").grid(row=2, column=0, columnspan=1, sticky= "ew")
    chaplist = zb.getchapters(auth, bookcode)
    chapdict = dict()
    chapnames = []
    chapnums = []
    for chapter in chaplist:
        chapnames.append(chapter["title"])
        chapnums.append(chapter["number"])
        chapdict[chapter['title']] = chapter['number']

    selectedchapter = IntVar()
    chapchoice = OptionMenu(MainF, 
                            selectedchapter,
                            *chapnums,
                            command = lambda selectedchapter: getsections(chaplist, selectedchapter))
    chapchoice.grid(row=2, column=1, columnspan=2, sticky="ew")


def getsections(chaplist, chapternumber):
    chapternumber = int(chapternumber)
    print("Success" + str(chapternumber))
    sectionlist = zb.getsections(chaplist, chapternumber)
    #print(sectionlist)
    global startindex, endindex, chapter
    startindex 
    endindex
    chapter = chaplist[chapternumber]
    Label(MainF, text="Do sections... ").grid(row=3, column=0, columnspan=1, sticky="ew")
    startindex = Spinbox(MainF, from_=1, to = len(sectionlist))
    startindex.grid(row=3, column=2, sticky='ew')
    endindex = Spinbox(MainF, from_=1, to = len(sectionlist))
    endindex.grid(row=3, column=3, sticky='ew')
    solvebutton = Button(MainF, text="DO MY HOMEWORK FOR ME", command = lambda: solveshit(sectionlist, int(startindex.get()), int(endindex.get())))
    solvebutton.grid(row=4, column=0, columnspan=4, sticky="ew")

def solveshit(sectionlist, startsection, endsection):
    global auth, chapter, book, usr, pwd
    zb.t_spfd = 0
    auth = zb.signin(usr, pwd)["session"]["auth_token"]
    #print(zb.getactivities(book, chapter['number'], sectionlist[0]['canonical_section_number'], auth))
    #print(book)
    print(chapter['title'])
    print(str(startsection) + " " + str(endsection))
    print("solving shit")
    for sec in range(startsection-1, endsection):
        zb.solveall(sectionlist[sec], book, chapter, auth)
    
#Load Screen
SigninScreen()
root.mainloop()
