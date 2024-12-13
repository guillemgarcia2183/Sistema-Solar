# Call the libraries
library(tidyverse)
library(dplyr)
library(readr)

# Set working directory
#path <- "C:/Users/garci/Desktop/UNIVERSITAT/QUART DE CARRERA/REALITAT AUGMENTADA/ABP/Sistema-Solar/codi/data"
path <- "C:/Users/garci/Desktop/QUART DE CARRERA/REALITAT AUGMENTADA/ABP/Sistema-Solar/codi/data"
setwd(path)

stars <- read.csv("stars.csv")

stars$x <- stars$x * 2
stars$y <- stars$y * 2
stars$z <- stars$z * 2
view(stars)

write.csv(stars, "stars.csv")



