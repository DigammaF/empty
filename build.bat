pyinstaller --onefile --hidden-import=curses main.spec --distpath .
call pack
call resetconfig