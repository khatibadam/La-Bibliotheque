# Sujets de TP Fil Rouge - Formation Python

## TP 1 : Système de Gestion de Bibliothèque

## Vue d'ensemble

Développer une API REST complète pour gérer une bibliothèque moderne incluant la gestion des livres, des
auteurs, des emprunts et un système de recherche avancé. L'accent est mis sur la modélisation
relationnelle, la validation des données et les règles métier.

## Contexte métier

Une bibliothèque municipale souhaite moderniser son système de gestion. Le système doit permettre de
cataloguer les ouvrages, suivre les emprunts, gérer les retards et fournir des statistiques d'utilisation. Les
bibliothécaires ont besoin d'une interface API pour intégrer avec leur système existant.

## Phase 1 : Modélisation et Structure

Modèles de données à concevoir

Book (Livre) Représente un ouvrage dans le catalogue de la bibliothèque.

Attributs requis :

```
Identifiant unique
Titre de l'ouvrage
Code ISBN au format ISBN-13 (validation stricte)
Année de publication (entre 1450 et année courante)
Référence vers l'auteur
Nombre d'exemplaires disponibles
Nombre total d'exemplaires possédés
Description textuelle (optionnelle)
Catégorie littéraire (énumération : Fiction, Science, Histoire, Philosophie, etc.)
Langue de publication
Nombre de pages
Maison d'édition
```
Contraintes métier :

```
Le nombre d'exemplaires disponibles ne peut jamais dépasser le total
L'ISBN doit être unique dans le système
Un livre ne peut être supprimé s'il existe des emprunts actifs
```
Author (Auteur) Représente un écrivain ou contributeur.

Attributs requis :


```
Identifiant unique
Prénom
Nom de famille
Date de naissance
Nationalité (code pays ISO)
Biographie (texte long, optionnel)
Date de décès (optionnelle)
Site web ou URL de référence (optionnel)
```
Contraintes métier :

```
Le nom complet doit être unique
Un auteur peut avoir écrit plusieurs livres
Un auteur ne peut être supprimé si des livres lui sont associés
```
Loan (Emprunt) Représente un prêt de livre à un usager.

Attributs requis :

```
Identifiant unique
Référence vers le livre emprunté
Nom complet de l'emprunteur
Email de contact de l'emprunteur
Numéro de carte de bibliothèque
Date et heure de l'emprunt
Date limite de retour (calculée automatiquement)
Date et heure de retour effectif (null si non retourné)
Statut de l'emprunt (actif, retourné, en retard)
Commentaires éventuels du bibliothécaire
```
Contraintes métier :

```
Un usager ne peut emprunter plus de 5 livres simultanément
La durée standard d'emprunt est de 14 jours
Un livre retourné en retard génère une pénalité calculée
Un livre ne peut être emprunté que s'il reste des exemplaires disponibles
```
LoanHistory (Historique) Pour la traçabilité et les statistiques.

Attributs requis :

```
Référence vers le livre
Statistiques d'emprunts (nombre total, durée moyenne)
Popularité du livre (calculée)
```
## Phase 2 : API REST - Endpoints à implémenter

Gestion des livres

Endpoint de listing


```
Récupérer la liste complète des livres avec pagination
Paramètres de pagination : numéro de page, taille de page
Réponse paginée avec métadonnées (total, page courante, pages totales)
Tri possible par titre, auteur, année, popularité
Ordre croissant ou décroissant
```
Endpoint de détail

```
Récupérer les informations complètes d'un livre spécifique
Inclure les informations de l'auteur associé
Inclure les statistiques d'emprunts
Gérer le cas où le livre n'existe pas (erreur 404)
```
Endpoint de création

```
Créer un nouveau livre dans le catalogue
Valider tous les champs obligatoires
Vérifier l'unicité de l'ISBN
Vérifier l'existence de l'auteur référencé
Retourner le livre créé avec son identifiant
```
Endpoint de modification

```
Mettre à jour les informations d'un livre existant
Modification partielle ou complète
Valider les changements avant application
Interdire la modification si emprunts actifs (certains champs)
Retourner le livre mis à jour
```
Endpoint de suppression

```
Supprimer un livre du catalogue
Vérifier qu'aucun emprunt n'est actif
Suppression logique recommandée (soft delete)
Retourner une confirmation de suppression
```
Endpoint de recherche avancée

```
Recherche par titre (correspondance partielle, insensible à la casse)
Recherche par nom d'auteur
Recherche par ISBN exact
Recherche par catégorie
Recherche par année de publication (plage ou année exacte)
Recherche par langue
Filtrage par disponibilité (disponible ou non)
Combinaison de critères avec opérateur ET
Résultats paginés
```
Gestion des auteurs


