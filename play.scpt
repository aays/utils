#!/usr/bin/osascript

on run argv
        set x to item 1 of argv
        if ((x as string) is equal to "album")
                set y to item 2 of argv
                tell application "iTunes"
                        play (first track of playlist "Library" whose album is y)
                end tell
        else
        tell application "iTunes"
                play track x
        end tell
        end if
end run
