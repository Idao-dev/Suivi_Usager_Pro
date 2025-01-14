"""
Module implémentant le pattern Observer pour la gestion des événements et la mise à jour des vues.
Ce pattern permet de maintenir une cohérence entre les objets liés sans créer de couplage fort.
"""

from abc import ABC, abstractmethod

class Observable:
    """
    Classe de base pour les objets qui peuvent être observés.
    Permet de notifier automatiquement tous les observateurs lors de changements.
    
    Utilisé principalement pour :
    - La mise à jour des vues quand les données changent
    - La synchronisation entre différentes parties de l'interface
    - La propagation des événements dans l'application
    """

    def __init__(self):
        """Initialise la liste des observateurs."""
        self._observers = []

    def add_observer(self, observer):
        """
        Ajoute un nouvel observateur à la liste.
        
        Args:
            observer (Observer): L'observateur à ajouter
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        """
        Retire un observateur de la liste.
        
        Args:
            observer (Observer): L'observateur à retirer
        """
        self._observers.remove(observer)

    def notify_observers(self, *args, **kwargs):
        """
        Notifie tous les observateurs d'un changement.
        
        Args:
            *args: Arguments positionnels à passer aux observateurs
            **kwargs: Arguments nommés à passer aux observateurs
        """
        for observer in self._observers:
            observer.update(*args, **kwargs)

class Observer(ABC):
    """
    Classe abstraite définissant l'interface pour les observateurs.
    Doit être héritée par toutes les classes qui souhaitent observer des objets Observable.
    """
    
    @abstractmethod
    def update(self, observable, *args, **kwargs):
        """
        Méthode appelée lorsqu'un Observable notifie un changement.
        
        Args:
            observable: L'objet Observable qui a déclenché la mise à jour
            *args: Arguments positionnels passés par l'Observable
            **kwargs: Arguments nommés passés par l'Observable
        """
        pass
