package com.company.util;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Enumeration;
import java.util.List;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;

import org.jboss.seam.log.Logging;
import org.jboss.seam.log.Log;

public class HttpRequestDebugFilter implements Filter {
    Log log = Logging.getLog(HttpRequestDebugFilter.class);

    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws IOException,
            ServletException {

        if (request instanceof HttpServletRequest) {
            HttpServletRequest httpRequest = (HttpServletRequest)request;
            if (httpRequest.getRequestURI().endsWith(".seam")) {
                // ruleid: seam-log-injection
                log.info("request: method="+httpRequest.getMethod()+", URL="+httpRequest.getRequestURI());
            }
        }

        chain.doFilter(request, response);
    }

    public void logUser(User user) {
        // ruleid: seam-log-injection
        log.info("Current logged in user : " + user.getUsername());
    }

    public void logUser(User user) {
        // ok: seam-log-injection
        log.info("Current logged in user : #0", user.getUsername());
    }

}
