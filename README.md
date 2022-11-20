# Retrying wrapper around signtool

Call resigntool with the same arguments as signtool.
Example:
```
resigntool sign /s MY /n "Garrick Meeker" /fd sha256 /tr "http://timestamp.digicert.com" /td sha256 myprog.exe
```
