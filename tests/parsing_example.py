from dominic import DOM

lists_html = """<html>
  <head>
    <title>My Lists</title>
  </head>
  <body>
    <ul>
      <li id="nice-ball">kicks</li>
      <li id="nice-star">sparks</li>
      <li id="awful-ball">that does not kick</li>
      <li id="awful-star">that has no light</li>
      <li id="capitalized word">Word</li>
      <li id="lower word case">word</li>
      <li id="word upper cased">WORD</li>
    </ul>
  </body>
</html>"""

lists_dom = DOM(lists_html)

ball, star = lists_dom.find('ul > [id^="nice"]')

assert ball.text() == 'kicks'
assert star.text() == 'sparks'

words = lists_dom.find('ul > [id~="word"]')

assert len(words) is 3
assert words[0].text() == 'Word'
assert words[1].text() == 'word'
assert words[2].text() == 'WORD'

