setwd("C:/Users/somsubhra.g/PycharmProjects/routeOptimization/comparison")
library('dplyr')
source('googleAPI.R')
latLngData = read.csv("Detail Path - Best Cost Output.csv")

names(latLngData) = gsub("\\.","_",names(latLngData))
latLngData =  latLngData %>%
              select(.,End_Node,End_Latitude,End_Longitude,Address_Line_1,Address_Line_2,City,State,Pincode) %>%
              dplyr::rename(Tracking_ID = End_Node,MMI_Latitude = End_Latitude, MMI_Longitude = End_Longitude) %>%
              filter(Tracking_ID != 'Sink')

for(i in 1:NROW(latLngData))
{
  R = googleMapsApi(latLngData[i,"Address_Line_1"],latLngData[i,"Address_Line_2"],latLngData[i,"Pincode"],
                    latLngData[i,"City"],latLngData[i,"State"])
  if(!is.na(R$lat))
    if(R$lat < 0 | R$lng < 0 )
      R$lat = R$lng = NA
  latLngData$GoogleAPI_Latitude[i] = R$lat
  latLngData$GoogleAPI_Longitude[i] = R$lng
  
  if(!is.na(R$lat))
  {
    Time = round(time(point1 = list(lat = latLngData[i,"MMI_Latitude"], lng = latLngData[i,"MMI_Longitude"]),
                   point2 = R),2)
    Distance = round(distance(point1 = list(lat = latLngData[i,"MMI_Latitude"], lng = latLngData[i,"MMI_Longitude"]),
                              point2 = R),2)
    latLngData$timeDiff[i] = ifelse(length(Time) > 0, Time, NA)
    latLngData$distanceDiff[i] = ifelse(length(Distance) > 0, Distance, NA)
  }
  else
  {
    latLngData$timeDiff[i] = NA
    latLngData$distanceDiff[i] = NA
  }
  
}

write.csv(latLngData,"Comparison Data.csv", row.names = FALSE)
