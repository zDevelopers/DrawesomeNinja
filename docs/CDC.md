# DrawesomeNinja

L'objectif du site est de proposer une implémentation de Pictionary™ simple à utiliser, sans se prendre la tête, possible sans inscription, et avec des parties que l'on peut rejoindre simplement en allant à une URL et en donnant éventuellement un pseudo (retenu pour être proposé, sans être imposé, les fois suivantes).

Le site est en temps réel, utilisant des websockets. Il est basé sur Django et Django-Channels.

## Composants publics

### Jeu de dessin

Le composant principal du site est le jeu de Pictionary. La page d'accueil offre directement, au premier regard, un bouton “Créer une partie”. À terme, une notion de partie publique listée sur la page d'accueil pourrait être une bonne idée afin de pouvoir venir jouer seul avec les autres personnes connectées.

Une partie se créée en donnant un nom (facultatif) et une liste de mots parmis une sélection. Une liste contient au moins un mot, mais les listes proposées à tous seront plus complètes que cela, avec au minimum plusieurs centaines de mots.
Des listes peuvent être créées à la convenance des joueurs — plus sur cela plus tard.

À la création, une URL est générée — par exemple, https://drawesome.ninja/YHn8IWFy — et est directement proposée en premier plan (par exemple dans une modale) au créateur du salon de jeu. Un bouton est présent pour copier et partager sur divers réseaux sociaux l'adresse.
Toute personne ouvrant l'adresse rejoint la partie, même si cette dernière est en cours ; dans un tel cas il est ajouté à la liste des gens présents, en dernier, et peut commencer tout de suite à jouer sur le dessin en cours.

La personne créant le salon est d'office nommée _Maître du jeu_, ou _Maître Ninja_ — soyons fous. Elle peut donner le rôle à quelqu'un d'autre, si elle le souhaite. Si elle se déconnecte, le rôle est donné aléatoirement à un autre joueur n'étant pas détecté comme AFK.

