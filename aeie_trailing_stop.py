# aeie_trailing_stop.py
from config import AEIE_TRIGGER, AEIE_TRAIL

class AEIETrailingStop:
    """
    Gestor de trailing stop AEIE para una posición abierta.
    """
    def __init__(self, entry_price, direction, initial_stop):
        self.entry_price = entry_price
        self.direction = direction
        self.initial_stop = initial_stop
        self.current_stop = initial_stop
        self.peak_price = entry_price
        self.activated = False

    def update(self, current_price):
        """
        Actualiza el trailing stop basado en el precio actual.
        Retorna el nuevo stop loss o None si no hay cambio.
        """
        if self.direction == 'LONG':
            if current_price > self.peak_price:
                self.peak_price = current_price
            profit_pct = (current_price - self.entry_price) / self.entry_price
            if not self.activated and profit_pct >= AEIE_TRIGGER:
                self.activated = True
                self.current_stop = self.peak_price * (1 - AEIE_TRAIL)
            elif self.activated:
                new_stop = self.peak_price * (1 - AEIE_TRAIL)
                if new_stop > self.current_stop:
                    self.current_stop = new_stop
        else:
            if current_price < self.peak_price:
                self.peak_price = current_price
            profit_pct = (self.entry_price - current_price) / self.entry_price
            if not self.activated and profit_pct >= AEIE_TRIGGER:
                self.activated = True
                self.current_stop = self.peak_price * (1 + AEIE_TRAIL)
            elif self.activated:
                new_stop = self.peak_price * (1 + AEIE_TRAIL)
                if new_stop < self.current_stop:
                    self.current_stop = new_stop
        return self.current_stop

    def check_stop(self, current_price):
        """
        Verifica si se ha alcanzado el stop loss.
        Retorna True si se debe cerrar.
        """
        if self.direction == 'LONG':
            return current_price <= self.current_stop
        else:
            return current_price >= self.current_stop
      
