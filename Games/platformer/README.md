# Platformer Game

A simple 2D platformer game built with Pygame. Collect all the stars to complete each level!




## Controls

- **Arrow Keys** or **A/D** - Move left/right
- **Up Arrow**, **W**, or **Space** - Jump
- **R** - Restart current level
- **ESC** - Return to menu
- **Mouse** - Click buttons in menus

## How to Play

1. Start from the main menu and select a level
2. Move your character using arrow keys or WASD
3. Collect all 3 stars (⭐) in each level
4. Avoid falling into spikes (🔺) or falling off the map
5. Once you collect all stars, you win and can proceed to the next level

## File Structure

```
platformer/
├── main.py              # Main game logic
├── classes.py           # Game classes (Player, Map, etc.)
├── img/                # Game textures
│   ├── player.png
│   ├── ground.png
│   ├── grass.png
│   ├── stone.png
│   ├── platform.png
│   ├── spike.png
│   ├── star.png
│   └── wall.png
└── maps/                # Level files (.map)
```

## Creating Textures

All textures should be **32x32 pixels** PNG files in the `img/` directory:

- **player.png** - Player character (blue/red/green square)
- **ground.png** - Brown dirt block
- **grass.png** - Grass-topped ground block
- **stone.png** - Gray stone block
- **platform.png** - Wooden/metal platform
- **spike.png** - Red/orange danger spikes
- **star.png** - Yellow/gold collectible star
- **wall.png** - Dark boundary wall

## Creating Custom Levels

Create `.map` files in the `maps/` folder using these characters:

| Character | Tile Type |
|-----------|-----------|
| `0` or space | Empty air |
| `1` | Ground/Dirt block |
| `2` | Grass block |
| `3` | Stone block |
| `4` | Platform |
| `5` | Spike (kills player) |
| `W` | Wall block |
| `S` | Star (collectible) |
| `P` | Player spawn point |

### Example Map:
```
WWWWWWWWWWWWWWWWWW
W0000000000000000W
W00P00000000000S0W
W222000000000222W
W11100000000011W
W1110555555501111W
W1112222222221111W
WWWWWWWWWWWWWWWWWW
```

### Map Guidelines:
- Always surround your map with `W` (walls) to prevent player from escaping
- Place exactly 3 `S` (stars) in each level
- Place one `P` (player spawn point)