Le salon de jeu commence sans partie active. Une fois que les gens ont rejoint la partie, le maître du jeu peut lancer la partie, cliquant sur un bouton bien visible pour ce faire. (iSketch lançait la partie immédiatement, avant même que d'autres joueurs soient connectés, mais je ne pense pas que ce soit une bonne idée.)

**Évolution** : si le Maître du Jeu est AFK avant le début de la partie pendant plusieurs minutes alors que personne ne se connecte, il serait envisageable d'automatiquement passer le rôle à une personne aléatoire n'étant pas AFK, ou de proposer un lien vers une nouvelle partie avec les mêmes paramètres que la partie courante.

**Questionnement** : pourrait-il y avoir _plusieurs_ Maîtres du Jeu ? Dans un tel cas, en cas d'AFK, le rôle serait ajouté sans pour autant le retirer à l'original. Pas convaincu, cela dit.

#### Déroulement d'une partie

- Une **partie** est un ensemble de tours de jeu, avec à la fin un vainqueur.
- Pendant un **tour**, chaque joueur dessine et fait deviner une fois aux autres un mot.
- Un **dessin** est, pendant un tour, le moment pour un joueur où il dessine et tente de faire deviner son mot.

Dans une partie, on dessine chacun son tour, dans un ordre aléatoire pour les gens qui sont connectés avant le début, ou d'arrivée pour les gens qui arrivent après.

##### Zone de dessin

Le joueur qui dessine se voit montré le mot, pioché au hasard dans la liste, en gros plan au milieu de la zone de dessin pendant cinq secondes, avec éventuellement un compteur (5… 4…) avant le début du chrono. Ensuite, il a 4 minutes — configurable par le créateur de la partie — pour dessiner et faire deviner le mot. Pendant ce temps, le mot reste affiché, en plus petit, sous le tableau de peintre.

**Évolution** : le chronomètre pourrait être réduit (à 30 secondes, par exemple) lorsque le mot a été deviné par au moins une personne. Il serait judicieux de proposer une option pour ce point.

Le _peintre ninja_ a divers outils de dessin pour faire deviner son mot :

- pinceaux de différentes tailles ;
- spays (éventuellement dans un second temps) de différentes tailles ;
- plusieurs couleurs de peinture ;
- possibilité de changer la couleur de fond (sans effacer le dessin) ;
- possibilité de tout effacer.

**Évolution** : les outils de peinture disponible sont configurables par le maître de partie. Il pourrait être intéressant d'avoir des parties avec des options de peinture très restreintes, ou en noir et blanc, ou…

Il est *interdit* d'écrire des lettres ou des chiffres.
**Évolution** : à terme, un système d'avertissement par les joueurs pourrait être ajouté, avec passage du tour du joueur si plus de trois avertissements. L'action finale (sanction, ou non) serait décidée par le Maître du Jeu.

##### Zone de discussion instantanée

À côté de cela, il y a une zone de discussion, avec très classiquement un champ unique d'envoi et un historique juste au dessus. Tous les joueurs peuvent écrire dedans. Ils peuvent discuter normalement ou proposer le mot qu'ils pensent être le bon.

Les messages sont affichés précédés du pseudonyme de l'envoyeur et de l'heure d'envoi, et accolés à l'avatar de l'envoyeur — ou à un avatar générique aléatoire, s'il n'en a pas. Si une même personne poste plusieurs messages à la suite, le pseudo et l'avatar ne sont pas répétés (comme sur Slack).

**Évolution** : si on veut faire moderne, afficher les avatars dans des cercles et non des carrés. Il paraît que c'est ça, la nouvelle modernité.

Un système est disponible, pour le Maître du Jeu, afin d'expulser ou de bannir un joueur de la partie. Il est également possible de rendre un joueur muet : dans un tel cas, ses messages ne sont plus transmis aux autres joueurs, mais sont toujours analysés afin qu'il puisse jouer et tenter de deviner le mot.

- Si le dessinateur entre une phrase contenant le mot ou une version proche, le message est censuré.
- Si un autre joueur entre une phrase contenant une version proche du mot, le message est censuré.
  - Dans le cas _d'un mot proche seul_, s'il n'a pas déjà gagné, il est prévenu qu'il est proche de la solution. Les autres joueurs sont prévenus (ou pas ? à discuter) que ce joueur est près de trouver.
  - Dans le cas _d'une phrase contenant un mot proche_, il est prévenu que son message n'a pas été envoyé car il contient un mot proche de la solution.
- Si un autre joueur entre une phrase contenant le mot exact, le message n'est pas transmis.
  - Dans le cas _du mot exact seul_, il est prévenu qu'il a trouvé. Les autres joueurs le sont également, et il se voit attribuer les points qu'il mérite. (Plus sur le sujet des scores dans la section suivante.)
  - Dans le cas _d'une phrase contenant le mot exact_, il est prévenu que son message n'a pas été envoyé car il contient la solution. Il est invité à envoyer un message contenant la solution _seule_ pour la valider, ceci pour éviter les gens qui envoient tout le dictionnaire dans le chat pour gagner facilement.
- Dans tous les autres cas (mot proposé faux ou message de discussion), le mot est transmis aux autres tel un message de _chat_ classique.

Si un message est censuré, cette censure est signifiée aux autres joueurs avec un message discret dans le chat, tel que « _Kévin semble proche de la solution !_ ».

La validation des mots est faite côté serveur, comme tout ce qui est validation, afin qu'il ne soit pas possible de tricher.

Si personne n'a déjà deviné, le dessinateur peut choisir de passer son tour. Il ne gagne aucun point s'il le fait.

S'il semble AFK (i.e., n'a rien dessiné 30 secondes après le début de son tour), il passe automatiquement.

Un point à discuter est celui du nombre de chats : vaut-il mieux un seul chat qui sert à discuter et à proposer une solution, ou un chat pour discuter et une zone de texte pour proposer un mot ?
L'avantage du chat unique est que les joueurs n'ont pas à changer de champ pour discuter et proposer. C'est plus efficace, surtout dans le cadre d'un jeu basé sur la vitesse. Par contre, il faut bien le faire comprendre.

Nous sommes globalement d'accord sur le fait qu'un canal unique de discussion est préférable à deux.

##### Autres composantes du déroulement d'une partie

