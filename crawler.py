#Test Amazon URL: https://www.amazon.co.uk/dp/B08NXKYLTP/ref=syn_sd_onsite_desktop_9?psc=1&pd_rd_w=AgCjn&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUFaV0lMMklLSlFFVTQmZW5jcnlwdGVkSWQ9QTAxMzIxNTEyUzRVMDJKSEtIUlA3JmVuY3J5cHRlZEFkSWQ9QTA0MzQ3NjUzM1pKMjlNWVlUUDNTJndpZGdldE5hbWU9c2Rfb25zaXRlX2Rlc2t0b3AmYWN0aW9uPWNsaWNrUmVkaXJlY3QmZG9Ob3RMb2dDbGljaz10cnVl
#Test eBay URL: https://www.ebay.co.uk/itm/363566371744?_trkparms=pageci%3A4d9547fd-727d-11ec-bd25-0a5a42ad320c%7Cparentrq%3A46bd152117e0ad33d3b42cccffda3a78%7Ciid%3A1
from tkinter.ttk import Treeview
import urllib.request
from datetime import datetime
from bs4 import BeautifulSoup
import csv
from tkinter import *
import threading
import gc
#from memory_profiler import profile
from crawlerFunctions import href2ProductURL as href2ProductURL

stopBtn = True
crawlStopping = False
root = Tk()
crawlSearch = Entry(root, width=50)
crawlSearch.grid(row=0,column=5)

radioChoice = IntVar()
ebayBtn = Radiobutton(root, text= "eBay", variable=radioChoice, value=1)
amazonBtn = Radiobutton(root, text= "Amazon", variable=radioChoice, value=2)
radioChoice.set(1)

#ebayBtn.grid(row=1, column= 1,sticky="W")
#amazonBtn.grid(row=2, column= 1,sticky="W")

urlLock = threading.Lock()
threadLock = threading.Lock() #Prevent other threads from making a thread at the same time, going over the max thread limit
pendingLock = threading.Lock()
csvLock = threading.Lock() # Used to stop other threads from writing to the .CSV file at the same time

header = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"} #To make the crawler appear more human
seenURL = [] #To prevent the crawler from opening the same page
pendingURL = [] #URLs appear here before being moved to seenURL to avoid race conditions
maxThreads = 5
threads = []

#Product to find prices for
searchLabel = Label(root, text="Amazon or eBay URL").grid(row=0,column=4)

def crawl(URL,level,levelLimit,indexLimit):
 if stopBtn == True:
  print("Stop button pressed!")
  return

 while True:
  try:
   print("Current level: " + str(level))
   req = urllib.request.Request(URL,headers=header)
   resp = urllib.request.urlopen(req)

   
   #Get the data and HTML structure of the opened page
   data = resp.read()
   html = data.decode("UTF-8")
   resp.close()

   soup = BeautifulSoup(html, 'html.parser')

   #Get price of current product
   if URL.startswith("https://www.ebay.co.uk"):
    res = soup.find("span", {"class": "notranslate"}) # place in html where the price is stored
    price = res.get_text() #price extracted from HTML structure
    csvLock.acquire()
    csvFile = open('crawlOutput.csv', 'a', newline='')
    print("Writing to CSV File price!")
    print("URL" + URL)
    print("PRICE" + str(price))
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow([href2ProductURL(URL),str(price)])
    output.insertItem(href2ProductURL(URL),price)
    csvFile.close()  
    csvLock.release()
   
   elif URL.startswith("https://www.amazon.co.uk"):
    if soup.find_all("span", {"class": "priceBlockBuyingPriceString"}):
       res = soup.find("span", {"class": "priceBlockBuyingPriceString"})

    if soup.find_all("span", {"class": "a-offscreen"}):
     res = soup.find("span", {"class": "a-offscreen"})
     price = res.get_text()
     print("getting CSV Lock")
     csvLock.acquire()
     print("Opening CSV File")
     csvFile = open('crawlOutput.csv', 'a', newline='')
     print("Writing to CSV File price!")
     print("URL" + URL)
     print("PRICE" + str(price))
     csvWriter = csv.writer(csvFile)
     csvWriter.writerow([href2ProductURL(URL),str(price)])
     output.insertItem(href2ProductURL(URL),price)
     csvFile.close()  
     print("releasing CSV Lock")
     csvLock.release()

   else:
     print("UNSUPPORTED WEBSITE")
     return
   

   
   pendingLock.acquire()
   if href2ProductURL(URL) in pendingURL:
    pendingURL.remove(href2ProductURL(URL))
   pendingLock.release()
   urlLock.acquire()
   seenURL.append(href2ProductURL(URL))
   urlLock.release()
   
   f = open("download.html", "w",encoding="utf-8")
   f.write(html)
   f.close()

   #Open links from related/similar items
   if URL.startswith("https://www.ebay.co.uk"):
    itemsList = soup.find_all("ul", {"class": "carousel__list"})[1]# find the list of items
    itemNames = itemsList.find_all("a",{"class": "item-tile"},href=True) #Items within the list

    for i in range(len(itemNames)):
      itemNames[i] = href2ProductURL(itemNames[i]['href']) #convert found links to just the product details

   else:
    itemsList = soup.find_all("ol", {"class": "a-carousel"})[1]
    
    itemNames = itemsList.find_all("div",{"class" : "a-section", 'data-asin':True})
    for i in range(len(itemNames)):
      itemNames[i] = "https://www.amazon.co.uk/dp/" + itemNames[i]['data-asin']

   break
  except Exception as e:
   print("Error Logged!")

   log = open("log.txt","a")# To log errors
   log.write("["+ str(datetime.now()) + "]"+str(e)+" \n")
   log.close()
   return
 
 #Free unused memory
 del URL
 del data
 del resp
 del html
 del req
 del res
 gc.collect()

 #Determine if at the furtherest layer the crawler is allowed to go down the tree of proucts
 if level != levelLimit:

  for index, found in enumerate(itemNames):
    print("Current index: " + str(index))
    urlLock.acquire()
    pendingLock.acquire()
    #Check to see if product is unique before crawling
    if href2ProductURL(found) not in seenURL and href2ProductURL(found) not in pendingURL:
     pendingURL.append(href2ProductURL(found))
     pendingLock.release()
     urlLock.release()
     threadLock.acquire()
     #Use more additonal thread if below the set limit
     if len(threads) < maxThreads:
       print("starting new thread")
       cProc = threading.Thread(target=crawl,args=(href2ProductURL(found),level + 1,0,0))
       threads.append(cProc)
       cProc.start()
       threadLock.release()
     
     else:
       print("continuing from existing thread")
       threadLock.release()
       crawl(href2ProductURL(found),level + 1,0,0)


    else:
      urlLock.release()
      pendingLock.release()
      print("already seen this product - " + href2ProductURL(found))
    if index == indexLimit:
        break
 


