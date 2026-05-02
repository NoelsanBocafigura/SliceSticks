from abc import ABC, abstractmethod

# ---------------------------- Skills ----------------------------
class Skill(ABC):
    def __init__(self, name, mana_cost, cooldown):
        self.name = name
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.level = 1

    def can_use(self, player):
        return (self.current_cooldown <= 0 and player.mana >= self.mana_cost)

    @abstractmethod
    def activate(self, player):
        pass

    def update_cooldown(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

class ManaGlovesSkill(Skill):
    def __init__(self):
        super().__init__("Mana Gloves", 10, 60)
        
    def activate(self, player):
        player.mana -= self.mana_cost
        self.current_cooldown = self.cooldown
        multiplier = 0.5 + (self.level * 0.1)
        player.skill_effects.append({
            'type': 'mana_gloves',
            'duration': 60 * 5,
            'damage_boost': player.attack_power * multiplier
        })

class ManaSurgeSkill(Skill):
    def __init__(self):
        super().__init__("Mana Surge", 30, 300)
        
    def activate(self, player):
        player.mana -= self.mana_cost
        self.current_cooldown = self.cooldown
        orig_atk = player.attack_power
        boost = 1.15 + (self.level * 0.05)
        player.attack_power *= boost
        player.skill_effects.append({
            'type': 'mana_surge',
            'duration': 60 * 8,
            'remove': lambda: setattr(player, 'attack_power', orig_atk)
        })