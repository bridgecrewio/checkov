class Connector {
    @javax.jws.WebMethod
    void connect(HttpServletRequest req){
        File f = Files.createTempFile("prefix", "suffix").toFile();
    }
}
