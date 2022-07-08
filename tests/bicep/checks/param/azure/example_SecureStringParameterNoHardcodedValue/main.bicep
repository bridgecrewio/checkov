// pass

@description('password')
@secure()
param password string

// fail

@description('default password')
@secure()
param defaultPassword string = 'secret'

// unknown

@description('username')
param username string
