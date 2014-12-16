Twisted SSE demo
================

A twisted web server that implements server sent events (SSE)

To run this demo:

    python sse_twisted_web.py
    
Open up http://localhost:12000 in your browser.

To publish events:

    curl -d 'data=Hello!' http://localhost:12000/publish
    
You should see the data you publish in your browser. That's it!
