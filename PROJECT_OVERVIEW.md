# RoboBuddy Project Overview

## 🤖 What is RoboBuddy?
RoboBuddy is a touch-friendly task management application designed for the Raspberry Pi 4. It acts as a helpful digital assistant for kids, keeping track of their daily routines and reminders. The interface is specifically built for touchscreens, with large buttons and easy-to-read text.

## ✨ Key Features
*   **Time-Aware Dashboard**: Automatically displays the relevant task list (Morning, Afternoon, or Night) based on the current time of day.
*   **Touch Interface**: Large, colorful buttons and checkboxes make it easy for kids to interact with the screen.
*   **Customizable Tasks**: All tasks are stored in a simple text file (`tasks.json`), allowing parents to easily update the schedule without touching any code.
*   **Interactive Checkboxes**: Kids can mark tasks as "Complete" by tapping the checkbox, which visually dims the task to show progress.

## 📂 Project Structure
Here's a breakdown of the files in this project:

### 1. `main.py` (The Brain)
This is the main Python script that powers the application. It:
*   Loads the task lists from the `tasks.json` file.
*   Checks the current time to decide which list to show first.
*   Handles user interactions (tapping buttons, checking boxes).
*   Uses the **Kivy** framework to create the window and graphics.

### 2. `robobuddy.kv` (The Look)
This file defines the User Interface (UI). It uses the Kivy Language to describe:
*   How big the buttons should be.
*   What colors to use (Blue for Morning/Active, Dark Grey for inactive).
*   The layout of the screen (Header at top, scrollable list in middle, navigation at bottom).
*   Font sizes and spacing to ensure everything is readable on a small screen.

### 3. `tasks.json` (The Data)
This is a simple text file that stores the actual lists. It is organized into three sections:
*   **"Morning"**: e.g., "Brush teeth", "Eat breakfast"
*   **"Afternoon"**: e.g., "Homework", "Clean room"
*   **"Night"**: e.g., "Brush teeth", "Bedtime"

You can edit this file with any text editor to change the tasks!

## 🛠️ Technology Stack
*   **Language**: Python 3
*   **GUI Framework**: Kivy (Open source Python library for rapid development of applications that make use of innovative user interfaces, such as multi-touch apps).
*   **Hardware Target**: Raspberry Pi 4 with Touchscreen (runs on Raspbian OS).

## 🚀 How it Works
When you run `python main.py`:
1.  The app starts and reads `tasks.json`.
2.  It checks the system clock. If it's 8:00 AM, it loads the "Morning" list.
3.  The user sees the list and can tap items to complete them.
4.  The user can manually switch to "Afternoon" or "Night" using the bottom buttons if needed.
