library(optimx)
library(reshape)
library(reshape2)
library(dplyr)

# Casting dataset to be recommendation engine friendly
df1 = read.csv("Addendum.csv")
df2 = read.csv("Ratio_CSV.csv")
df = rbind(df1,df2)
df_cast = acast(df, user~game_name)
df_cast_dataframe = data.frame(df_cast)

# Pull only relevant games
columnmeans = colMeans(df_cast_dataframe)
filter_by_name = names(sort(columnmeans, decreasing = TRUE)[0:1000])
df_filtered = df_cast_dataframe[,c(filter_by_name)]
#names(df_cast_dataframe)

# Init
numfeatures = 100
numbercol = ncol(df_filtered)
numberrow = nrow(df_filtered)
X = matrix(.125,nrow=ncol(df_filtered),ncol=numfeatures)
Theta = matrix(.125,nrow=nrow(df_filtered),ncol=numfeatures)
Y = df_filtered
R = data.frame((Y!=0)*1)

# Grad function for both X and Theta (collaborative filtering)
TotalGrad = function(XTheta,Y,R,lambda,numbercol,numberrow){
  X = matrix(data = XTheta[0:numbercol*numfeatures],nrow = numbercol, ncol = numfeatures)
  Theta = matrix(data = XTheta[((numbercol*numfeatures)+1):length(XTheta)],nrow = numberrow, ncol = numfeatures)
  #Gradient for X
  XGradient = function(X,Theta,Y,R,lambda){
    XGrad = t(as.matrix(t(Theta))%*%as.matrix((R*(X%*%t(Theta)-Y)))) +
      lambda*X
    return(XGrad)
  }
  
  #Gradient for Theta
  ThetaGradient = function(X,Theta,Y,R,lambda){
    ThetaGrad = as.matrix(R*(X%*%t(Theta)-Y))%*%as.matrix(X) +
      lambda*Theta
    return(ThetaGrad)
  } 
  XGrad = XGradient(X,Theta,Y,R,lambda)
  ThetaGrad = ThetaGradient(X,Theta,Y,R,lambda)
  Grad = c(XGrad,ThetaGrad)
  return(Grad)
}
#Cost function and gradients
CostFunction = function(XTheta,Y,R,lambda,numbercol,numberrow){
  X = matrix(data = XTheta[0:numbercol*numfeatures],nrow = numbercol, ncol = numfeatures)
  Theta = matrix(data = XTheta[((numbercol*numfeatures)+1):length(XTheta)],nrow = numberrow, ncol = numfeatures)
  initCost = sum(R*(X%*%t(Theta)-Y))^2
  J = .5 *initCost+ 
    .5*lambda*(sum(Theta))^2+
    .5*lambda*(sum(X))^2
  return(J)
}

# Run the functions
Cost = CostFunction(c(X,Theta),Y,R,.05,numbercol,numberrow)
GradList = TotalGrad(c(X,Theta),Y,R,.05,numbercol,numberrow)

# Hacky stepwise gradient descent
XTheta = c(X,Theta)
count = 0
minCount = 0
minCost = 100000000
while(count != 100){
  Cost = CostFunction(XTheta,Y,R,.1,numbercol,numberrow)
  Grad = TotalGrad(XTheta,Y,R,.1,numbercol,numberrow)
  XTheta = XTheta - (.001*Grad)
  if(minCost > Cost){
    minCost = Cost
    minCount = count
    minGrad = Grad
  }
  count = count + 1
}

# Create YPred
XPred = matrix(data = minGrad[0:(numbercol*numfeatures)],nrow = numbercol, ncol = numfeatures)
ThetaPred = matrix(data = minGrad[((numbercol*numfeatures)+1):(numberrow*numfeatures+numbercol*numfeatures)],nrow = numberrow, ncol = numfeatures)

YMean = colMeans(Y)
Pred = (XPred%*%t(ThetaPred))[,1] + YMean

# Remove games already played
PlayedGames = data.frame(R[1,])
PlayedGames2 = PlayedGames[, (colSums(PlayedGames == 0) > 0)]
gamesNames = names(PlayedGames2)
Pred2 = Pred[gamesNames]

print(sort(Pred2,decreasing = TRUE)[0:20])
