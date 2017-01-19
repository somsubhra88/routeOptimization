setwd("C:/Users/somsubhra.g/PycharmProjects/routeOptimization/comparison")
library('dplyr')
source('googleAPI.R')
latLngData = read.csv("Comparison Data_final.csv")

for(i in 1:NROW(latLngData))
{
  R = list(lat = latLngData$Device_Latitude[i], lng = latLngData$Device_Longitude[i])
    
  if(!is.na(latLngData$Device_Latitude[i]))
    {
      Time = round(time(point1 = list(lat = latLngData[i,"GoogleAPI_Latitude"], lng = latLngData[i,"GoogleAPI_Longitude"]),
                        point2 = R),2)
      Distance = round(distance(point1 = list(lat = latLngData[i,"GoogleAPI_Latitude"], lng = latLngData[i,"GoogleAPI_Longitude"]),
                                point2 = R),2)
      latLngData$timeDiff_3[i] = ifelse(length(Time) > 0, Time, NA)
      latLngData$distanceDiff_3[i] = ifelse(length(Distance) > 0, Distance, NA)
    }
    else
    {
      latLngData$timeDiff_3[i] = NA
      latLngData$distanceDiff_3[i] = NA
    }
    
}

write.csv(latLngData,"Comparison Data_final.csv", row.names = FALSE)
