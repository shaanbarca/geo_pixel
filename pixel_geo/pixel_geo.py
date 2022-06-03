
"""
Neccesary Libraries 
"""
from PIL import Image
import os, os.path
import torch
import pandas as pd
from google.colab import files
import shutil
import rasterio


def count_wpshp(image_path,model_path,threshold=0.3):
  """
  inputs = TIFF file with coordinates, threshold, modelpath
  outputs = CSV of lat long of object detected for GIS shp file

  """
  model = model_path
  model.conf = threshold
  imgs = [] # contains all images in dir
  geos = [] # contains tiff coords in dir
  path = image_path
  valid_images = [".jpg",".gif",".png",".tga",".tif",".tiff"]
  total = []
  for f in os.listdir(path):
      ext = os.path.splitext(f)[1]
      if ext.lower() not in valid_images:
          continue
      imgs.append(Image.open(os.path.join(path,f))) #opens images 
      geos.append(rasterio.open(os.path.join(path,f))) # gets coordinates of tiff

  for img,geo in zip(imgs,geos) : #iterate over two list/tuple 
    
    results = model(img) #inputs image to model
    
    boredpile_ds = results.pandas().xyxy[0] #outputs a pandas df with cols of coordinates, class of object and confidence score
   
    # Below we reapply the coordinates extracted from the tif files to our xmin,xmax,ymin,ymax to convert to latlong

    boredpile_ds["xmin"], boredpile_ds["ymin"] = geo.transform * (boredpile_ds.xmin,boredpile_ds.ymin) # transforms coordinates to geoloc
    boredpile_ds["xmax"], boredpile_ds["ymax"] = geo.transform * (boredpile_ds.xmax, boredpile_ds.ymax) # same as above
    boredpile_ds =boredpile_ds[['name','class','xmin', 'ymin', 'xmax','ymax','confidence']] # removes unneeded columns
    total.append(boredpile_ds) #we need to appends result of each object (here in pandas df) to a list so to get one giant df

  total = pd.concat(total,ignore_index=True) #concatanate to list of results df to one big dataframe
  total.to_csv("shp.csv") #download csv of our shp file location