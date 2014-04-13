#!/bin/sh

# move strings to pot template
/bin/sh ./scan.sh

# move strings from pot template to po files
pybabel update -i messages.pot -d ../../translations
