#!/usr/bin/env python
# -*- coding: utf-8 -*-

header = """<!DOCTYPE html>
<html>
  <head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type">
    <title>%s</title>
    <script type="text/javascript">
    function showSpoiler(obj)
    {
    var inner = obj.parentNode.getElementsByTagName("div")[0];
    if (inner.style.display == "none")
        inner.style.display = "";
    else
        inner.style.display = "none";
    }
    </script>
  </head>
  <body>
"""

photoline = '''
    <a href="$title.jpg"

    target="_blank"><img alt="" width="800"src="$title.jpg"

      title="" border="0"></a><br>
    $text
    <br>
    <br>
'''

footer = """  </body>
</html>
"""

comments_begin = '''
    <div class="spoiler">
    <input type="button" onclick="showSpoiler(this);" value="Show/Hide $num comments" />
    <div class="inner" style="display:none;">
'''

comment_text = '''<br>
        <b>$author_name $author_family</b><br>
        &nbsp;&nbsp;&nbsp;&nbsp$text
        <br>
'''

comments_end = '''
    </div><br>
    <br>'''