# DrawesomeNinja

L'objectif du site est de proposer une implémentation de Pictionary™ simple à utiliser, sans se prendre la tête, possible sans inscription, et avec des parties que l'on peut rejoindre simplement en allant à une URL et en donnant éventuellement un pseudo (retenu pour les fois suivantes).

Le site est en temps réel, utilisant des websockets. Il est basé sur Django et Django-Channels.

## Composants publics

#### Jeu de dessin

Le composant principal du site est le jeu de Pictionary. La page d'accueil offre directement, au premier regard, un bouton “Créer une partie”. À terme, une notion de partie publique listée sur la page d'accueil pourrait être une bonne idée.

Une partie se créée en donnant un nom (facultatif) et une liste de mots parmis une sélection. Des listes peuvent être créées à la convenance des joueurs — plus sur cela plus tard.

À la création, une URL est générée — par exemple, https://drawesome.ninja/gTUffuFD — et est directement proposée en premier plan (par exemple dans une modale) au créateur du salon de jeu. Toute personne ouvrant l'adresse rejoint la partie, même si cette dernière est en cours ; dans un tel cas il est ajouté à la liste des gens présents, en dernier, et peut commencer tout de suite à jouer sur le dessin en cours.

La personne créant le salon est d'office nommée _Maître du jeu_. Elle peut donner le rôle à quelqu'un d'autre, si elle le souhaite.

Le salon de jeu commence sans partie active. Une fois que les gens ont rejoint la partie, le maître du jeu peut lancer la partie, cliquant sur un bouton bien visible pour ce faire. (iSketch lançait la partie immédiatement, avant même que d'autres joueurs soient connectés, mais je ne pense pas que ce soit une bonne idée.) Il serait envisageable de lancer la partie automatiquement dés que deux joueurs sont en ligne, ou trois, ou de proposer l'option à la création du salon de jeu — à discuter.

##### Déroulement d'une partie

- Une **partie** est un ensemble de tours de jeu, avec à la fin un vainqueur.
- Pendant un **tour**, chaque joueur dessine et fait deviner une fois aux autres un mot.
- Un **dessin** est, pendant un tour, le moment pour un joueur où il dessine et tente de faire deviner son mot.

Dans une partie, on dessine chacun son tour, dans un ordre aléatoire pour les gens qui sont connectés avant le début, ou d'arrivée pour les gens qui arrivent après.

Le joueur qui dessine se voit montré le mot, pioché au hasard dans la liste, en gros plan au milieu de la zone de dessin pendant cinq secondes, avec éventuellement un compteur (5… 4…) avant le début du chrono. Ensuite, il a 4 minutes — configurable par le créateur de la partie — pour dessiner et faire deviner le mot.

Le chronomètre pourrait être réduit (à 30 secondes, par exemple) lorsque le mot a été deviné par au moins une personne. À discuter.

Il a pour cela des outils simple de dessin : 

- pinceaux de différentes tailles ;
- spays (éventuellement dans un second temps) de différentes tailles ;
- plusieurs couleurs de peinture ;
- possibilité de changer la couleur de fond (sans effacer le dessin) ;
- possibilité de tout effacer.

Il est interdit d'écrire des lettres ou des chiffres. _À terme, un système d'avertissement par les joueurs pourrait être ajouté, avec passage du tour du joueur si plus de deux, ou trois, avertissements. À voir, ce n'est pas prioritaire._

À côté de cela, il y a une zone de chat. Tous les joueurs peuvent écrire dedans. Ils peuvent discuter normalement ou proposer le mot qu'ils pensent être le bon.

- Si le dessinateur entre une phrase contenant le mot ou une version proche, le message est censuré.
- Si un autre joueur entre une phrase contenant une version proche du mot, le message n'est pas transmis.
  - Dans le cas _d'un mot proche seul_, s'il n'a pas déjà gagné, il est prévenu qu'il est proche de la solution. Les autres joueurs sont prévenus (ou pas ? à discuter) que ce joueur est près de trouver.
  - Dans le cas _d'une phrase contenant un mot proche_, il est prévenu que son message n'a pas été envoyé car il contient un mot proche de la solution.
- Si un autre joueur entre une phrase contenant le mot exact, le message n'est pas transmis.
  - Dans le cas _du mot exact seul_, il est prévenu qu'il a trouvé. Les autres joueurs le sont également, et il se voit attribuer les points qu'il mérite. (Plus sur le sujet des scores dans la section suivante.)
  - Dans le cas _d'une phrase contenant le mot exact_, il est prévenu que son message n'a pas été envoyé car il contient la solution. Il est invité à envoyer un message contenant la solution _seule_ pour la valider, ceci pour éviter les gens qui envoient tout le dictionnaire dans le chat pour gagner facilement.
- Dans tous les autres cas (mot proposé faux ou message de discussion), le mot est transmis aux autres tel un message de _chat_ classique.

La validation des mots est faite côté serveur, comme tout ce qui est validation, afin qu'il ne soit pas possible de tricher.

Si personne n'a déjà deviné, le dessinateur peut choisir de passer son tour. Il ne gagne aucun point s'il le fait. S'il semble AFK (i.e., n'a rien dessiné 30 secondes après le début de son tour), il passe automatiquement.

