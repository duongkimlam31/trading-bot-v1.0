@echo off

set PACKAGES=selenium keyboard colorama

for %%p in (%PACKAGES%) do (
    python -c "import %%p" 2>nul && (
        echo %%p already installed
    ) || (
        echo Installing %%p
        pip install %%p
    )
)

echo Starting Trading Bot
python -u trading_bot.py
echo Exiting Bot
pause
