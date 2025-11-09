import numpy as np


class RandomDotMotion(object):
    def __init__(self, stimulus_size=(1280, 720)):
        self.stimulus_size = stimulus_size
        self.radius = 17
        self.color = (255, 255, 255)
        self.vel = 350
        self.lifetime = 30
        self.nDots = []
        self.fill = 15
        self.x = []
        self.y = []
        self.age = []
        self.theta = []
        self.randTheta = [0, 45, 90, 135, 180, 225, 270, 315, 360]
        self.coherence = None
        self.cohDots = []
        self.noncohDots = []

        self.rdk_generator = np.random.RandomState()  # Creating separate random number generator -> rdk_generator

    def update_lifetime(self, pars):
        self.lifetime = pars["lifetime"]

    def new_stimulus(self, pars):
        if "seed" in pars:
            self.rdk_generator.seed(pars["seed"])
        self.coherence = pars["coherence"]
        # self.stimulus_size = pars["stimulus_size"]

        self.radius = pars.get("dot_radius", self.radius)
        self.color = pars.get("dot_color", self.color)
        self.fill = pars.get("dot_fill", self.fill)
        self.vel = pars.get("dot_vel", self.vel)
        self.lifetime = pars.get("dot_lifetime", self.lifetime)

        self.nDots = round((self.fill / 100) * self.stimulus_size[0] * self.stimulus_size[1] / (np.pi * self.radius**2))
        self.x = self.rdk_generator.randint(self.stimulus_size[0], size=self.nDots)
        self.y = self.rdk_generator.randint(self.stimulus_size[1], size=self.nDots)
        self.age = self.rdk_generator.randint(self.lifetime, size=self.nDots)
        self.theta = self.rdk_generator.randint(360, size=self.nDots)  # Non coherent dots in all direction of 360 degrees
        # self.theta = self.rdk_generator.choice(self.randTheta, size=self.nDots)  # Non coherent dots in one of 8 direction separated by 45 degrees
        self.cohDots = np.array(range(round(np.abs(self.coherence) * self.nDots / 100)))
        if not self.cohDots.size:
            self.noncohDots = np.array(range(self.nDots))  # If cohDots are empty all dots are non-coherent
        else:
            self.noncohDots = np.array(range(self.cohDots[-1] + 1, self.nDots))
            self.theta[self.cohDots] = np.sign(pars["coherence"]) * 90

    def move_dots(self, frame_rate=60, new_coherence=None):
        self.x[self.age == self.lifetime] = self.rdk_generator.randint(self.stimulus_size[0], size=np.count_nonzero(self.age == self.lifetime))
        self.y[self.age == self.lifetime] = self.rdk_generator.randint(self.stimulus_size[1], size=np.count_nonzero(self.age == self.lifetime))
        self.age[self.age == self.lifetime] = 0
        # If update is required
        if new_coherence is not None:
            self.update_coherence(new_coherence)
        # Moving dots one step a time
        self.x = self.x + int(self.vel / frame_rate) * np.sin(np.deg2rad(self.theta))
        self.y = self.y + int(self.vel / frame_rate) * np.cos(np.deg2rad(self.theta))
        self.age += 1
        # Accounting for boundaries
        self.x[self.x >= self.stimulus_size[0]] = 0
        self.x[self.x < 0] = self.stimulus_size[0]
        self.y[self.y >= self.stimulus_size[1]] = 0
        self.y[self.y < 0] = self.stimulus_size[1]

    def update_coherence(self, new_coherence):
        # Congruent burst - high coherence
        if (np.sign(new_coherence) == np.sign(self.coherence)) & (np.abs(new_coherence) > np.abs(self.coherence)):
            Nchangedots = (self.nDots * np.abs(new_coherence - self.coherence) // 100).astype(int)
            changeDots = self.noncohDots[:Nchangedots]
            self.theta[changeDots] = np.sign(new_coherence) * 90
            self.coherence = new_coherence
            self.cohDots = np.union1d(self.cohDots, changeDots).astype(int)
            self.noncohDots = np.setdiff1d(self.noncohDots, changeDots).astype(int)

        # Congruent burst - low coherence
        if (np.sign(new_coherence) == np.sign(self.coherence)) & (np.abs(new_coherence) < np.abs(self.coherence)):
            Nchangedots = (self.nDots * np.abs(new_coherence - self.coherence) // 100).astype(int)
            changeDots = self.cohDots[:Nchangedots]
            self.theta[changeDots] = self.rdk_generator.randint(360, size=Nchangedots)
            self.coherence = new_coherence
            self.cohDots = np.setdiff1d(self.cohDots, changeDots).astype(int)
            self.noncohDots = np.union1d(self.noncohDots, changeDots).astype(int)

        # incongruent burst - high coherence
        if (np.sign(new_coherence) != np.sign(self.coherence)) & (np.abs(new_coherence) > np.abs(self.coherence)):
            Nchangedots = (self.nDots * np.abs(new_coherence) // 100).astype(int)
            changeDots = np.concatenate((self.cohDots, self.noncohDots[: (Nchangedots - len(self.cohDots))])).astype(int)
            self.theta[changeDots] = np.sign(new_coherence) * 90
            self.coherence = new_coherence
            self.noncohDots = np.setdiff1d(self.noncohDots, changeDots).astype(int)
            self.cohDots = np.union1d(self.cohDots, changeDots).astype(int)

        # Incongruent burst - low coherence
        if (np.sign(new_coherence) != np.sign(self.coherence)) & (np.abs(new_coherence) <= np.abs(self.coherence)):
            Nchangedots = (self.nDots * np.abs(new_coherence) // 100).astype(int)
            Nchangedots = min(Nchangedots, len(self.cohDots))
            changeDots = self.cohDots[:Nchangedots]
            self.theta[changeDots] = np.sign(new_coherence) * 90
            self.theta[np.setdiff1d(self.cohDots, changeDots)] = self.rdk_generator.randint(360, size=len(self.cohDots) - Nchangedots)
            self.coherence = new_coherence
            self.noncohDots = np.concatenate([self.noncohDots, np.setdiff1d(self.cohDots, changeDots)]).astype(int)
            self.cohDots = changeDots.astype(int)
