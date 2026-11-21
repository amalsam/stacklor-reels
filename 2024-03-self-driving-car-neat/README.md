# Self-driving car learns a track with NEAT

Cars are controlled by small neural networks evolved with NEAT (NeuroEvolution of Augmenting Topologies). Each car has five radar sensors. Cars that crash are removed, the ones that get furthest breed the next generation, and after a few generations they drive the whole track.

Moved here from [amalsam/Self-Driving-Car-Simulation](https://github.com/amalsam/Self-Driving-Car-Simulation).

## Run it

Run from inside this folder, because the track and car images are loaded from `Assets/`.

```bash
cd 2024-03-self-driving-car-neat
pip install -r requirements.txt
python main.py
```

## Things to change

- `Assets/mytrack orginal2.png` is the track. Draw your own on the same background colour to make a new one.
- `config.txt` holds the NEAT settings: population size, mutation rates, and the fitness threshold that ends training.
- Radar angles are in `Car.update()` in `main.py`.
