#!/usr/bin/env python
# -*- coding: utf-8 -*-

from string import Template

header = Template("""<!DOCTYPE html>
<html>
  <head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type">
    <title>$title</title>
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
""")

photoline = Template('''
    <a href="$title.jpg"

    target="_blank"><img alt="" width="807"src="$title.jpg"

      title="" border="0"></a><br>
    $text
    <br>
    <br>
''')

footer = """  </body>
</html>
"""

comments_begin = Template('''
    <div class="spoiler">
    <input type="button" onclick="showSpoiler(this);" value="Show/Hide $num comments" />
    <div class="inner" style="display:none;padding-left:5%">
''')

author_line = Template('''<br>
        <b>$author_name $author_family</b> $date<br>
''')

comment_text = Template('''&nbsp;&nbsp;&nbsp;&nbsp$text
        <br>
''')

comments_end = '''
    </div>
    </div><br>
    <br>'''

wall_photo_begin = '''
    <div id="image-table" style="width:85%">
        <table>
            <tr>
'''

wall_photo_content = Template('''
            <td style="padding:4px">
                <img src="$title.jpg" width="100%">
              </td>
''')

wall_photo_newline = '''
            <tr>
            </tr>
'''

wall_photo_end = '''
            </tr>
        </table>
    </div>
'''

date_format_posts = '%Y-%m-%d  %H:%M'