Endpoints CRUD complets

```
Lister tous les auteurs (paginé)
Détails d'un auteur avec liste de ses livres
Créer un nouvel auteur
Modifier les informations d'un auteur
Supprimer un auteur (si aucun livre associé)
```
Endpoint de recherche

```
Recherche par nom (prénom ou nom de famille)
Recherche par nationalité
Tri par nom, date de naissance
```
Gestion des emprunts

Endpoint de création d'emprunt

```
Emprunter un livre disponible
Valider la disponibilité du livre
Vérifier que l'utilisateur n'a pas atteint sa limite
Décrémenter automatiquement les exemplaires disponibles
Calculer automatiquement la date limite de retour
Envoyer une confirmation (simulation)
```
Endpoint de retour

```
Marquer un livre comme retourné
Calculer si retour en retard
Calculer la pénalité éventuelle
Incrémenter les exemplaires disponibles
Mettre à jour les statistiques
```
Endpoint de consultation des emprunts

```
Lister les emprunts actifs (non retournés)
Lister les emprunts en retard
Lister l'historique complet des emprunts
Filtrer par utilisateur (email ou carte)
Filtrer par livre
Filtrer par période
```
Endpoint de renouvellement

```
Prolonger la durée d'un emprunt actif
Valider qu'il n'y a pas de réservation en attente
Maximum 1 renouvellement par emprunt
Ajouter 14 jours supplémentaires
```
Endpoints de statistiques


Statistiques globales

```
Nombre total de livres dans le catalogue
Nombre d'exemplaires totaux
Nombre d'emprunts actifs
Nombre d'emprunts en retard
Taux d'occupation de la bibliothèque
```
Statistiques par livre

```
Nombre total d'emprunts historiques
Durée moyenne des emprunts
Nombre de fois en retard
Classement de popularité
```
Statistiques par auteur

```
Nombre total d'ouvrages
Nombre d'emprunts cumulés
Auteurs les plus populaires
```
Endpoint de rapports

```
Générer un rapport mensuel (format JSON)
Export des données en CSV
Livres jamais empruntés
Usagers les plus actifs
```
## Phase 3 : Validation et Règles métier

Validations Pydantic à implémenter

Validation de l'ISBN

```
Format ISBN-13 : XXX-XXXXXXXXXX ou XXXXXXXXXXXXX
Validation du checksum selon l'algorithme ISBN
Message d'erreur explicite en cas de format invalide
```
Validation des emails

```
Format email valide selon RFC
Normalisation en minuscules
Domaine de l'email doit être valide
```
Validation des dates

```
Date de naissance de l'auteur : ne peut être future
Année de publication : entre 1450 et année courante
Date d'emprunt : ne peut être future
Date de retour : doit être postérieure à la date d'emprunt
```

```
Validation de cohérence temporelle
```
Validation des quantités

```
Exemplaires disponibles : >= 0
Total d'exemplaires : > 0
Disponibles <= Total
Nombre de pages : > 0
```
Validation des énumérations

```
Catégories prédéfinies avec liste fermée
Statuts d'emprunt prédéfinis
Codes pays ISO pour nationalités
```
Validators personnalisés

```
Vérification que l'auteur existe lors de la création d'un livre
Vérification de la disponibilité avant création d'emprunt
Calcul automatique de la date limite de retour
Détection automatique du statut d'emprunt (actif/retard)
```
Règles métier complexes

Gestion de la disponibilité

```
Décrémentation atomique lors d'un emprunt
Incrémentation atomique lors d'un retour
Gestion des conditions de course (race conditions)
Transaction complète : validation + modification
```
Calcul des pénalités

```
Formule : nombre de jours de retard × taux journalier
Plafond maximum de pénalité
Arrondi à 2 décimales
Ajout dans la réponse de retour
```
Limitation des emprunts

```
Comptage des emprunts actifs par utilisateur
Vérification avant création de nouvel emprunt
Message d'erreur explicite si limite atteinte
Possibilité de configurer la limite par profil
```
## Phase 4 : Qualité et Bonnes pratiques

Structure du projet

Organisation recommandée des fichiers :


```
Séparation stricte des couches (routes, services, repositories, models)
Configuration centralisée (constantes, paramètres)
Schemas Pydantic séparés des modèles de persistance
Utilitaires communs (validateurs, formateurs, calculs)
Tests organisés par modules
```
Formatage et conventions

Black - Formatage automatique

```
Configuration dans pyproject.toml
Longueur de ligne à 88 caractères (ou 100 selon préférence équipe)
Application automatique sur tous les fichiers Python
Intégration dans pre-commit hooks
```
isort - Organisation des imports

```
Tri automatique des imports
Séparation claire : stdlib, third-party, local
Ordre alphabétique dans chaque section
Cohérent avec Black
```
Flake 8 - Linting

