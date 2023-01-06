
def href2ProductURL(href):
  if str(href).startswith("https://www.ebay.co.uk"):
   productURL = str(href).split('?')[0]
   return productURL
  if str(href).startswith("https://www.amazon.co.uk"):
   if str(href).startswith("https://www.amazon.co.uk/gp/"):
     productURL = "https://www.amazon.co.uk/gp/" + str(href).split('gp')[1].split("/")[1]
     return productURL
   productURL = "https://www.amazon.co.uk/dp/" + str(href).split('dp')[1].split("/")[1]
   return productURL