À terme, il pourrait être envisageable de proposer aux dessins d'être enregistrés pour une partie. Une idée serait aussi, d'un point de vue visibilité sociale, de proposer de partager le dessin réalisé sur divers réseaux sociaux. Par contre, si mis en place, il faut que cette intégration reste élégante — évitons une fourmillière de boutons sociaux.

#### Système de scores

Lorsqu'un mot est deviné, le joueur ayant deviné et le dessinateur gagnent des points.

- Le dessinateur gagne trois points par joueur devinant le mot.
  Si tout le monde sans exception devine le mot, un bonus de 5 points est offert à ce dernier.
- En ce qui concerne les joueurs, ils gagnent des points en fonction de leur classement : 
  - le premier à deviner gagne dix points ;
  - le second, huit points ;
  - le troisième, six points ; 
  - le quatrième, quatre points ;
  - les autres, deux points.

Ce système est je pense améliorable. À discuter.

#### Cycle de vie des parties ; victoires

Un salon est créée par un joueur quelconque.

Une partie débute dés que lancée par le maître de jeu. On peut imaginer plusieurs types de parties :

- fin lorsque un joueur atteint un certain nombre de points ;
- fin lorsque tous les joueurs ont joué un certain nombre de tours ;
- fin après un certain temps (en laissant tout de même le tour courant se finir).

Ce choix est fait par le Maître du Jeu.

**Évolution** : on peut également envisager une partie sans fin (close lorsque les joueurs se déconnectent tous et ne reviennent pas dans le salon avant une demi-heure), à terme. Peu prioritaire, pas forcément très intéressant.

Si quelqu'un rejoint un salon alors qu'une partie est en cours, il rejoint automatiquement la partie et est ajouté au tour courant, à la fin. Par contre, il n'a pas d'avantage de points lié au fait d'être arrivé plus tard.

#### Configuration des parties

Une partie est configurable par le Maître du Jeu suivant plusieurs options.

- La liste des mots.
  _À terme, il serait envisageable de permettre de choisir plusieurs listes à utiliser en même temps._
- Le type de partie (chrono, nombre de tours, nombre de points ?).
- Le temps par tour, par défaut quatre minutes.
- **Évolution** : un mot de passe de salon de jeu.
- **Évolution** : personnalisation du système de scores.
- **Évolution** : le fait que la partie soit publique (listée sur la page d'accueil) ou non.

Il est important de réfléchir à l'interface de création de parties : elle doit être _simple_, et surtout ne pas être un gros formulaire plein de boutons et de champs, quitte à par exemple masquer certaines paramètres moins utilisés.
Une solution élégante serait de n'afficher au joueur _que_ le choix de la liste des mots et celui du caractère public ou non (lorsqu'implémenté), et de masquer le reste sous un lien « _Paramètres de la partie_ ».

Il est possible de reconfigurer les parties d'un salon ; cela dit, seuls les parties suivantes seront affectées. Les paramètres d'une partie commencée sont immutables.

Une partie peut être annulée ; elle sera alors marquée comme _nulle_ et il n'y aura pas de vainqueur. Cela peut se produire dans les cas suivants : 

- si l'intégralité des joueurs se déconnecte pendant plus d'une heure ;
- au bon vouloir du Maître du Jeu, via une option dans le menu des paramètres de la partie. S'il choisit cette option, une confirmation est demandée.

Lorsqu'une partie se termine, le salon passe en pause, avec pour le maître du jeu un gros bouton « Nouvelle partie ». Le chat reste actif en permanence. La page ressemble beaucoup à la page du jeu actif, mais sans aucun peintre actif, ni mot, ni compteur. On peut imaginer, pour faire passer le temps :

- un dessin aléatoire qui s'auto-dessine ;
- (plus fun) la possibilité pour tous les joueurs de dessiner en même temps sur le tableau.

### Listes de mots

Un joueur ayant un compte (voir plus loin) peut créer des listes de mots.

Il a pour ça, s'il est connecté, accès à une page lui permettant de créer une liste, ayant un nom et… des mots (ouais). Un grand champ de texte lui permet d'entrer un mot par ligne.
**Évolution** : un système de _tags_ est disponible pour trier la liste.

