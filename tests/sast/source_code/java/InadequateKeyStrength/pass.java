class Connector {
    @javax.jws.WebMethod
    void connect(HttpServletRequest req){
        Keygen keygen = javax.crypto.KeyGenerator.getInstance("Blowfish");
        keygen.init(128);
    }
}
