class Connector {
    @javax.jws.WebMethod
    void connect(HttpServletRequest req){
        Cookie cook = new Cookie("cookie");
        req.setMethod(cook.getString(), cook.getVal());
    }
}