Un point à discuter est celui du nombre de chats : vaut-il mieux un seul chat qui sert à discuter et à proposer une solution, ou un chat pour discuter et une zone de texte pour proposer un mot ?
L'avantage du chat unique est que les joueurs n'ont pas à changer de champ pour discuter et proposer. C'est plus efficace, surtout dans le cadre d'un jeu basé sur la vitesse. Par contre, il faut bien le faire comprendre.

À terme, il pourrait être envisageable de proposer aux dessins d'être enregistrés pour une partie.

##### Système de scores

Lorsqu'un mot est deviné, le joueur ayant deviné et le dessinateur gagnent des points.

- Le dessinateur gagne trois points par joueur devinant le mot.
  _Idée : donner un bonus de quelques points si tout le monde sans exception devine le mot ?_
- Pour ce qui est des joueurs, ils gagnent des points en fonction de leur classement : 
  - le premier à deviner gagne dix points ;
  - le second, huit points ;
  - le troisième, six points ; 
  - le quatrième, quatre points ;
  - les autres, deux points.

Ce système est je pense améliorable. À discuter.

##### Cycle de vie des parties ; victoires

Un salon est créée par un joueur quelconque. Il n'est jamais supprimé.

Une partie débute dés que lancée par le maître de jeu. On peut imaginer plusieurs types de parties :

- fin lorsque un joueur atteint un certain nombre de points ;
- fin lorsque tous les joueurs ont joué un certain nombre de tours ;
- fin après un certain temps (en laissant tout de même le tour courant se finir).

On peut également envisager une partie sans fin (close lorsque les joueurs se déconnectent tous et ne reviennent pas dans le salon avant une demi-heure), à terme.

Si quelqu'un rejoint un salon alors qu'une partie est en cours, il rejoint automatiquement la partie et est ajouté au tour courant, à la fin. Par contre, il n'a pas d'avantage de points lié au fait d'être arrivé plus tard.

##### Configuration des parties

Une partie est configurable suivant plusieurs options.

- La liste des mots.
  _À terme, il serait envisageable de permettre de choisir plusieurs listes à utiliser en même temps._
- Le type de partie (chrono, nombre de tours, nombre de points ?).
- Le temps par tour, par défaut quatre (?) minutes.
- Autre chose ? Un mot de passe de salon de jeu, peut-être ?
- Et dans un second temps : 
  - pourquoi pas rendre système de scores personnalisable ;
  - le fait que la partie est publique (listée sur la page d'accueil) ou non.

Il est important de réfléchir à l'interface de création de parties : elle doit être _simple_, et surtout ne pas être un gros formulaire plein de boutons et de champs, quitte à par exemple masquer certaines paramètres moins utilisés.

Il est possible de reconfigurer les parties d'un salon ; cela dit, seuls les parties suivantes seront affectées.

Le maître du jeu peut choisir d'annuler la partie ; elle sera alors marquée comme _nulle_ et il n'y aura pas de vainqueur.

Lorsqu'une partie se termine, le salon passe en pause, avec pour le maître du jeu un gros bouton « Nouvelle partie ». Le chat reste actif en permanence.

#### Listes de mots

Un joueur ayant un compte (voir plus loin) peut créer des listes de mots.

Il a pour ça, s'il est connecté, accès à une page lui permettant de créer une liste, ayant un nom et… des mots (ouais). Un grand champ de texte lui permet d'entrer un mot par ligne.

Une liste peut être configurée comme étant _publique_, dans ce cas elle sera proposée sur l'accueil à toute personne voulant créer une partie. Seuls les administrateurs du site (ayant accès à l'admin Django) peuvent rendre une liste publique.

Une idée serait de permettre également de rendre les listes privées (des joueurs isolés) partageables, par exemple sous la forme d'une référence `pseudo@nom-de-la-liste` qu'il serait possible d'entrer sur l'écran de création d'une partie. Si ceci est implémenté, il serait judicieux de permettre aux joueurs de cloner la liste d'un autre joueur pour y apporter des modifications personnelles. Inutile, cela dit, d'aller plus loin à mon sens — listes collaboratives, ou système de propositions de modifications, sont hors de propos ici, sauf si le site grossis à terme et que la fonctionnalité est demandée.