```
Vérification PEP 8
Détection des variables inutilisées
Détection du code mort
Complexité cyclomatique limitée
Configuration des règles dans .flake 8
```
mypy - Vérification des types

```
Mode strict recommandé
Vérification de tous les type hints
Détection des incompatibilités de types
Gestion des types optionnels
```
Pylint - Analyse statique avancée

```
Vérification des conventions de nommage
Détection de code dupliqué
Suggestions d'améliorations
Score minimal requis (8/10 recommandé)
```
Documentation

Docstrings

```
Format Google ou NumPy
Documentation de toutes les fonctions publiques
Description des paramètres et retours
```

```
Exemples d'utilisation pour les fonctions complexes
```
OpenAPI / Swagger

```
Description détaillée de chaque endpoint
Exemples de requêtes et réponses
Documentation des codes d'erreur
Schémas de validation visibles
Tags pour regrouper les endpoints
```
README complet

```
Description du projet
Prérequis et dépendances
Instructions d'installation étape par étape
Configuration de l'environnement
Lancement de l'application
Exécution des tests
Endpoints disponibles avec exemples curl
```
Tests

Tests unitaires

```
Couverture minimale de 80 %
Tests de toutes les validations Pydantic
Tests des règles métier
Tests des cas limites et erreurs
Fixtures pytest réutilisables
```
Tests d'intégration

```
Tests des endpoints complets
Scénarios utilisateur bout en bout
Test de création → lecture → modification → suppression
Tests de scénarios d'emprunt complets
```
Tests de validation

```
Données valides acceptées
Données invalides rejetées avec messages appropriés
Tests des contraintes uniques
Tests des contraintes de cohérence
```
Gestion d'erreurs

Exceptions personnalisées

```
BookNotFoundException
AuthorNotFoundException
BookNotAvailableException
```

```
LoanLimitExceededException
InvalidISBNException
```
Handlers d'erreurs globaux

```
Formatage cohérent des erreurs
Codes HTTP appropriés (404, 400, 422, 500)
Messages d'erreur explicites en français
Logs des erreurs serveur
Pas d'exposition de détails sensibles
```
Validation des entrées

```
Validation au niveau Pydantic
Validation métier supplémentaire dans les services
Messages d'erreur clairs et actionnables
Indication du champ en erreur
```
## Phase 5 : Fonctionnalités avancées

Cache et Performance

Mise en cache

```
Cache des listes d'auteurs (peu de modifications)
Cache des statistiques (recalculées périodiquement)
TTL (Time To Live) adapté par type de donnée
Invalidation du cache lors des modifications
```
Optimisation des requêtes

```
Pagination systématique des listes
Limitation du nombre de résultats
Eager loading pour éviter N+1 queries
Index sur les champs recherchés fréquemment
```
Export de données

Format CSV

```
Export de la liste des livres
Export des emprunts sur une période
En-têtes explicites
Encodage UTF-8 avec BOM
```
Format Excel

```
Feuilles multiples (livres, auteurs, emprunts)
Formatage des colonnes (dates, nombres)
Filtres automatiques
```

```
Création via openpyxl
```
Format PDF

```
Génération de rapports de statistiques
Mise en page professionnelle
Graphiques de statistiques (matplotlib)
Export via reportlab
```
Logging et Monitoring

Logging structuré

```
Niveaux appropriés (DEBUG, INFO, WARNING, ERROR)
Format JSON pour parsing automatique
Rotation des fichiers de logs
Logs différenciés par environnement
```
Métriques

```
Nombre de requêtes par endpoint
Temps de réponse moyen
Taux d'erreur
Nombre d'emprunts créés/retournés
```
Sécurité

Validation stricte

```
Sanitization des entrées utilisateur
Protection contre injection SQL (via ORM)
Limitation de la taille des payloads
Rate limiting global
```
Headers de sécurité

```
CORS configuré proprement
Headers de sécurité standards
Pas d'exposition d'informations sensibles dans les erreurs
```
## Livrables attendus

Code source

```
Repository Git propre avec historique cohérent
Commits atomiques et messages explicites
Branches feature si développement collaboratif
.gitignore approprié (venv, cache, IDE)
```
Documentation


```
README complet et à jour
Documentation API accessible via Swagger
Schémas de données visuels (optionnel mais apprécié)
Guide de contribution (si projet collaboratif)
```
Configuration

```
requirements.txt ou pyproject.toml
Fichier de configuration pour les outils (Black, Flake8, mypy)
Variables d'environnement documentées
Script de setup automatisé
```
Tests

```
Suite de tests complète et passante
Coverage report
Instructions pour exécuter les tests
Données de test (fixtures)
```

