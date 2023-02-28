class Connector {
    @javax.jws.WebMethod
    void connect(HttpServletRequest req){
        HttpServletResponse res = new HttpServletResponse();
        res.setHeader("Access-Control-Allow-Origin", "*");
    }
}
