# Projet D'Advanced Compilation
Killian Bertrand, Emilien Bois

Nous avons choisi pour ce projet de traiter les deux fonctionnalités suivantes :
- les fonctions
- les float.
Nous n'avons réussi aucun des deux.
Nous avons passé beaucoup de temps sur les fonctions et n'avons pas eu le temps de nous pencher sur l'implémentation de float.

Pour faire malgré tout tourner la compilation, faire les commandes suivantes :
- Création du .asm : python3 main.py hello.c helloTest.asm :
- Création et lancement du .o : nasm -f elf64 helloTest.asm && gcc -no-pie helloTest.o && ./a.out 1 5 

Ceci donne une segmentation fault, ce qui doit sûrement être dû à une mauvaise gestion de la pile.

Pour implémenter les fonctions, nous avons tout d'abord du comprendre les conventions sur la pile d'une fonction. A chaque appel de fonction est donc crée un "frame" pour celui-ci, possédant une partie pour les paramètres, pour la commande suivant l'appel, une adresse où est stocké l'adresse de la fonction qui lance l'appelle, le old rpb, et aussi une partie pour les variables locales.

Ainsi, nous avons premièrement réalisé deux fonctions permettant de trouver des dictionnaires associant une clé, étant le nom d'une fonction, à un dictionnaire qui associe à chaque nom de variable sa position associé (par rapport à rbp)

Nous avons modifié l'alphabet du langage pour ajouter la liste de fonctions, qui pourrait être vide ou être une fonction suivi d'une liste de fonction, à la manière des listes de variables. 

Nous avons aussi beaucoup modifié les fonctions python du fichier compile.py pour les adapter aux fonctions. Nous avons aussi ajouté une fonction compile_func qui s'adapte à une liste vide ou non vide, une fonction initVar, initMainVar. De même nous avons rajouté l'implémentation de la fonction start : qui initialise les variables de main et l'appelle. Nous pensons que l'erreur vient de l'initialisation de ces variables. 

Nous avons alors un problème de segmentation fault, nous n'avons aucune idée de la provenance de l'erreur.
