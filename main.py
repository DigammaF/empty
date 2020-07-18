

import curses, time

from game import MainStateManager, MainMenu


def main(screen):

	main_state_manager = MainStateManager(screen)
	main_state_manager.init()

	screen.clear()

	main_state_manager.push_state(screen, MainMenu)

	print("Dimensions du terminal:")
	print(str(curses.COLS) + "x" + str(curses.LINES))
	print("Dimensions de la fenêtre:")
	print(str(screen.getmaxyx()))

	prev_time = time.time()

	while main_state_manager.get_running_state():

		main_state_manager.handle_events()

		now = time.time()
		dt = now - prev_time
		prev_time = now

		main_state_manager.update(dt)
		main_state_manager.draw()
		main_state_manager.endframe()

	main_state_manager.cleanup()


input("Réglez la taille du terminal puis appuyez sur entrer")
curses.wrapper(main)