Une liste peut être configurée comme étant _mise en avant_, dans ce cas elle sera proposée sur l'accueil directement à toute personne voulant créer une partie. Seuls les administrateurs du site (ayant accès à l'admin Django) peuvent mettre une liste en avant. Ce système est pensé pour les listes “officielles”.

**Évolution** : une liste peut également être marquée par son auteur comme _publique_. Dans ce cas, sur l'écran de création de partie, via une option « listes communautaires », il est possible de la retrouver en tapant quelques mots de son titre ou de ses tags.
Si ceci est implémenté, il serait judicieux de permettre aux joueurs de cloner la liste d'un autre joueur pour y apporter des modifications personnelles. En évolution secondaire, il serait envisageable de permettre aux listes d'avoir plusieurs auteurs, ce qui permettrait une édition collaborative.

### Compte utilisateur

Les joueurs peuvent (mais c'est facultatif) créer un compte utilisateur. Dans ce cas, leurs statistiques seront enregistrées, à savoir : 

- nombre & liste des parties ;
- nombre total de points gagnés ;
- nombre total de mots dessinés devinés par au moins une personne ;
- nombre total de mots dessinés devinés par _tout le monde_ ;
- nombre de devinages corrects ;
- nombre d'incorrects ;
- nombre de parties gagnées.

Ouvrir un compte offre également l'accès à l'éditeur de listes mentionné plus haut, permet de simplifier un peu l'usage du site (plus de pseudo demandé lorsqu'un salon est rejoint), et offre la possibilité d'avoir un avatar (?).

À terme, des tableaux de scores pourraient être publiés, pour les gens ayant un compte (sur le mois précédent et tout le temps). Les rangs auraient un nom, par exemple :

1. Maître Ninja ;
2. Ninja ceinture noire ;
3. <nom d'un peintre>…

## Notes d'implémentation technique

### Ordre d'implémentation

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

   *À ce niveau, on pourra ouvrir en bêta.*
4. Systèmes plus avancés : 
   - passage du rôle de Maître du Jeu à quelqu'un d'autre ;
   - pages de statistiques des joueurs connectés ;
   - sauvegarde des images ;
   - partage & clônage des listes ;
   - …

### Idées d'implémentation du dessin en temps réel

Le dessin se fait sur un _canvas_, avec des événements au clic & au maintient en fonction de l'outil actuellement choisi.

Pour le joueur, le temps entre deux vérifications de brossage est court, au maximum un dixième de secondes, pour que le dessin soit confortable et non saccadé.

Pour la transmission, lorsque le joueur dessine, une zone (initialement carrée, mais à terme, la forme pourrait être optimisée) contenant les pixels modifiés est en permanence mise à jour chez le client ; toutes les demi-secondes, la position et le contenu de cette zone sont copiés et envoyés par websocket au serveur, qui se charge de :

- recombiner l'image avec l'image qu'il stocke localement en mémoire, en permanence ;
- transférer le bout d'image et sa position aux autres clients, pour qu'ils recombinent le bout d'image avec ce qu'ils ont et mettent ainsi l'affichage à jour chez les autres joueurs.

Contrairement aux autres Pictonary en ligne, l'idée est d'éviter de transférer le dessin au _relâchement de la souris_ uniquement et _en entier à chaque fois_ afin :

- de proposer un vrai dessin en temps réel aux autres joueurs ;
- d'optimiser la consommation réseau de l'application.

### Puissance nécessaire par salon

Pour chaque salon l'image entière courante est stockée en mémoire, afin de pouvoir l'envoyer à tout nouveau client. Ceci plus les données du salon chargées en mémoire et le traitement des messages, on peut estimer que chaque salon nécessite quelques Mio de mémoire vive et un peu de puissance de calcul pour recombiner les pixels de l'image toutes les demi-secondes lorsque quelque chose est dessiné.

Cette valeur peut être revue à la baisse vu que si rien ne change dans le dessin au bout d'une demi-seconde, rien n'est envoyé (logique).

### Définition d'un protocole WebSockets

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

Voir aussi si Django – Channels ne propose pas quelque chose de natif pour gérer ça, mais il me semble que non.

### Interface

Il serait cool d'avoir un graphiste participant au projet. Laurie a mentionné son intérêt.