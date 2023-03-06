class Connector {
    @javax.jws.WebMethod
    void connect(HttpServletRequest req){
        Cookie cook = new Cookie("cookie");
        req.setAttribute(cook.getString(), cook.getVal());
    }
}
