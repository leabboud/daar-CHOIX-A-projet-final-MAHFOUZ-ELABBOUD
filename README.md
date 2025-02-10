Afin de réduire la taille de l'archive finale, nous n'avons pas inclus les infos dérivés des pre-calculs ni les environnements virtuels.
Les dépendances pour imageService et bookService sont:
- Les bibliothèques Python non-installés par défaut: Flask, gutenberg
- Les bibliothèques Python: csv, requests, os, json, re, functools

# Pour le Back-end

## Pour book service

1. export GUTENBERG_MIRROR=http://www.mirrorservice.org/sites/ftp.ibiblio.org/pub/docs/books/gutenberg/
2. (Si les pre-calculs ne sont pas encore fait) cd bookService/bookInfo
2.1 python3 reduceLocalInfo.py (Afin de modifier le nombre de textes traités, changer le parametre de la fonction initialise())
3. python3 -m flask --app bookService run -p 5001

## Pour image service

1. cd backend/imageservice/src
2. python3 -m flask --app imageService run -p 5002

# Pour le Front-end

1. cd frontend/biblioshelf/src
2. npm run dev


# Présentation par vidéo pitch : 
Lien: https://youtu.be/mVeSIqKZoGE