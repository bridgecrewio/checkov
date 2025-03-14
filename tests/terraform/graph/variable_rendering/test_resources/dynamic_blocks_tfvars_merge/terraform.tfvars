
key_name                = "test1"
vmhosts = [
    {
        name            = "vm1"
        monitoring      = false
        tags            = { Environment = "prod", Department = "Testing" }
        private_ip      = "11.101.33.254"
        ports           = [ 22 ]
    },    
    {
        name            = "vm2"
        monitoring      = false
        tags            = { Environment = "Test" }
        private_ip      = "22.212.0.200"
        ports           = [ 80 ]
    }      
]
