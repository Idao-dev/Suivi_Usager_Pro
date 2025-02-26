"""
Tests unitaires pour le module observer.py.
Ces tests vérifient le bon fonctionnement du pattern Observer.
"""

import pytest
from src.utils.observer import Observable, Observer

class MockObserver(Observer):
    """Classe d'observateur simulée pour les tests."""
    
    def __init__(self):
        """Initialise le compteur d'appels et les arguments reçus."""
        self.update_called = 0
        self.last_args = None
        self.last_kwargs = None
        self.last_observable = None
    
    def update(self, observable, *args, **kwargs):
        """
        Méthode appelée lorsqu'un Observable notifie un changement.
        Garde une trace des appels et des arguments reçus.
        """
        self.update_called += 1
        self.last_observable = observable
        self.last_args = args
        self.last_kwargs = kwargs

class ConcreteObservable(Observable):
    """Classe Observable concrète pour les tests."""
    
    def __init__(self):
        """Initialise la classe parent."""
        super().__init__()
        self.value = 0
    
    def set_value(self, value):
        """
        Définit une valeur et notifie les observateurs.
        
        Args:
            value: La nouvelle valeur
        """
        self.value = value
        self.notify_observers(self, "value_changed", new_value=value)

class TestObservable:
    """Tests pour la classe Observable."""
    
    def test_add_observer(self):
        """Teste l'ajout d'un observateur."""
        observable = Observable()
        observer = MockObserver()
        
        observable.add_observer(observer)
        
        assert len(observable._observers) == 1
        assert observable._observers[0] == observer
    
    def test_add_duplicate_observer(self):
        """Teste l'ajout d'un observateur déjà présent."""
        observable = Observable()
        observer = MockObserver()
        
        observable.add_observer(observer)
        observable.add_observer(observer)  # Ajout du même observateur
        
        assert len(observable._observers) == 1  # L'observateur ne doit être présent qu'une fois
    
    def test_remove_observer(self):
        """Teste la suppression d'un observateur."""
        observable = Observable()
        observer = MockObserver()
        
        observable.add_observer(observer)
        observable.remove_observer(observer)
        
        assert len(observable._observers) == 0
    
    def test_notify_observers(self):
        """Teste la notification des observateurs."""
        observable = Observable()
        observer1 = MockObserver()
        observer2 = MockObserver()
        
        observable.add_observer(observer1)
        observable.add_observer(observer2)
        
        # Notification avec des arguments
        observable.notify_observers(observable, "test_arg", test_kwarg="test_value")
        
        # Vérifier que les deux observateurs ont été notifiés
        assert observer1.update_called == 1
        assert observer2.update_called == 1
        
        # Vérifier que les arguments ont été correctement transmis
        assert observer1.last_args == ("test_arg",)
        assert observer1.last_kwargs == {"test_kwarg": "test_value"}
        assert observer2.last_args == ("test_arg",)
        assert observer2.last_kwargs == {"test_kwarg": "test_value"}
        assert observer1.last_observable == observable
    
    def test_observable_interaction(self):
        """Teste l'interaction entre Observable et Observer."""
        observable = ConcreteObservable()
        observer = MockObserver()
        
        observable.add_observer(observer)
        
        # Définir une valeur qui déclenchera une notification
        observable.set_value(42)
        
        # Vérifier que l'observateur a été notifié
        assert observer.update_called == 1
        assert observer.last_args == ("value_changed",)
        assert observer.last_kwargs == {"new_value": 42}
        assert observer.last_observable == observable
        
        # Modifier à nouveau la valeur
        observable.set_value(100)
        
        # Vérifier que l'observateur a été notifié une seconde fois
        assert observer.update_called == 2
        assert observer.last_kwargs == {"new_value": 100} 