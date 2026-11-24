# Spek — usage du registre fédéré diK en entrée éditoriale

**Statut : interface candidate, aucune publication ni affectation approuvée.**

Le registre dérivé de diK sert à **référencer** les identités Kristal avec leur
namespace et les Q/P Wikidata explicitement revus. Il ne remplace ni la preuve
Framework, ni les six sections agricoles (`soil`,`crop`,`inputs`,`practices`,
`yield`,`cross`), ni les registres de compositions Spek.

Le nouvel outil :

```
python tools/dik_federation_preflight.py --dir <répertoire de sortie diK>
```

ne vérifie que l'intégrité locale du snapshot. `INTEGRITY_ONLY` n'est **pas**
une autorisation de lancer `build`, d'affecter un template, d'accepter une
proposition éditoriale ni de publier via les gates C1/C2/C3/C4.

`KQ` seul est interdit pour le référencement croisé ; il faut toujours
`namespace_id+KQ/KP`. Les liens Wikidata `Q/P` ne créent pas des références
locales. Les liens `candidate`, `relatedMatch`, `closeMatch` et les observations
EncyK ne sont pas des équivalences exactes pour une page.

La politique diK cible 13 langues sans `no`, mais ne garantit aucune
réalisation GF, ni couverture dans une langue donnée. Conserver les décisions
éditoriales et runtime Spek indépendantes. La publication reste opt-in.
