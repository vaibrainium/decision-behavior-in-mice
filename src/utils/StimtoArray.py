def get_RDK(coh, seed, nFrames, pulse_coh=None, pulse_t=None, pulse_dur=None):
    import time
    import tkinter as tk

    import numpy as np

    # Loading pygame dependencies
    import pygame
    import pygame.locals

    from scripts.ucla_rdk import DotMotionStim

    if pulse_dur is None:
        pulse_dur = []
    if pulse_t is None:
        pulse_t = []
    if pulse_coh is None:
        pulse_coh = []
    pygame.init()
    # pygame.mixer.init()
    pygame.time.Clock()

    # clock = pyglet.clock.Clock()
    # clock.set_fps_limit(60)

    # global window_size, screen, rewardTone, incorrectTone
    tk.Tk()
    window_size = (1280, 720)
    flags = pygame.DOUBLEBUF  # Using buffer screen to increase speed
    screen = pygame.display.set_mode(window_size, flags=flags, display=1)  # Projecting on secondary screen      # Changed this line on March 30 2021 to see if flickering stops with no vsync

    Dots = DotMotionStim()
    Dots.vel = 5
    Dots.radius = 14

    screen.fill((0, 0, 0))  # Display Black Screen
    pygame.display.update()
    pygame.event.pump()

    time.time_ns()

    Dots.newStimulus(coh, seed)
    RDK = np.zeros((nFrames, window_size[0], window_size[1]))

    pulse = bool(pulse_coh)

    for i in range(nFrames):
        if pulse and i == pulse_t:
            Dots.updateBurst(pulse_coh)
        if pulse and i == pulse_t + pulse_dur:
            Dots.updateBurst(coh)

        screen.fill((0, 0, 0))
        Dots.moveDots()  # Drawing dots
        for dot in range(Dots.nDots):
            pygame.draw.circle(screen, Dots.color, (int(Dots.x[dot]), int(Dots.y[dot])), Dots.radius)

        # pygame.display.update()
        RDK[i, :, :] = pygame.surfarray.array2d(screen)
        # pygame.event.pump()

    pygame.quit()
    return RDK


# if __name__ == '__main__':
#     get_RDK(coh=0, seed=1, nFrames=360, pulse_coh=-100, pulse_t=100, pulse_dur=100)
