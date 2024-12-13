# Call the libraries
library(tidyverse)
library(dplyr)
library(readr)

# Set working directory
path <- "C:/Users/garci/Desktop/UNIVERSITAT/QUART DE CARRERA/REALITAT AUGMENTADA/ABP/Sistema-Solar/codi/data"
setwd(path)

stars <- read.csv("stars.csv")
view(stars)

