# Tetris Termux

Game Tetris chạy trực tiếp trên Termux Android, hỗ trợ GUI và No-GUI/Terminal.

## Tính năng
- 7 Tetromino chuẩn I, O, T, S, Z, J, L.
- Di chuyển, xoay, Soft Drop, Hard Drop.
- Collision detection, lock piece, xóa hàng.
- Score, Level, Lines, Combo, High Score.
- Tốc độ tăng theo level và Ghost Piece.
- Pause, Restart, Game Over.
- Lưu dữ liệu tại ~/.tetris-termux/.
- GUI tùy chọn bằng pygame-ce.
- Terminal mode không cần X11.
- CLI: --gui, --terminal, --settings.
- GUI lỗi hoặc chưa cài sẽ tự chuyển No-GUI.

## Cài đặt

    pkg update
    pkg install python git
    git clone https://github.com/khahdihdz/tetris-termux.git
    cd tetris-termux
    python tetris.py

## No-GUI
Không cần dependency GUI:

    python tetris.py --terminal

Điều khiển: A/D trái/phải, S xuống, W hoặc mũi tên lên xoay, SPACE Hard Drop, P Pause, R Restart, Q Thoát.

## GUI
Cài pygame-ce khi môi trường Termux hỗ trợ:

    pip install -r requirements.txt
    python tetris.py --gui

Nếu pygame không khả dụng, chương trình tự chuyển sang Terminal mode.

## Menu
Khi chạy không có tham số: 1 GUI, 2 No-GUI, 3 Cài đặt, 4 Thống kê. Chế độ được ghi nhớ trong ~/.tetris-termux/config.json.

## Kiểm thử

    python -m py_compile tetris.py
    python tetris.py --help

## License
MIT © 2026 khahdihdz
