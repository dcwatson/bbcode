Built-In Tags
=============

Below are the tag formatters that are built into ``bbcode`` by default:

Tag    | Input                          | Output
-------|--------------------------------|----------------------------------------------
b      | [b]test[/b]                    | `<strong>test</strong>`
i      | [i]test[/i]                    | `<em>test</em>`
u      | [u]test[/u]                    | `<u>test</u>`
s      | [s]test[/s]                    | `<strike>test</strike>`
hr     | [hr]                           | `<hr />`
sub    | x[sub]3[/sub]                  | `x<sub>3</sub>`
sup    | x[sup]3[/sup]                  | `x<sup>3</sup>`
list/* | [list][*] item[/list]          | `<ul><li>item</li></ul>`
quote  | [quote]hello[/quote]           | `<blockquote>hello</blockquote>`
code   | [code]x = 3[/code]             | `<code>x = 3</code>`
center | [center]hello[/center]         | `<div style="text-align:center;">hello</div>`
color  | [color=red]red[/color]         | `<span style="color:red;">red</span>`
url    | [url=www.apple.com]Apple[/url] | `<a href="http://www.apple.com">Apple</a>`
