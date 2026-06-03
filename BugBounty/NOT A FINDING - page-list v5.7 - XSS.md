https://wordpress.org/plugins/page-list/
https://github.com/webvitalii/page-list
---
![[Pasted image 20250903204828.png]]


![[Pasted image 20250903204839.png]]
What is unfiltered_html?
unfiltered_html is a capability in WordPress that is granted to site administrators and editors that allows them to add unfiltered HTML, like scripts, in various places like posts and pages. Users without this capability will have their HTML run through wp_kses() which will strip all “evil” tags and attributes. This capability is a common reason why researchers think they’ve found an XSS vulnerability exploitable by admins and editors, when in fact it is the result of the capability in WordPress