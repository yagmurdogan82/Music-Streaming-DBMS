# Music Streaming Content Management System 🎵

**Course:** CMPE 351 - Database Systems Project  
**Student:** Yağmur Doğan

## 📖 Project Overview
This project is a fully functional **Music Streaming Content Management System** inspired by platforms like Spotify and Apple Music. It allows for the comprehensive management of artists, albums, tracks, users and playlists through a relational database.

The system is built using **Python**, **Streamlit** for the user interface and **SQLite** for database management.

## 🚀 Features
The system supports full **CRUD (Create, Read, Update, Delete)** operations for the following entities:

* **Artists & Social Links:** Manage artist details and their social media accounts.
* **Albums & Tracks:** Organize music releases and assign moods to tracks.
* **User Management:** * **Premium Users:** Managed with renewal dates and payment methods.
    * **Free Users:** Managed with ad frequency and listening limits.
* **Playlists:** Create playlists, add/remove tracks and assign to users.
* **Advanced Queries:** View joined data across Artists, Albums and Tracks.

## 🛠️ Tech Stack
* **Language:** Python
* **Database:** SQLite
* **Interface:** Streamlit

## 📂 Project Structure
* `YağmurDoğan_Codes/` - Contains the Python source code and the SQLite database file.
* `YağmurDoğan_Report.pdf` - Detailed project report including ER diagrams, database schema and normalization steps.

## ▶️ How to Run
1.  Clone the repository.
2.  Install the required library:
    ```bash
    pip install streamlit
    ```
3.  Run the application:
    ```bash
    streamlit run "YağmurDoğan_Codes/YağmurDoğan_Code.py"
    ```
