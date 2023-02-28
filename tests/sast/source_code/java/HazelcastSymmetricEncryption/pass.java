class Connector {
    @javax.jws.WebMethod
    void connect(HttpServletRequest req){
        SymmetricEncryptionConfig sec = new com.hazelcast.config.AsymmetricEncryptionConfig();
    }
}
