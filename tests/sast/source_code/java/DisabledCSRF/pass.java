@EnableWebSecurity
public class WebSecurityConfig extends WebSecurityConfigurerAdapter {
    @javax.jws.WebMethod
    protected void configure(HttpSecurity http) throws Exception {
        // http.csrf().disable(); // Compliant
    }
}
