# SliceSticks

---

# Stick Fighter

A fast-paced, physics-driven 2D action game built with **Pygame**. Take control of a skilled stick figure warrior, battle waves of enemies, unlock powerful weapons, and take down massive bosses. This project utilizes an event-driven architecture with a custom physics and animation engine to deliver smooth, dynamic stick-figure combat.

---

## Features

*   **Dynamic Animation System**: Procedural animations for walking, jumping, and attacking with multiple weapon types[cite: 1].
*   **Weapon Variety**: Choose your playstyle with Fists, Swords, Axes, or Bows—each with unique hitboxes and animation sets[cite: 1, 5].
*   **RPG Elements**: Level up your character, earn tokens, and distribute stat points into HP, Attack, Defense, and Mana[cite: 1, 5].
*   **Skill System**: Unleash special abilities like *Mana Gloves* and *Mana Surge* to turn the tide of battle[cite: 6].
*   **Wave-Based Combat**: Face increasingly difficult enemies, culminating in a challenging Boss fight every 10 kills[cite: 4].
*   **VFX & Juice**: Includes screen shake, floating combat text, and particle effects for satisfying impact feedback[cite: 4].

---

## Installation

1.  **Requirement**: Ensure you have Python 3.x and Pygame installed.
    ```bash
    pip install pygame
    ```
2.  **Project Structure**: Ensure your files are organized as follows:
    *   `main.py`: The entry point[cite: 3].
    *   `entities.py`: Character and enemy logic[cite: 1].
    *   `managers.py`: Physics, VFX, and Wave logic[cite: 4].
    *   `ui.py`: HUD and menu systems[cite: 5].
    *   `skills.py`: Skill classes[cite: 6].
    *   `core.py`: Singleton and Event Bus[cite: 7].
    *   `config.py`: Constants and game settings[cite: 2].

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

*   **Event-Driven**: Uses a central `EventBus` to decouple systems (e.g., an entity dying triggers experience gain, VFX, and wave updates simultaneously)[cite: 3, 7].
*   **Singleton Managers**: Core systems like `PhysicsManager` and `VFXManager` are implemented as Singletons for easy access across the codebase[cite: 4, 7].
*   **Procedural Figures**: Stick figures are drawn using vector lines and circles, allowing for "hit flash" effects and "squash and stretch" during movement[cite: 1].

---

## Gameplay Mechanics

*   **Combat**: Attacks are registered via `attack_rect` hitboxes that appear during specific animation frames[cite: 1, 4].
*   **Bosses**: After 10 kills, a Boss spawns with 5x health and a special **Charge Attack** that deals massive damage[cite: 1, 4].
*   **Progression**: Killing enemies grants **XP** (to level up and gain stat points) and **Tokens** (to buy better weapons in the shop)[cite: 3, 5].

---