class table():
 def __init__(self):
   self.itemList = Treeview(root)
   #Columns
   self.itemList['columns']=('Link', 'Price')
   self.itemList.column('#0', width=0, stretch=NO)
   self.itemList.column('Link', anchor=CENTER, width=250)
   self.itemList.column('Price', anchor=CENTER, width=200)
   #Headings
   self.itemList.heading('#0', text='', anchor=CENTER)
   self.itemList.heading('Link', text="Link", anchor=CENTER)
   self.itemList.heading('Price', text='Price', anchor=CENTER)
   
   self.itemList.grid(row=3,column=5)
   self.count = 0

 def insertItem(self,link,price):
   self.itemList.insert(parent='',index=self.getCount(),values=(link,price))

 def getCount(self):
   previous = self.count
   self.count = self.count + 1
   return previous

 def resetList(self):
   for i in self.itemList.get_children():
       self.itemList.delete(i)
   self.count = 0
output = table()



def crawlThread():
   csvFile = open('crawlOutput.csv', 'w', newline="")
   csvWriter = csv.writer(csvFile)
   csvWriter.writerow(["URL","PRICE"])
   csvFile.close()
   baseURL = crawlSearch.get()
   crawl(baseURL,0,50,50)

   #Free threads so that the crawler can fire up more if needed
   while len(threads) != 0 :
     threadLock.acquire()
     threadLock.release()
     for t in threads:
      t.join(timeout = 2)
      if t.is_alive() == False:
       threads.remove(t)
       print("thread removed")
   
   print("Crawl complete")
   global seenURL
   seenURL = []
   global crawlStopping
   crawlStopping = False
   global stopBtn
   stopBtn = True
   btnText.set("Start Crawl")

btnText = StringVar()
btnText.set("Start Crawl")

def buttonClick():
  global stopBtn
  global crawlStopping
  print(crawlStopping)
  if crawlStopping == False:
   if stopBtn == True:
    print("starting crawl")
    output.resetList()
    stopBtn = False
    beginCrawl = threading.Thread(target=crawlThread)
    beginCrawl.start()
    btnText.set("End Crawl")

   else:
     print("waiting for crawl to stop")
     crawlStopping = True
     stopBtn = True
     btnText.set("Waiting to stop.....")
  else:
    print("crawl stopping, cannot start until stopped")
    
crawlButton = Button(root, textvariable=btnText, padx=60, bg="cyan", command=buttonClick).grid(row=1,column=5)
root.mainloop()