#### Compte utilisateur

Les joueurs peuvent (mais c'est facultatif) créer un compte utilisateur. Dans ce cas, leurs statistiques seront enregistrées, à savoir : 

- nombre & liste des parties ;
- nombre total de points gagnés ;
- nombre total de mots dessinés devinés par au moins une personne ;
- nombre total de mots dessinés devinés par _tout le monde_ ;
- nombre de devinages corrects ;
- nombre d'incorrects ;
- nombre de parties gagnées.

Ouvrir un compte offre également l'accès à l'éditeur de listes mentionné plus haut, permet de simplifier un peu l'usage du site (plus de pseudo demandé lorsqu'un salon est rejoint), et offre la possibilité d'avoir un avatar (?).

À terme, des tableaux de scores pourraient être publiés, pour les gens ayant un compte (sur le mois précédent et tout le temps).



## Notes d'implémentation technique

#### Ordre d'implémentation

1. Interfaces d'inscription et de connexion (fournies par Django).
2. Interfaces de gestion des listes de mots, afin d'avoir un moyen simple de créer les listes publiques (conversion de l'entrée brute des mots en les modèles de la base de données avec une table des mots et une des listes des mots, plus une relation `ManyToMany`).
3. Bases du jeu : 
   - création de salon ;
   - connexion aux salons, rang des joueurs (maître de jeu ou joueur) ;
   - chat de salon ;
   - lancement d'une partie ;
   - passage des tours ;
   - gestion des mots, des gens qui devinent bien ou mal, de la proximité (distance de Levenshtein) ;
   - gestion de la victoire et du redémarrage d'une partie.
4. Systèmes plus avancés : 
   - passage du rôle de Maître du Jeu à quelqu'un d'autre ;
   - pages de statistiques des joueurs connectés ;
   - sauvegarde des images ;
   - partage & clônage des listes ;
   - …

#### Idées d'implémentation du dessin en temps réel

Le dessin se fait sur un _canvas_, avec des événements au clic & au maintient en fonction de l'outil actuellement choisi.

Pour le joueur, le temps entre deux vérifications de brossage est court, au maximum un dixième de secondes, pour que le dessin soit confortable et non saccadé.

Pour la transmission, lorsque le joueur dessine, une zone (initialement carrée, mais à terme, la forme pourrait être optimisée) contenant les pixels modifiés est en permanence mise à jour chez le client ; toutes les demi-secondes, la position et le contenu de cette zone sont copiés et envoyés par websocket au serveur, qui se charge de :

- recombiner l'image avec l'image qu'il stocke localement en mémoire, en permanence ;
- transférer le bout d'image et sa position aux autres clients, pour qu'ils recombinent le bout d'image avec ce qu'ils ont et mettent ainsi l'affichage à jour chez les autres joueurs.

Contrairement aux autres Pictonary en ligne, l'idée est d'éviter de transférer le dessin au _relâchement de la souris_ uniquement et _en entier à chaque fois_ afin :

- de proposer un vrai dessin en temps réel aux autres joueurs ;
- d'optimiser la consommation réseau de l'application.

#### Puissance nécessaire par salon

Pour chaque salon l'image entière courante est stockée en mémoire, afin de pouvoir l'envoyer à tout nouveau client. Ceci plus les données du salon chargées en mémoire et le traitement des messages, on peut estimer que chaque salon nécessite quelques Mio de mémoire vive et un peu de puissance de calcul pour recombiner les pixels de l'image toutes les demi-secondes lorsque quelque chose est dessiné.

Cette valeur peut être revue à la baisse vu que si rien ne change dans le dessin au bout d'une demi-seconde, rien n'est envoyé (logique).

#### Définition d'un protocole WebSockets

Il faudra définir proprement un protocole interne pour la communication via WebSockets, par exemple basé sur une charge utile en JSON structurée et contenant un type de paquet, du genre :

```json
{
  "packet": "drawing.update_draw",
  "payload": {
    "draw_extract_location": [18, 34],
    "draw_extract_size": [22, 15],
    "draw_extract_data": "data:image/png;base64,iVBORw..."
  }
}
```

où le `payload` est dépendant du type de paquet. Derrière, il suffirait de router les “paquets” vers la bonne fonction pour les gérer.

Voir aussi si Django-Channels ne propose pas quelque chose de natif pour gérer ça, mais il me semble que non.