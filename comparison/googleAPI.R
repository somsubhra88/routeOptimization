googleMapsApi = function(addr1,addr2,pincode,city,state)
{
  library('httr')
  library('curl')
  library('dplyr')
  # Universal Variable
  key = "AIzaSyAzjrVs89CXIfG3smf5Z-HIxqw6wJ9N3Hk"
  
  # Converting Everything into String
  addr1 = as.character(addr1)
  pincode = as.character(pincode)
  city = as.character(city)
  state = as.character(state)
  
  if(!addr2 %in% "" & !is.na(addr2))
  {
    addr2 = as.character(addr2)
    URL = paste("https://maps.googleapis.com/maps/api/geocode/json?address=", 
                URLencode(addr1),URLencode(addr2),",",city,
                ",",state,",",pincode,"&key=",key,sep="")
    URL = gsub("\\#","",URL)
  }
  else
  {
    URL = paste("https://maps.googleapis.com/maps/api/geocode/json?address=", 
                URLencode(addr1),",",city,",",state,
                ",",pincode,"&key=",key,sep="")
    URL = gsub("\\#","",URL)
  }
  
  if(length(content(GET(URL), "parsed", encoding = "UTF-8")$results) != 0)
    return(content(GET(URL), "parsed", encoding = "UTF-8")$results[[1]]$geometry$location)
  else
    return(list(lat = NA, lng = NA))
}

time = function(point1,point2)
{
	key <<- "0e41de65-d2c5-4ebd-9cfb-a552dae27f3e"
	referer <<- "http://large-analytics.flipkart.com/"
	URL = paste("https://maps.flipkart.com/api/v1/directions?point=",point1$lat,",",point1$lng,
			'&point=',point2$lat,",",point2$lng,"&key=",key,sep="")
	output = NULL
	counter = 0
	while(is.null(output))
	{
		counter = counter + 1
		R = URL %>%
			httr::GET(.,add_headers(referer = referer)) %>%
			content(., "parsed", encoding = "UTF-8")
		output = R$paths[[1]]$time
		if(!is.null(output) | counter > 20)
			break
	}
	return( R$paths[[1]]$time/60000)
}

distance = function(point1,point2)
{
  key <<- "0e41de65-d2c5-4ebd-9cfb-a552dae27f3e"
  referer <<- "http://large-analytics.flipkart.com/"
  URL = paste("https://maps.flipkart.com/api/v1/directions?point=",point1$lat,",",point1$lng,
      '&point=',point2$lat,",",point2$lng,"&key=",key,sep="")
  output = NULL
  counter = 0
  while(is.null(output))
  {
    counter = counter + 1
    R = URL %>%
      httr::GET(.,add_headers(referer = referer)) %>%
      content(., "parsed", encoding = "UTF-8")
    output = R$paths[[1]]$time
    if(!is.null(output) | counter > 20)
      break
  }
  return( R$paths[[1]]$distance/1000)
}