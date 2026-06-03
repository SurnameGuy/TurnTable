#!/usr/bin/env bash
if [ "$EUID" -eq 0 ]; then
    echo
    echo "Never use sudo if not required."
    echo "Never use sudo if not required."
    echo "Never use sudo if not required."
    echo
    echo "[FATAL ERROR] WARNING: NEVER EVER EXECUTE A SCRIPT WITH SUDO IF NOT REQUIRED! PLEASE, DO NOT BREAK YOUR SYSTEM."
    echo "Execute this script again WITHOUT sudo."
    echo
    exit 1
fi

install() {
    if [ -x "$(command -v apt-get)" ]; then
        echo "APT package manager detected. Installing dependencies..."
        sudo apt-get update
        sudo apt-get install -y libmpv-dev libmpv2 python3-pip python3-venv libgl1-mesa-glx
    elif [ -x "$(command -v dnf)" ]; then
        echo "DNF package manager detected. Installing dependencies..."
        sudo dnf install -y mpv-libs python3-pip Mesa-libGL
    else
        echo "Warning: Unknown package manager."
        echo "Make sure to have 'libmpv', 'python3', 'python3-pip', 'python3-venv', 'libmpv-dev' and 'libmpv2'/'mpb-libs', 'libgl1-mesa-glx'/'Mesa-libGL' dependencies installed on your system so the application can work normally."
        sleep 5
    fi
    
    echo "[1] CREATING VIRTUAL PYTHON ENVIRONMENT..."
    echo
    python3 -m venv venv
    source venv/bin/activate

    echo "[2] INSTALLING APPLICATION PYTHON DEPENDENCIES..."
    echo
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install pyinstaller

    echo "[3] BUILDING TURNTABLE WITH PYINSTALLER..."
    pyinstaller --onefile --noconsole --clean --name "TurnTable" --add-data "assets:assets" --add-data "index.html:." appBin.py
    deactivate

    echo "[4] INSTALLING TURNTABLE IN THE SYSTEM..."
    echo
    sudo cp dist/TurnTable /usr/local/bin/turntable
    sudo chmod +x /usr/local/bin/turntable
    sudo cp assets/icon.png /usr/share/pixmaps/TurnTableIcon.png
cat <<EOF > ~/.local/share/applications/TurnTable.desktop
[Desktop Entry]
Name=TurnTable
Exec=/usr/local/bin/turntable %U
Icon=/usr/share/pixmaps/TurnTableIcon.png
Type=Application
Categories=AudioVideo;Audio;Player;
Terminal=false
EOF
    
    echo "[5] CLEANING TEMPORARY COMPILATION FILES..."
    echo
    rm -rf build/ dist/ TurnTable.spec venv/
    echo
    echo "'turntable' installation complete."
    echo
    echo "=========================================="
    echo "     TURNTABLE SUCESSFULLY INSTALLED!"
    echo " Look for it into your menu application."
    echo "=========================================="
    echo
}

uninstall() {
    sudo rm -rf /usr/local/bin/turntable
    sudo rm -rf /usr/share/pixmaps/TurnTableIcon.png
    rm -rf ~/.local/share/applications/TurnTable.desktop
    echo "FINISHED UNINSTALLATION SCRIPT."
}

echo "Select an option bellow and press ENTER:"
echo "1) Build & Install"
echo "2) Uninstall"
echo
read -p "SELECT> " option

case $option in
    1)
        install
        ;;
    2)
        uninstall
        ;;
    *)
        echo "Invalid option, aborted."
        exit 1
        ;;
esac