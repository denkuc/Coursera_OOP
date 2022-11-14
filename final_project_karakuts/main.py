import pygame
from game import Game

SCREEN_DIM = (800, 600)

pygame.init()
gameDisplay = pygame.display.set_mode(SCREEN_DIM)
pygame.display.set_caption("MyRPG")
KEYBOARD_CONTROL = True

if not KEYBOARD_CONTROL:
    import numpy as np
    answer = np.zeros(4, dtype=float)


if __name__ == '__main__':
    game = Game()
    engine = game.engine

    while engine.working:
        if KEYBOARD_CONTROL:
            for event in pygame.event.get():
                if engine.game_over:
                    if event.key == pygame.K_RETURN:
                        game = Game(game.size)
                        engine = game.engine
                        engine.game_over = False
                if event.type == pygame.QUIT:
                    engine.working = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h:
                        engine.show_help = not engine.show_help
                    if event.key == pygame.K_KP_PLUS:
                        game.increase_size()
                        game.redraw()
                    if event.key == pygame.K_KP_MINUS:
                        game.decrease_size()
                        game.redraw()
                    if event.key == pygame.K_r:
                        game = Game(game.size)
                        engine = game.engine
                    if event.key == pygame.K_ESCAPE:
                        engine.working = False
                    if engine.game_process:
                        if event.key == pygame.K_UP:
                            engine.move_up()
                            game.iteration += 1
                        elif event.key == pygame.K_DOWN:
                            engine.move_down()
                            game.iteration += 1
                        elif event.key == pygame.K_LEFT:
                            engine.move_left()
                            game.iteration += 1
                        elif event.key == pygame.K_RIGHT:
                            engine.move_right()
                            game.iteration += 1
                    else:
                        if event.key == pygame.K_RETURN:
                            game.redraw()

                gameDisplay.blit(game.drawer, (0, 0))
                game.drawer.draw(gameDisplay)
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    engine.working = False
            if engine.game_process:
                prev_score = engine.score
                move = engine.get_random_action()
                move()
                state = pygame.surfarray.array3d(gameDisplay)
                reward = engine.score - prev_score
            else:
                game = Game(game.size)
                engine = game.engine

            gameDisplay.blit(game.drawer, (0, 0))
            game.drawer.draw(gameDisplay)

        pygame.display.update()

    pygame.display.quit()
    pygame.quit()
    exit(0)
