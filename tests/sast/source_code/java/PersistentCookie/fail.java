import javax.servlet.http.Cookie;
class Connector {
    @javax.jws.WebMethod
    void connect(HttpServletRequest req){
        Cookie cook = new Cookie("cookie");
        cook.setMaxAge(31536000);
    }
}
