Localization
============

Initialization
--------------
Create template file. Get messages from *.py file and place them to *.pot template
```
sh init.sh
```

Add language
------------
Create lang dir in ./translations if new locale required
```
sh addlang.sh en
```

Update translation files
------------------------
If template file *.pot not created - create it. Then generate translation files *.po  for all languages
```
sh update.sh
```

Compile translations
--------------------
Compile translations
```
sh compile.sh
```