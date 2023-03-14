class Connector {
    @javax.jws.WebMethod
    void connect(HttpServletRequest req){
        File.createTempFile("prefix", "suffix", new File("/mySecureDirectory"));
    }
}
