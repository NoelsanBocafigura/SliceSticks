# SliceSticks

---

# Stick Fighter

A fast-paced, physics-driven 2D action game built with **Pygame**. Take control of a skilled stick figure warrior, battle waves of enemies, unlock powerful weapons, and take down massive bosses. This project utilizes an event-driven architecture with a custom physics and animation engine to deliver smooth, dynamic stick-figure combat.

---

## Features

*   **Dynamic Animation System**: Procedural animations for walking, jumping, and attacking with multiple weapon types.
*   **Weapon Variety**: Choose your playstyle with Fists, Swords, Axes, or Bows—each with unique hitboxes and animation sets.
*   **RPG Elements**: Level up your character, earn tokens, and distribute stat points into HP, Attack, Defense, and Mana.
*   **Skill System**: Unleash special abilities like *Mana Gloves* and *Mana Surge* to turn the tide of battle.
*   **Wave-Based Combat**: Face increasingly difficult enemies, culminating in a challenging Boss fight every 10 kills.
*   **VFX & Juice**: Includes screen shake, floating combat text, and particle effects for satisfying impact feedback.

---

## Installation

1.  **Requirement**: Ensure you have Python 3.x and Pygame installed.
    ```bash
    pip install pygame
    ```
2.  **Project Structure**: Ensure your files are organized as follows:
    *   `main.py`: The entry point.
    *   `entities.py`: Character and enemy logic.
    *   `managers.py`: Physics, VFX, and Wave logic.
    *   `ui.py`: HUD and menu systems.
    *   `skills.py`: Skill classes.
    *   `core.py`: Singleton and Event Bus.
    *   `config.py`: Constants and game settings.

3.  **Run the Game**:
    ```bash
    python main.py
    ```

---

## Controls

| Action | Key |
| :--- | :--- |
| **Move Left / Right** | `Left Arrow` / `Right Arrow` |
| **Jump** | `Space` |
| **Basic Attack** | `A` |
| **Mana Gloves (Skill)** | `S` |
| **Mana Surge (Skill)** | `D` |
| **Stat Menu** | `M` |
| **Skill Menu** | `K` |
| **Weapon Shop** | `B` |
| **Pause Game** | `P` or `Esc` |

---

## Architecture Overiew

*   **Event-Driven**: Uses a central `EventBus` to decouple systems (e.g., an entity dying triggers experience gain, VFX, and wave updates simultaneously).
*   **Singleton Managers**: Core systems like `PhysicsManager` and `VFXManager` are implemented as Singletons for easy access across the codebase.
*   **Procedural Figures**: Stick figures are drawn using vector lines and circles, allowing for "hit flash" effects and "squash and stretch" during movement.

---

## Gameplay Mechanics

*   **Combat**: Attacks are registered via `attack_rect` hitboxes that appear during specific animation frames.
*   **Bosses**: After 10 kills, a Boss spawns with 5x health and a special **Charge Attack** that deals massive damage.
*   **Progression**: Killing enemies grants **XP** (to level up and gain stat points) and **Tokens** (to buy better weapons in the shop).

---
