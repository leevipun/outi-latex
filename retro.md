Retro 1.0 - 17.11.2025

Koko tiimin mielestä ohjelmointi sujui hyvin ja työoli jaettu tasasisesti. Ryhmäläiset nostivat esille muun muassa tyytyväisyyttä työnjakoon ja siihen, että jokainen sai itse vaikuttaa siihen mitä teki. 

Ryhmäläiset kertoivat, että projektin alku setup oli hieman raskas ja tämä johtui heidän mukaansa siitä, että PostgreSQL ei ollut heille tuttu. Tutustumisen jälkeen tekeminen muttui helpommaksi ja positiivisemmaksi. Myös testien tekeminen osoittautui osin hankalammaksi mitä olimme ajatelleet.
Osittain committien vähyys teki katselmoinnista hieman hankalampaa, vaikka katselmointi tehtiin Feature haarojen PR-vaiheessa. Yksi ryhmästä katselmoi suurimman osan PR:sta, joka kävi raskaaksi. 

CI-pipelinen tekeminen oli hermoja koetteleva kokemus. Kukaan ei pitänyt siitä. 

Kehitysideaoita:
- Enemmän committeja. Ei kaikkea vain yhteen committiin.
- Jokainen katselmoi ainakin yhden PR:n spritin aikana

Retro 2.0 - 24.11.2025

Committien määrä kasvoi joka helpotti katselmointia. Omat osuudet sujui hyvin ja ryhmä on tyytyväinen viikon suorituksiin. Jokainen sai katselmoida ainakin yhden PR:n tällä viikolla

Robotti testien kanssa ongelmia. Bibtex tiedoston tarkistaminen hankalaa. Robotti testit olivat kaikille suht hankalaa. Yksi ryhmäläinen nosti esille muutaman ärsyttävän bugin, mutta ne hoidettiin hienosti pois alta.

Kenelläkään ei ollut suurempia murheita, mutta CI-pipeline testien epäonnistuminen ärsytti kaikkia tiimiläisiä. Se kuuluu kuitenkin asiaan, koska pipline testit ovat tarkoituksella sellaisia, että tuotantoon ei pääse kuin testattua koodia.

Hyvillä mielillä suuntaamme kohti seuraavan sprintin storyjä ja haasteita.

Kehitysideaoita:
- Enemmän robotti testejä seuraavassa sprintissä.
- Valmistautuminen asiakaspalaveriin on parempi ja tietokanta on varmistettu toimivaksi.

Retro 3.0 - 1.12.2025

Tässä sprintissä robotti testejä saatiin tehty enemmän ja asiakaspalaveriin valmistauduttiin niin, että tapaaminen sujui hyvin. Tiimillä nousi tämän sprintin tiimoilta positiivisina puolina filtteröinnin toteuttaminen, jossa sorttauksen toteutus oli hauskaa. Myös nav barin ja UI:n toteuttaminen sujui hyvin. Yllättäen myös tietokannan muokkaus avainsanojen osalta sujui ilman suurempia vaivoja.

Tiimissä nousi myös harmitusta, ettei kuutta tuntia saa oikein ylittää. Negatiivinen puoli oli myös robotti testien kirjottamisen vaikeus dark moden testaukseen ja muut siinä ilmenneet ongelmat. Myös liian yksinkertainen homma aiheutti murhetta.

Kovin suuria tunteita ei tämä sprintti aiheuttanut, mutta yhtä tiimiläistä harmitti, ettei päässyt asiakastapaamiseen edellisellä kerralla. Myös robotti testit aiheuttivat hiukan murhetta, mutta kaikesta selvittiin.

Kehitysideoita:
* UI:sta tehdään yhtenäisempi
* Lisenssiin kaikkien nimet
