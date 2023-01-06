REQUIREMENTS
requires the beautiful soup 4 module to be installed on the system - https://www.crummy.com/software/BeautifulSoup/bs4/doc/

HOW TO USE
1. Run crawler.py
2. Enter either an Amazon or eBay product URL
3. Click Start Crawl
4. You will know the crawl has finished once the button returns to saying Start Crawl
5. You can see the results (also displayed on screen) in output.CSV


EXAMPLE OF PRODUCT URLs KNOWN TO WORK
Amazon:https://www.amazon.co.uk/dp/B08NXKYLTP/ref=syn_sd_onsite_desktop_9?psc=1&pd_rd_w=AgCjn&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUFaV0lMMklLSlFFVTQmZW5jcnlwdGVkSWQ9QTAxMzIxNTEyUzRVMDJKSEtIUlA3JmVuY3J5cHRlZEFkSWQ9QTA0MzQ3NjUzM1pKMjlNWVlUUDNTJndpZGdldE5hbWU9c2Rfb25zaXRlX2Rlc2t0b3AmYWN0aW9uPWNsaWNrUmVkaXJlY3QmZG9Ob3RMb2dDbGljaz10cnVl
eBay: https://www.ebay.co.uk/itm/363566371744?_trkparms=pageci%3A4d9547fd-727d-11ec-bd25-0a5a42ad320c%7Cparentrq%3A46bd152117e0ad33d3b42cccffda3a78%7Ciid%3A1

OPTIONS
in crawler.py, calls to level limit and index limit can be altered to get more or less data
index limit is how many related items items it will traverse on the same page (breadth)
level limit is how many related items items will be traversed from the inital related items (depth)

in crawler.py, maxThreads can be changed to increase or decrease the number of threads (c-procs) that are used by the system